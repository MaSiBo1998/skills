#!/usr/bin/env python3
"""Create per-endpoint KB contracts inferred from project usage."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


IGNORED_DIRS = {"node_modules", "dist", "build", ".git"}
TERMINAL_TYPES = {
    "any",
    "bigint",
    "boolean",
    "false",
    "null",
    "number",
    "object",
    "string",
    "symbol",
    "true",
    "undefined",
    "unknown",
    "void",
    "never",
}
TERMINAL_GENERIC_PREFIXES = (
    "Record<",
    "Partial<",
    "Required<",
    "Readonly<",
    "Pick<",
    "Omit<",
    "Extract<",
    "Exclude<",
)


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clean(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def short_file(path_value: str) -> str:
    return path_value.replace("\\", "/").split("/")[-1]


def find_matching_brace(text: str, start: int) -> int:
    depth = 0
    in_string = ""
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = ""
            continue
        if char in {"'", '"', "`"}:
            in_string = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def parse_exported_types(root: Path) -> dict[str, dict[str, Any]]:
    type_map: dict[str, dict[str, Any]] = {
        "EmptyRequest": {"kind": "alias", "target": "Record<string, never>", "fields": []},
        "unknown": {"kind": "alias", "target": "unknown", "fields": []},
    }
    files = list((root / "src").glob("**/*.ts"))
    for path in files:
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        text = read_text(path)
        for match in re.finditer(r"export\s+interface\s+(\w+)(?:\s+extends\s+(\w+))?\s*{", text):
            name = match.group(1)
            parent = match.group(2) or ""
            end = find_matching_brace(text, match.end() - 1)
            if end == -1:
                continue
            body = text[match.end() : end]
            type_map[name] = {
                "kind": "interface",
                "parent": parent,
                "fields": parse_interface_fields(body),
                "source_file": str(path),
            }
        for match in re.finditer(r"export\s+type\s+(\w+)\s*=\s*([^;\n]+);", text):
            type_map[match.group(1)] = {
                "kind": "alias",
                "target": match.group(2).strip(),
                "fields": [],
                "source_file": str(path),
            }
    return type_map


def parse_interface_fields(body: str) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    pending_comment = ""
    lines = body.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("/**"):
            comment_parts = []
            while index < len(lines):
                part = lines[index].strip()
                comment_parts.append(part)
                if "*/" in part:
                    break
                index += 1
            pending_comment = clean_comment("\n".join(comment_parts))
            index += 1
            continue
        match = re.match(r"([A-Za-z_$][\w$]*)\??\s*:\s*([^;/]+)(?:[;,])?\s*(?://\s*(.*))?$", line)
        if match:
            fields.append(
                {
                    "field": match.group(1),
                    "type": match.group(2).strip(),
                    "required": "?" not in line.split(":", 1)[0],
                    "description": clean(match.group(3) or pending_comment),
                    "enum": [],
                    "enumDesc": "",
                }
            )
            pending_comment = ""
        index += 1
    return fields


def clean_comment(comment: str) -> str:
    lines = []
    for line in comment.splitlines():
        line = re.sub(r"^/\*\*|\*/$", "", line.strip()).strip()
        line = re.sub(r"^\*\s?", "", line).strip()
        if line:
            lines.append(line)
    return " ".join(lines)


def normalize_type(type_name: str) -> str:
    value = clean(type_name)
    value = re.sub(r"\s+", " ", value)
    return value


def strip_array(type_name: str) -> tuple[str, bool]:
    value = normalize_type(type_name)
    if value.endswith("[]"):
        return value[:-2], True
    array_match = re.match(r"Array<(.+)>", value)
    if array_match:
        return array_match.group(1).strip(), True
    return value, False


def is_terminal_type(type_name: str) -> bool:
    value = normalize_type(type_name)
    if not value:
        return True
    if value in TERMINAL_TYPES:
        return True
    if value.startswith("{") or value.startswith("("):
        return True
    if value.startswith("keyof ") or value.startswith("typeof "):
        return True
    if any(value.startswith(prefix) for prefix in TERMINAL_GENERIC_PREFIXES):
        return True
    if re.fullmatch(r"['\"].*['\"]|\d+(?:\.\d+)?", value):
        return True
    return False


def terminal_field(prefix: str, type_name: str, description: str = "") -> list[dict[str, Any]]:
    if not prefix:
        return []
    return [
        {
            "field": prefix,
            "type": normalize_type(type_name) or "unknown",
            "required": True,
            "description": description,
            "enum": [],
            "enumDesc": "",
        }
    ]


def flatten_type(type_name: str, type_map: dict[str, dict[str, Any]], prefix: str = "", seen: set[str] | None = None) -> list[dict[str, Any]]:
    seen = seen or set()
    type_name = normalize_type(type_name)
    if is_terminal_type(type_name):
        return []
    base, is_array = strip_array(type_name)
    array_prefix = f"{prefix}[]" if is_array and prefix else prefix
    if is_array:
        fields = [
            {
                "field": array_prefix or "[]",
                "type": f"array<{base}>",
                "required": bool(prefix),
                "description": "",
                "enum": [],
                "enumDesc": "",
            }
        ]
        if base in seen or is_terminal_type(base):
            return fields if prefix else []
        fields.extend(flatten_type(base, type_map, array_prefix or "[]", seen))
        return fields

    if base in seen:
        return terminal_field(prefix, base, "递归类型引用，保留为终止字段")

    if "|" in base and not base.startswith("{"):
        return [
            {
                "field": prefix or "value",
                "type": base,
                "required": bool(prefix),
                "description": "",
                "enum": [],
                "enumDesc": "",
            }
        ]

    item = type_map.get(base)
    if not item:
        return terminal_field(prefix, base)

    if item["kind"] == "alias":
        target = normalize_type(item.get("target", ""))
        if not target or target == base or base in seen:
            return terminal_field(prefix, target or base, "递归类型别名，保留为终止字段")
        if target in {"Record<string, never>", "{}"}:
            return []
        if is_terminal_type(target):
            return [
                {
                    "field": prefix or "body",
                    "type": target,
                    "required": False,
                    "description": "项目代码约束为通用或终止类型，需补项目接口文档确认字段",
                    "enum": [],
                    "enumDesc": "",
                }
            ] if prefix or target.startswith("Record<") else []
        return flatten_type(target, type_map, prefix, seen | {base})

    fields: list[dict[str, Any]] = []
    parent = item.get("parent")
    if parent:
        fields.extend(flatten_type(parent, type_map, prefix, seen | {base}))
    for field in item.get("fields", []):
        field_path = f"{prefix}.{field['field']}" if prefix else field["field"]
        field_type = normalize_type(field.get("type", "unknown"))
        output = {
            **field,
            "field": field_path,
            "type": field_type,
        }
        fields.append(output)
        child_base, child_is_array = strip_array(field_type)
        if child_base in type_map and child_base not in seen:
            fields.extend(flatten_type(field_type, type_map, field_path, seen | {base}))
        elif child_is_array:
            fields.append(
                {
                    "field": f"{field_path}[]",
                    "type": field_type,
                    "required": field.get("required", False),
                    "description": field.get("description", ""),
                    "enum": [],
                    "enumDesc": "",
                }
            )
    return fields


def extract_service_context(root: Path) -> dict[str, dict[str, Any]]:
    context: dict[str, dict[str, Any]] = {}
    files = list((root / "src").glob("**/*.ts")) + list((root / "src").glob("**/*.tsx"))
    for path in files:
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        text = read_text(path)
        for match in re.finditer(r"API\.([A-Za-z_$][\w$]*)", text):
            symbol = match.group(1)
            block = surrounding_export_block(text, match.start())
            body_fields = parse_body_literal(block)
            request_type = infer_request_type(block)
            response_type = infer_response_type(block)
            context.setdefault(symbol, {})
            context[symbol].update(
                {
                    "block": block,
                    "body_fields": body_fields,
                    "request_type": request_type,
                    "response_type": response_type,
                    "service_file": str(path),
                    "service_name": infer_export_name(block),
                    "description": infer_description(block),
                }
            )
    return context


def surrounding_export_block(text: str, position: int) -> str:
    starts = [m.start() for m in re.finditer(r"export\s+(?:async\s+function|const\s+|function\s+)", text) if m.start() <= position]
    if not starts:
        start = max(0, text.rfind("\n", 0, position - 1))
    else:
        start = starts[-1]
        comment_start = text.rfind("/**", 0, start)
        comment_end = text.rfind("*/", 0, start)
        if comment_start != -1 and comment_end != -1 and comment_end > comment_start and start - comment_end < 8:
            start = comment_start
    next_match = re.search(r"\n(?:/\*\*[\s\S]*?\*/\s*)?export\s+(?:async\s+function|const\s+|function\s+)", text[position:])
    end = position + next_match.start() if next_match else len(text)
    return text[start:end]


def infer_export_name(block: str) -> str:
    match = re.search(r"export\s+async\s+function\s+(\w+)", block) or re.search(r"export\s+function\s+(\w+)", block) or re.search(r"export\s+const\s+(\w+)", block)
    return match.group(1) if match else ""


def infer_description(block: str) -> str:
    comment_match = re.search(r"/\*\*([\s\S]*?)\*/", block)
    if comment_match:
        lines = [line for line in clean_comment(comment_match.group(0)).split(" ") if not line.startswith("@")]
        text = " ".join(lines)
        text = re.sub(r"POST\s+/[^\s]+\s*", "", text).strip()
        return text
    line_comment = re.search(r"//\s*([^\n]+)\n\s*export", block)
    return clean(line_comment.group(1)) if line_comment else ""


def infer_request_type(block: str) -> str:
    function_match = re.search(r"\(([^)]*)\)\s*:\s*Promise", block)
    if function_match:
        params = function_match.group(1)
        data_match = re.search(r"(?:data|_data|p)\s*:\s*([A-Za-z_$][\w$]*)", params)
        if data_match:
            return data_match.group(1)
    const_match = re.search(r"=\s*(?:<[^>]+>\s*)?(?:async\s*)?\(([^)]*)\)", block)
    if const_match:
        params = const_match.group(1)
        data_match = re.search(r"(?:data|_data|p)\s*:\s*([A-Za-z_$][\w$]*)", params)
        if data_match:
            return data_match.group(1)
    return ""


def first_generic_argument(block: str, callee_pattern: str) -> str:
    match = re.search(callee_pattern + r"\s*<", block)
    if not match:
        return ""
    start = block.find("<", match.end() - 1)
    depth = 0
    in_string = ""
    escaped = False
    for index in range(start, len(block)):
        char = block[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = ""
            continue
        if char in {"'", '"', "`"}:
            in_string = char
            continue
        if char == "<":
            depth += 1
        elif char == ">":
            depth -= 1
            if depth == 0:
                return block[start + 1 : index].strip()
    return ""


def infer_response_type(block: str) -> str:
    promise_type = first_generic_argument(block, r"Promise")
    if promise_type:
        return promise_type
    request_type = first_generic_argument(block, r"(?:request|http\.post)")
    if request_type:
        return request_type
    return "unknown"


def parse_body_literal(block: str) -> list[dict[str, Any]]:
    body_match = re.search(r"body\s*:\s*{", block)
    if not body_match:
        body_match = re.search(r"\b(?:const|let)\s+body\s*=\s*{", block)
    if not body_match:
        return []
    start = block.find("{", body_match.start())
    end = find_matching_brace(block, start)
    if end == -1:
        return []
    body = block[start + 1 : end]
    fields: list[dict[str, Any]] = []
    depth = 0
    for raw_line in body.splitlines():
        line = raw_line.strip()
        match = re.match(r"([A-Za-z_$][\w$]*)\s*:\s*([^,]+),?\s*(?://\s*(.*))?$", line) if depth == 0 else None
        if match and not line.startswith("..."):
            fields.append(
                {
                    "field": match.group(1),
                    "type": "unknown",
                    "required": True,
                    "description": clean(match.group(3)),
                    "enum": [],
                    "enumDesc": "",
                }
            )
        depth += line.count("{") - line.count("}")
        depth = max(depth, 0)
    return fields


def endpoint_slug(method: str, path_value: str, source_type: str) -> str:
    raw = f"{method}-{path_value}"
    slug = re.sub(r"[^A-Za-z0-9]+", "-", raw).strip("-").lower()
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}"


def field_row(field: dict[str, Any]) -> str:
    enum_value = field.get("enum", [])
    enum_text = ", ".join(str(item) for item in enum_value) if isinstance(enum_value, list) else clean(enum_value)
    def cell(value: Any) -> str:
        return clean(value).replace("|", "\\|").replace("\n", "<br>")

    return "| `{field}` | {type} | {required} | {desc} | {enum_text} | {enum_desc} |".format(
        field=cell(field.get("field", "")),
        type=cell(field.get("type", "unknown")),
        required="yes" if field.get("required") else "no",
        desc=cell(field.get("description", "")),
        enum_text=cell(enum_text),
        enum_desc=cell(field.get("enumDesc", "")),
    )


def write_contract_files(contract: dict[str, Any], out_dir: Path) -> tuple[str, str]:
    slug = endpoint_slug(contract["method"], contract["path"], contract["source_type"])
    json_name = f"{slug}.json"
    md_name = f"{slug}.md"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / json_name).write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / md_name).write_text(contract_markdown(contract), encoding="utf-8")
    return json_name, md_name


def clean_title(value: Any, fallback: str) -> str:
    text = clean(value)
    if not text:
        return fallback
    replacements = {
        "首复贷风控埋点接口": "首复贷风控埋点",
        "还款银行列表接口": "还款银行列表",
        "还款支付接口": "还款支付",
    }
    for key, title in replacements.items():
        if key in text:
            return title
    text = re.sub(r"^TODO[:：]\s*", "", text)
    text = re.sub(r"swaggerApi\.json\s*当前未提供该接口定义[，,]?", "", text)
    text = re.sub(r"当前\s*swaggerApi\.json\s*未提供[^。；;]*[。；;]?", "", text)
    text = re.sub(r"因此入参按空对象约束[。；;]?", "", text)
    text = re.sub(r"先按通用对象约束[。；;]?", "", text)
    text = re.sub(r"先按同结构缓存[。；;]?", "", text)
    text = re.sub(r"暂保留参考项目路径.*$", "", text).strip(" ，,。")
    return text or fallback


def contract_markdown(contract: dict[str, Any]) -> str:
    contract_status = "正式接口文档" if contract.get("source_type") == "swagger" else "项目提取，待正式文档确认"
    lines = [
        "---",
        f"title: {contract['method']} {contract['path']}",
        "type: api-contract",
        "status: active",
        "tags:",
        "  - api",
        "  - api-contract",
        f"appName: {contract.get('appName', '')}",
        f"path: {contract.get('path', '')}",
        f"method: {contract.get('method', '')}",
        f"source_type: {contract.get('source_type', '')}",
        f"api_symbol: {contract.get('symbol', '')}",
        "---",
        "",
        f"# {contract['method']} {contract['path']}",
        "",
        f"- appName：`{contract.get('appName', '')}`",
        f"- API symbol：`{contract.get('symbol', '')}`",
        f"- 模块：{contract.get('module', '')}",
        f"- 用途：{contract.get('title', '')}",
        f"- 文档状态：{contract_status}",
        "",
    ]
    if contract.get("source_type") == "project-extracted":
        lines.extend(
            [
                "> 该接口目前来自项目用法提取，已沉淀可确定的入参/出参结构；后续拿到正式接口文档时需要校准。",
                "",
            ]
        )
    lines.extend(
        [
            "## Request Fields",
            "",
            "| Field | Type | Required | Description | Enum | Enum Desc |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    request = contract.get("request_fields", [])
    lines.extend(field_row(field) for field in request) if request else lines.append("|  |  |  | 无请求字段或待接口文档确认 |  |  |")
    lines.extend(
        [
            "",
            "## Response Fields",
            "",
            "| Field | Type | Required | Description | Enum | Enum Desc |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    response = contract.get("response_fields", [])
    lines.extend(field_row(field) for field in response) if response else lines.append("|  |  |  | 响应结构待项目接口文档确认 |  |  |")
    return "\n".join(lines) + "\n"


def merge_contracts(
    manifest: list[dict[str, Any]],
    existing_index: list[dict[str, Any]],
    root: Path,
    app_name: str,
    out_dir: Path,
) -> list[dict[str, Any]]:
    type_map = parse_exported_types(root)
    service_context = extract_service_context(root)
    existing_by_path = {item.get("path"): item for item in existing_index}
    rows: list[dict[str, Any]] = []

    for row in existing_index:
        row = {**row}
        row.setdefault("source_type", "swagger")
        row.setdefault("symbols", [])
        rows.append(row)

    for record in manifest:
        path_value = record.get("path", "")
        if path_value in existing_by_path:
            continue
        symbol = record.get("symbol", "")
        context = service_context.get(symbol, {})
        request_fields = context.get("body_fields") or flatten_type(context.get("request_type", ""), type_map)
        response_fields = flatten_type(context.get("response_type", "unknown"), type_map)
        contract = {
            "appName": app_name,
            "module": module_for(record),
            "title": clean_title(context.get("description") or record.get("semantic_hint"), symbol),
            "path": path_value,
            "method": "POST" if record.get("method", "unknown") == "unknown" else str(record.get("method")).upper(),
            "symbol": symbol,
            "source_type": "project-extracted",
            "request_type": context.get("request_type", ""),
            "response_type": context.get("response_type", ""),
            "request_fields": request_fields,
            "response_fields": response_fields,
        }
        json_name, md_name = write_contract_files(contract, out_dir)
        rows.append(
            {
                "appName": app_name,
                "module": contract["module"],
                "title": contract["title"],
                "path": path_value,
                "method": contract["method"],
                "json_file": json_name,
                "markdown_file": md_name,
                "request_field_count": len(request_fields),
                "response_field_count": len(response_fields),
                "source_type": "project-extracted",
                "symbol": symbol,
            }
        )
    return sorted(rows, key=lambda item: (item.get("module", ""), item.get("path", "")))


def first_file(record: dict[str, Any]) -> str:
    files = record.get("files", [])
    return str(files[-1]) if files else ""


def module_for(record: dict[str, Any]) -> str:
    file_names = [short_file(str(file_path)) for file_path in record.get("files", [])]
    if "home.ts" in file_names:
        return "首复贷/首页"
    if "product.ts" in file_names:
        return "产品/订单详情"
    if "order.ts" in file_names:
        return "订单/还款"
    if "banner.ts" in file_names:
        return "Banner"
    if "user.ts" in file_names:
        return "用户/首页"
    if "apply.ts" in file_names:
        return "进件"
    if "monitor.ts" in file_names:
        return "飞书告警"
    if "feedback.ts" in file_names:
        return "客服反馈"
    return clean(record.get("semantic_hint")) or "未归类"


def write_index(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--existing-index", required=True, type=Path)
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    rows = merge_contracts(
        read_jsonl(args.manifest),
        read_jsonl(args.existing_index),
        args.project_root,
        args.app_name,
        args.out_dir,
    )
    write_index(rows, args.out_dir / "index.jsonl")
    print(
        json.dumps(
            {
                "appName": args.app_name,
                "endpoint_contracts": len(rows),
                "swagger": len([row for row in rows if row.get("source_type", "swagger") == "swagger"]),
                "project_extracted": len([row for row in rows if row.get("source_type") == "project-extracted"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
