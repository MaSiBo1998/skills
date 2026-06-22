#!/usr/bin/env python3
"""Archive project API contracts into personal-ai-kb/Work/API/apps/<appName>."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path
from typing import Any


IGNORED_DIRS = {"node_modules", "dist", "build", ".git", ".dart_tool"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}
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

PURPOSE_BY_SYMBOL = {
    "getHomeData": "首页信息",
    "getHomeInfo": "首页信息",
    "toUniversalPoint": "首复贷风控埋点",
    "getProductDetail": "产品订单详情",
    "getRepaymentBankList": "还款银行列表",
    "toSubmitOrder": "提交申贷",
    "toPayMoney": "还款支付",
    "bannerVagary": "首复贷 Banner 配置",
    "getUserDetail": "用户详情与步骤完成状态",
    "getStepConfig": "步骤配置",
    "getCommonConfig": "通用配置",
    "saveWorkInfo": "保存工作信息",
    "saveContactInfo": "保存联系人信息",
    "savePersonalInfo": "保存个人信息",
    "validOcr": "身份证 OCR 识别",
    "idcardOcr": "身份证 OCR 识别",
    "saveUserIdInfo": "保存身份信息",
    "saveIdInfo": "保存身份信息",
    "saveUpdateUserIdInfo": "修改身份信息",
    "saveRejectIdInfo": "被拒后保存身份信息",
    "saveUserSelfInfo": "保存人脸信息",
    "saveFaceInfo": "保存人脸信息",
    "saveUpdateUserSelfInfo": "修改人脸信息",
    "saveRejectFaceInfo": "被拒后保存人脸信息",
    "validHeadByPerson": "个人中心人脸校验",
    "validHeadByHome": "首页人脸校验",
    "validChangeBankSelfHead": "换卡人脸校验",
    "getBankList": "银行列表",
    "saveUserBankInfo": "保存银行卡信息",
    "saveBankInfo": "保存银行卡信息",
    "saveChangeBankInfo": "修改银行卡信息",
    "updateBankInfo": "修改银行卡信息",
    "switchPayoutBank": "切换打款银行卡",
    "removeBankInfo": "移除银行卡",
    "getBankInfo": "查询银行卡信息",
    "getBankCardInfo": "查询银行卡回填信息",
    "submitNewOrder": "提交申贷",
    "submitOrder": "提交申贷",
    "getUserInfo": "用户信息",
    "pushCommonStatistic": "通用埋点上报",
    "incomingStepToDot": "进件步骤埋点",
    "sendEmailCode": "邮箱验证码",
    "sendFeishuAlert": "飞书前端监控告警",
    "getProblemTypes": "客服问题分类",
    "submitComplaint": "提交投诉建议",
}

MODULE_BY_FILE = {
    "home.ts": "首复贷/首页",
    "product.ts": "产品/订单详情",
    "order.ts": "订单/还款",
    "banner.ts": "Banner",
    "user.ts": "用户/首页",
    "apply.ts": "进件",
    "monitor.ts": "飞书告警",
    "feedback.ts": "客服反馈",
    "steps.js": "进件步骤",
    "data.js": "用户/订单",
    "dot.js": "埋点",
}

HEADER_SEMANTICS = {
    "a0835d": ("businessLine", "业务线", "import.meta.env.VITE_APP_BUSINESS_LINE"),
    "v7028c": ("appName", "App 名称", "import.meta.env.VITE_APP_NAME"),
    "y0566y": ("appVersion", "版本号", "Native device.appVersion，缺省 1.0.0"),
    "x0665g": ("platformType", "平台类型", "固定值 1"),
    "r1408o": ("afid", "AF ID", "当前项目为空字符串"),
    "t0849o": ("gaid", "Google Advertising ID", "Native appInfo.gaid"),
    "h8306j": ("drmid", "DRM ID", "Native device.smds.tarlatan"),
    "u7495s": ("adid", "广告 ID", "当前项目为空字符串"),
    "p1063k": ("ip", "IP 地址", "Native device.yapese.returned"),
    "b8637r": ("token", "登录 token", "本地缓存 token，withAuth=true 时发送"),
    "f1378d": ("loginId", "登录用户 ID", "本地缓存 loginId，withAuth=true 时发送"),
}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def clean(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def clean_inline(value: Any) -> str:
    return clean(value).replace("\n", " ").replace("|", "\\|")


def iter_source_files(root: Path) -> list[Path]:
    src = root / "src"
    if not src.exists():
        return []
    files: list[Path] = []
    for pattern in ("**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"):
        for path in src.glob(pattern):
            if path.is_file() and not any(part in IGNORED_DIRS for part in path.parts):
                files.append(path)
    return sorted(set(files))


def short_file(path_value: str) -> str:
    return path_value.replace("\\", "/").split("/")[-1]


def relative_to_project(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def parse_env_files(root: Path) -> dict[str, dict[str, str]]:
    envs: dict[str, dict[str, str]] = {}
    for name in (".env", ".env.development", ".env.production"):
        path = root / name
        if not path.exists():
            continue
        values: dict[str, str] = {}
        for line in read_text(path).splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
        envs[name] = values
    return envs


def parse_env_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def git_output(root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout.strip()
    except Exception:
        return ""


def current_git_branch(root: Path) -> str:
    return git_output(root, ["branch", "--show-current"]) or "unknown"


def git_show_env(root: Path, branch: str, file_name: str) -> dict[str, str]:
    text = git_output(root, ["show", f"{branch}:{file_name}"])
    return parse_env_text(text) if text else {}


def collect_backend_api_envs(root: Path, envs: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    current_branch = current_git_branch(root)
    test_urls = []
    for file_name in (".env", ".env.development", ".env.production"):
        url = envs.get(file_name, {}).get("VITE_API_BASE_URL", "")
        if url and url not in test_urls:
            test_urls.append(url)

    formal_rows: list[dict[str, str]] = []
    seen_formal_urls = set()
    for branch in ("master", "master-co", "master-ng", "origin/master", "origin/master-co", "origin/master-ng"):
        file_name = ".env.production"
        values = git_show_env(root, branch, file_name)
        url = values.get("VITE_API_BASE_URL", "")
        if not url or url in seen_formal_urls:
            continue
        seen_formal_urls.add(url)
        formal_rows.append({"env": "正式", "url": url, "source": f"{branch}:{file_name}"})

    rows = []
    if test_urls:
        rows.append(
            {
                "env": "测试",
                "url": " / ".join(test_urls),
                "source": f"当前分支 {current_branch} 的 .env/.env.development/.env.production；测试分支里的 production 也按测试地址处理",
            }
        )
    rows.extend(formal_rows)
    return rows


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


def clean_comment(comment: str) -> str:
    lines = []
    for line in comment.splitlines():
        line = re.sub(r"^/\*\*|\*/$", "", line.strip()).strip()
        line = re.sub(r"^\*\s?", "", line).strip()
        if line and not line.startswith("@"):
            lines.append(line)
    return " ".join(lines)


def collect_string_constants(text: str) -> dict[str, str]:
    constants: dict[str, str] = {}
    for match in re.finditer(r"(?:export\s+)?const\s+([A-Z][A-Z0-9_]*)\s*=\s*['\"]([^'\"]+)['\"]", text):
        constants[match.group(1)] = match.group(2)
    return constants


def extract_request_url(block: str, constants: dict[str, str]) -> str:
    direct = re.search(r"\burl\s*:\s*['\"]([^'\"]+)['\"]", block)
    if direct:
        return direct.group(1)
    expr_match = re.search(r"\burl\s*:\s*([^\n,}]+)", block)
    if not expr_match:
        return ""
    for name in re.findall(r"\b[A-Z][A-Z0-9_]+\b", expr_match.group(1)):
        if name in constants:
            return constants[name]
    return ""


def collect_direct_request_records(root: Path, records: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    export_re = re.compile(
        r"export\s+const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*(?:request2?|http\.post)\s*\(\s*{",
        re.S,
    )
    for path in iter_source_files(root):
        text = read_text(path)
        constants = collect_string_constants(text)
        for match in export_re.finditer(text):
            symbol = match.group(1)
            block = surrounding_export_block(text, match.start())
            path_value = extract_request_url(block, constants)
            if not path_value:
                continue
            record = records.setdefault(
                symbol,
                {
                    "symbol": symbol,
                    "path": "",
                    "method": "POST",
                    "semantic_hint": "",
                    "module_hint": "",
                    "files": [],
                },
            )
            record["path"] = record.get("path") or path_value
            record["method"] = infer_method(block)
            rel = relative_to_project(path, root)
            if rel not in record["files"]:
                record["files"].append(rel)
    return records


def parse_api_config(root: Path) -> dict[str, dict[str, Any]]:
    config = root / "src" / "services" / "api" / "config.ts"
    records: dict[str, dict[str, Any]] = {}
    if not config.exists():
        return collect_direct_request_records(root, records)
    section = ""
    previous_comment = ""
    api_re = re.compile(r"^\s*([A-Za-z_$][\w$]*)\s*:\s*['\"]([^'\"]+)['\"]")
    for line in read_text(config).splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            comment = stripped.lstrip("/").strip()
            if comment.strip("= "):
                if "====" in comment:
                    section = comment.strip("= ").strip()
                else:
                    previous_comment = comment
            continue
        match = api_re.match(line)
        if match:
            symbol, path_value = match.groups()
            records[symbol] = {
                "symbol": symbol,
                "path": path_value,
                "method": "POST",
                "semantic_hint": previous_comment,
                "module_hint": section,
                "files": [relative_to_project(config, root)],
            }
            previous_comment = ""
    return collect_direct_request_records(root, records)


def collect_api_usage(root: Path, records: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    usage_re = re.compile(r"\bAPI\.([A-Za-z_$][\w$]*)\b")
    for path in iter_source_files(root):
        text = read_text(path)
        for symbol in sorted(set(usage_re.findall(text))):
            record = records.setdefault(
                symbol,
                {
                    "symbol": symbol,
                    "path": "",
                    "method": "POST",
                    "semantic_hint": "",
                    "module_hint": "",
                    "files": [],
                },
            )
            rel = relative_to_project(path, root)
            if rel not in record["files"]:
                record["files"].append(rel)
    return records


def parse_exported_types(root: Path) -> dict[str, dict[str, Any]]:
    type_map: dict[str, dict[str, Any]] = {
        "EmptyRequest": {"kind": "alias", "target": "Record<string, never>", "fields": []},
        "unknown": {"kind": "alias", "target": "unknown", "fields": []},
    }
    for path in iter_source_files(root):
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
                "source_file": relative_to_project(path, root),
            }
        for match in re.finditer(r"export\s+type\s+(\w+)\s*=\s*([^;\n]+);", text):
            type_map[match.group(1)] = {
                "kind": "alias",
                "target": match.group(2).strip(),
                "fields": [],
                "source_file": relative_to_project(path, root),
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


def normalize_type(type_name: str) -> str:
    return re.sub(r"\s+", " ", clean(type_name))


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
    if not value or value in TERMINAL_TYPES:
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
                    "description": "项目代码约束为通用或终止类型，需正式接口文档校准字段",
                    "enum": [],
                    "enumDesc": "",
                }
            ]
        return flatten_type(target, type_map, prefix, seen | {base})
    fields: list[dict[str, Any]] = []
    parent = item.get("parent")
    if parent:
        fields.extend(flatten_type(parent, type_map, prefix, seen | {base}))
    for field in item.get("fields", []):
        field_path = f"{prefix}.{field['field']}" if prefix else field["field"]
        field_type = normalize_type(field.get("type", "unknown"))
        output = {**field, "field": field_path, "type": field_type}
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


def surrounding_export_block(text: str, position: int) -> str:
    starts = [m.start() for m in re.finditer(r"export\s+(?:async\s+function|function\s+|const\s+)", text) if m.start() <= position]
    start = starts[-1] if starts else max(0, text.rfind("\n", 0, position - 1))
    comment_start = text.rfind("/**", 0, start)
    comment_end = text.rfind("*/", 0, start)
    if comment_start != -1 and comment_end != -1 and comment_end > comment_start and start - comment_end < 12:
        start = comment_start
    next_match = re.search(r"\n(?:/\*\*[\s\S]*?\*/\s*)?export\s+(?:async\s+function|function\s+|const\s+)", text[position:])
    end = position + next_match.start() if next_match else len(text)
    return text[start:end]


def infer_export_name(block: str) -> str:
    match = re.search(r"export\s+async\s+function\s+(\w+)", block) or re.search(r"export\s+function\s+(\w+)", block) or re.search(r"export\s+const\s+(\w+)", block)
    return match.group(1) if match else ""


def infer_description(block: str) -> str:
    comment_match = re.search(r"/\*\*([\s\S]*?)\*/", block)
    if comment_match:
        text = clean_comment(comment_match.group(0))
        text = re.sub(r"POST\s+/[^\s]+\s*", "", text).strip()
        text = re.sub(r"swaggerApi\.json\s*当前未提供该接口定义[，,]?", "", text)
        text = re.sub(r"当前接口返回内容与地址列表一致[，,]?", "", text)
        text = re.sub(r"先按同结构缓存[。；;]?", "", text)
        text = re.sub(r"因此入参按空对象约束[。；;]?", "", text)
        return text.strip(" ，,。")
    line_comment = re.search(r"//\s*([^\n]+)\n\s*export", block)
    return clean(line_comment.group(1)) if line_comment else ""


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


def infer_response_type(block: str) -> str:
    promise_type = first_generic_argument(block, r"Promise")
    if promise_type:
        return promise_type
    request_type = first_generic_argument(block, r"(?:request|http\.post)")
    if request_type:
        return request_type
    return "unknown"


def infer_method(block: str) -> str:
    if "http.post" in block or "method: 'POST'" in block or 'method: "POST"' in block:
        return "POST"
    for method in ("GET", "PUT", "PATCH", "DELETE"):
        if f"method: '{method}'" in block or f'method: "{method}"' in block:
            return method
    return "POST"


def parse_body_literal(block: str) -> list[dict[str, Any]]:
    body_match = re.search(r"\b(?:body|data)\s*:\s*{", block)
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


def context_from_block(block: str, path: Path, root: Path) -> dict[str, Any]:
    return {
        "block": block,
        "body_fields": parse_body_literal(block),
        "request_type": infer_request_type(block),
        "response_type": infer_response_type(block),
        "method": infer_method(block),
        "service_file": relative_to_project(path, root),
        "service_name": infer_export_name(block),
        "description": infer_description(block),
    }


def extract_service_context(root: Path) -> dict[str, dict[str, Any]]:
    context: dict[str, dict[str, Any]] = {}
    usage_re = re.compile(r"\bAPI\.([A-Za-z_$][\w$]*)\b")
    direct_export_re = re.compile(
        r"export\s+const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*(?:request2?|http\.post)\s*\(\s*{",
        re.S,
    )
    for path in iter_source_files(root):
        text = read_text(path)
        for match in direct_export_re.finditer(text):
            symbol = match.group(1)
            block = surrounding_export_block(text, match.start())
            context.setdefault(symbol, {})
            context[symbol].update(context_from_block(block, path, root))
        for match in re.finditer(usage_re, text):
            symbol = match.group(1)
            block = surrounding_export_block(text, match.start())
            context.setdefault(symbol, {})
            context[symbol].update(context_from_block(block, path, root))
    return context


def resolve_ref(data: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    node: Any = data
    for part in ref[2:].split("/"):
        if not isinstance(node, dict):
            return {}
        node = node.get(part)
    return node if isinstance(node, dict) else {}


def schema_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return str(schema["$ref"]).split("/")[-1]
    value = schema.get("type")
    if value == "array":
        item_type = schema_type(schema.get("items", {}) if isinstance(schema.get("items"), dict) else {})
        return f"array<{item_type or 'unknown'}>"
    if value:
        return str(value)
    if "properties" in schema:
        return "object"
    return "unknown"


def flatten_schema(schema: dict[str, Any], data: dict[str, Any], prefix: str = "", required: set[str] | None = None, seen_refs: set[str] | None = None) -> list[dict[str, Any]]:
    required = required or set()
    seen_refs = seen_refs or set()
    if "$ref" in schema:
        ref = str(schema["$ref"])
        if ref in seen_refs:
            return []
        return flatten_schema(resolve_ref(data, ref), data, prefix, required, seen_refs | {ref})
    if schema.get("type") == "array":
        items = schema.get("items") if isinstance(schema.get("items"), dict) else {}
        array_path = f"{prefix}[]" if prefix else "[]"
        fields = [
            {
                "field": array_path,
                "type": schema_type(schema),
                "required": prefix in required,
                "description": clean(schema.get("description", "")),
                "enum": schema.get("enum", []),
                "enumDesc": clean(schema.get("enumDesc", "")),
            }
        ]
        fields.extend(flatten_schema(items, data, array_path, set(items.get("required", [])) if isinstance(items, dict) else set(), seen_refs))
        return fields
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        if prefix:
            return [
                {
                    "field": prefix,
                    "type": schema_type(schema),
                    "required": prefix.split(".")[-1].replace("[]", "") in required,
                    "description": clean(schema.get("description", "")),
                    "enum": schema.get("enum", []),
                    "enumDesc": clean(schema.get("enumDesc", "")),
                }
            ]
        return []
    local_required = set(schema.get("required", [])) if isinstance(schema.get("required"), list) else set()
    fields: list[dict[str, Any]] = []
    for name, child in properties.items():
        if not isinstance(child, dict):
            continue
        field_path = f"{prefix}.{name}" if prefix else str(name)
        field = {
            "field": field_path,
            "type": schema_type(child),
            "required": name in local_required or name in required,
            "description": clean(child.get("description", "")),
            "enum": child.get("enum", []),
            "enumDesc": clean(child.get("enumDesc", "")),
        }
        fields.append(field)
        if "$ref" in child or child.get("type") == "array" or isinstance(child.get("properties"), dict):
            fields.extend(flatten_schema(child, data, field_path, local_required, seen_refs))
    return fields


def swagger_request_fields(operation: dict[str, Any], data: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    parameters = operation.get("parameters", [])
    if not isinstance(parameters, list):
        return fields
    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue
        location = clean(parameter.get("in", "")) or "body"
        name = clean(parameter.get("name", "")) or "body"
        schema = parameter.get("schema")
        if isinstance(schema, dict):
            body_fields = flatten_schema(schema, data)
            if body_fields:
                for field in body_fields:
                    field["location"] = location
                fields.extend(body_fields)
            else:
                fields.append(
                    {
                        "location": location,
                        "field": name,
                        "type": schema_type(schema),
                        "required": bool(parameter.get("required", False)),
                        "description": clean(parameter.get("description", "")),
                        "enum": [],
                        "enumDesc": "",
                    }
                )
        else:
            fields.append(
                {
                    "location": location,
                    "field": name,
                    "type": clean(parameter.get("type", "unknown")),
                    "required": bool(parameter.get("required", False)),
                    "description": clean(parameter.get("description", "")),
                    "enum": parameter.get("enum", []),
                    "enumDesc": clean(parameter.get("enumDesc", "")),
                }
            )
    return fields


def swagger_response_fields(operation: dict[str, Any], data: dict[str, Any]) -> list[dict[str, Any]]:
    responses = operation.get("responses")
    if not isinstance(responses, dict):
        return []
    response = responses.get("200") or responses.get(200) or next(iter(responses.values()), {})
    if not isinstance(response, dict):
        return []
    schema = response.get("schema")
    if not isinstance(schema, dict):
        return []
    return flatten_schema(schema, data)


def extract_swagger_contracts(path: Path, app_name: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    data = json.loads(read_text(path))
    contracts: dict[str, dict[str, Any]] = {}
    paths = data.get("paths", {})
    if not isinstance(paths, dict):
        return contracts
    for path_value, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in HTTP_METHODS:
                continue
            operation = operation if isinstance(operation, dict) else {}
            tags = operation.get("tags") if isinstance(operation.get("tags"), list) else []
            contracts[str(path_value)] = {
                "appName": app_name,
                "module": str(tags[0]) if tags else "",
                "title": clean(operation.get("summary") or operation.get("operationId") or path_value),
                "path": str(path_value),
                "method": method.upper(),
                "source_type": "swagger",
                "request_fields": swagger_request_fields(operation, data),
                "response_fields": swagger_response_fields(operation, data),
            }
    return contracts


def module_for(record: dict[str, Any], context: dict[str, Any]) -> str:
    files = [short_file(str(item)) for item in record.get("files", [])]
    if context.get("service_file"):
        files.append(short_file(str(context["service_file"])))
    for name in files:
        if name in MODULE_BY_FILE:
            return MODULE_BY_FILE[name]
    return clean(record.get("module_hint")) or clean(record.get("semantic_hint")) or "未归类"


def choose_title(symbols: list[str], records: list[dict[str, Any]], contexts: list[dict[str, Any]], swagger: dict[str, Any] | None) -> str:
    if swagger and swagger.get("title"):
        return clean(swagger["title"])
    for symbol in symbols:
        if symbol in PURPOSE_BY_SYMBOL:
            return PURPOSE_BY_SYMBOL[symbol]
    for context in contexts:
        if context.get("description"):
            return clean(context["description"])
    for record in records:
        if record.get("semantic_hint"):
            return clean(record["semantic_hint"])
    return symbols[0] if symbols else "未命名接口"


def sanitize_filename(title: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]", "", clean(title))
    value = re.sub(r"\s+", "", value)
    value = value.strip(". ")
    return value or "未命名接口"


def unique_fields(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for field in fields:
        key = (field.get("field", ""), field.get("type", ""), field.get("description", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(field)
    return result


def ensure_request_fields(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if fields:
        return fields
    return [
        {
            "field": "body",
            "type": "Record<string, never>",
            "required": False,
            "description": "无请求字段或项目当前按空对象提交",
            "enum": [],
            "enumDesc": "",
        }
    ]


def ensure_response_fields(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if fields:
        return fields
    return [
        {
            "field": "data",
            "type": "unknown",
            "required": False,
            "description": "项目当前未声明具体响应结构，需正式接口文档校准",
            "enum": [],
            "enumDesc": "",
        }
    ]


def build_contracts(root: Path, app_name: str, swagger_path: Path | None) -> list[dict[str, Any]]:
    records_by_symbol = collect_api_usage(root, parse_api_config(root))
    type_map = parse_exported_types(root)
    contexts_by_symbol = extract_service_context(root)
    swagger_by_path = extract_swagger_contracts(swagger_path, app_name) if swagger_path else {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records_by_symbol.values():
        if not record.get("path"):
            continue
        grouped.setdefault(record["path"], []).append(record)
    contracts: list[dict[str, Any]] = []
    for path_value, records in grouped.items():
        symbols = sorted(record["symbol"] for record in records)
        contexts = [contexts_by_symbol.get(symbol, {}) for symbol in symbols]
        swagger = swagger_by_path.get(path_value)
        method = swagger.get("method") if swagger else next((ctx.get("method") for ctx in contexts if ctx.get("method")), "POST")
        title = choose_title(symbols, records, contexts, swagger)
        module = swagger.get("module") if swagger and swagger.get("module") else module_for(records[0], contexts[0] if contexts else {})
        source_type = "swagger" if swagger else "project-extracted"
        request_fields: list[dict[str, Any]] = []
        response_fields: list[dict[str, Any]] = []
        if swagger:
            request_fields = swagger.get("request_fields", [])
            response_fields = swagger.get("response_fields", [])
        else:
            for symbol in symbols:
                context = contexts_by_symbol.get(symbol, {})
                request_fields.extend(context.get("body_fields") or flatten_type(context.get("request_type", ""), type_map))
                response_fields.extend(flatten_type(context.get("response_type", "unknown"), type_map))
        contracts.append(
            {
                "appName": app_name,
                "module": module,
                "title": title,
                "path": path_value,
                "method": method or "POST",
                "source_type": source_type,
                "symbols": symbols,
                "request_fields": ensure_request_fields(unique_fields(request_fields)),
                "response_fields": ensure_response_fields(unique_fields(response_fields)),
                "keywords": unique_keywords([title, module, path_value, *symbols]),
            }
        )
    return sorted(contracts, key=lambda item: (item["module"], item["title"], item["path"]))


def unique_keywords(values: list[str]) -> list[str]:
    keywords: list[str] = []
    for value in values:
        for part in re.split(r"[\s,，/]+", clean(value)):
            if part and part not in keywords:
                keywords.append(part)
    return keywords


def field_row(field: dict[str, Any]) -> str:
    enum_value = field.get("enum", [])
    enum_text = ", ".join(str(item) for item in enum_value) if isinstance(enum_value, list) else clean(enum_value)
    return "| `{field}` | {type} | {required} | {desc} | {enum_text} | {enum_desc} |".format(
        field=clean_inline(field.get("field", "")),
        type=clean_inline(field.get("type", "unknown")),
        required="yes" if field.get("required") else "no",
        desc=clean_inline(field.get("description", "")),
        enum_text=clean_inline(enum_text),
        enum_desc=clean_inline(field.get("enumDesc", "")),
    )


def contract_markdown(contract: dict[str, Any], app_name: str) -> str:
    doc_status = "正式接口文档" if contract["source_type"] == "swagger" else "项目已用，待正式文档校准"
    today = date.today().isoformat()
    lines = [
        "---",
        f"title: {contract['title']}",
        "type: api-contract",
        "status: active",
        "tags:",
        "  - api",
        "  - api-contract",
        f"  - {app_name}",
        f"appName: {app_name}",
        f"path: {contract['path']}",
        f"method: {contract['method']}",
        f"source_type: {contract['source_type']}",
        f"created: {today}",
        f"updated: {today}",
        f"summary: {app_name} 的{contract['title']}接口契约。",
        "next_action: 使用时先通过 _indexes 命中本文件，再按入参/出参落地代码。",
        "---",
        "",
        f"# {contract['title']}",
        "",
        "## 定位",
        "",
        f"- appName：[[Work/API/apps/{app_name}/{app_name}|{app_name}]]",
        f"- 模块：{contract['module']}",
        f"- API symbol：{', '.join(f'`{symbol}`' for symbol in contract['symbols'])}",
        f"- Method / Path：`{contract['method']} {contract['path']}`",
        "- 鉴权：默认走全局请求头；业务接口的 token 以调用处 `token` 参数为准，埋点接口不发送 token。",
        f"- 文档状态：{doc_status}",
        "",
        "## 用途",
        "",
        f"{contract['title']}。如需确认 baseURL、响应码或 header，先从 app 节点进入对应全局文档。",
        "",
        "## Request Fields",
        "",
        "| Field | Type | Required | Description | Enum | Enum Desc |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend(field_row(field) for field in contract["request_fields"])
    lines.extend(
        [
            "",
            "## Response Fields",
            "",
            "| Field | Type | Required | Description | Enum | Enum Desc |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(field_row(field) for field in contract["response_fields"])
    lines.extend(
        [
            "",
        "## 状态码和业务判断",
        "",
            "- 成功：请求层 resolve 解密后的响应对象，具体字段以正式接口文档校准。",
            "- `301`：当前项目请求层会延迟调用原生 `goBackToLogin`，常见含义是登录态失效。",
            "- 其他 code/status：以正式接口文档或业务调用处判断为准，当前项目代码未完整声明。",
        "",
        "## 关键词",
            "",
            ", ".join(f"`{keyword}`" for keyword in contract["keywords"]),
            "",
        ]
    )
    return "\n".join(lines)


def build_global_config(root: Path, app_name: str) -> str:
    envs = parse_env_files(root)
    request_files = [
        root / "src" / "services" / "http.ts",
        root / "src" / "utils" / "request.ts",
        root / "src" / "utils" / "request.js",
    ]
    text = "\n".join(read_text(path) for path in request_files if path.exists())
    header_keys = sorted(
        set(re.findall(r"headers\[['\"]([^'\"]+)['\"]\]", text))
        | set(re.findall(r"['\"]([^'\"]+)['\"]\s*:", text))
    )
    today = date.today().isoformat()
    lines = [
        "---",
        f"title: {app_name} 全局配置",
        "type: api-app-config",
        "status: active",
        "tags:",
        "  - api",
        "  - app-config",
        f"  - {app_name}",
        f"created: {today}",
        f"updated: {today}",
        f"summary: {app_name} 的 API baseURL、响应码、请求头和全局取值来源。",
        "next_action: 接接口时先读取本文件确认 baseURL、header key 和响应码。",
        "---",
        "",
        f"# {app_name} 全局配置",
        "",
        "## App 信息",
        "",
        "| 字段 | 取值 | 来源 |",
        "| --- | --- | --- |",
    ]
    merged = {}
    for values in envs.values():
        merged.update(values)
    app_fields = [
        ("appName", merged.get("VITE_APP_NAME", app_name), "VITE_APP_NAME"),
        ("appVersion", merged.get("VITE_APP_VERSION", "1.0.0"), "VITE_APP_VERSION / 默认值"),
        ("requestAesKey", merged.get("VITE_REQUEST_AES_KEY", ""), "VITE_REQUEST_AES_KEY，用于业务接口请求体加密和响应解密"),
        ("trackingAesKey", merged.get("VITE_TRACKING_AES_KEY", ""), "VITE_TRACKING_AES_KEY，用于埋点接口请求体加密和响应解密"),
        ("privacyUrl", merged.get("VITE_PRIVACY_URL", ""), "VITE_PRIVACY_URL"),
        ("loanAgreementUrl", merged.get("VITE_LOAN_AGREEMENT_URL", ""), "VITE_LOAN_AGREEMENT_URL"),
        ("token", "options.token || ''", "src/utils/request.js 中 request() 透传调用参数 token"),
    ]
    lines.extend(f"| `{key}` | `{value}` | {source} |" for key, value, source in app_fields)
    lines.extend(
        [
            "",
            "## 环境地址",
            "",
            "环境地址只记录后端接口访问地址，不记录 H5 页面地址。测试分支里的 `.env.production` 仍视为测试地址；正式地址只从 `master`、`master-co`、`master-ng` 等正式分支读取。",
            "",
            "| 环境 | 后端 API baseURL | 来源 |",
            "| --- | --- | --- |",
        ]
    )
    for row in collect_backend_api_envs(root, envs):
        lines.append(f"| {row['env']} | `{row['url']}` | {row['source']} |")
    lines.extend(
        [
            "",
            "## 响应码",
            "",
            "| code/status | 含义 | 处理方式 |",
            "| --- | --- | --- |",
            "| 成功响应 | 具体字段待正式文档校准 | 请求层 resolve 解密后的响应对象 |",
            "| `301` | 登录态失效/需回登录页 | `request()` 延迟调用原生 `goBackToLogin` |",
            "| 其他 code/status | 项目代码未统一声明 | 按正式接口文档或业务调用处判断 |",
            "",
            "## 请求头",
            "",
            "| Header key | 语义字段 | 说明 | 取值来源 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for key in header_keys:
        if key in {"Accept", "Content-Type"}:
            continue
        if key == "content-type":
            semantic, desc, source = ("contentType", "JSON 请求体", "固定 `application/json`")
        elif key == "token":
            semantic, desc, source = ("token", "登录 token，仅 `request()` 按调用参数发送", "options.token || ''")
        elif key == "appName":
            semantic, desc, source = ("appName", "App 名称", "import.meta.env.VITE_APP_NAME")
        else:
            semantic, desc, source = HEADER_SEMANTICS.get(key, ("unknown", "待确认", "项目代码"))
        lines.append(f"| `{key}` | `{semantic}` | {desc} | {source} |")
    lines.extend(
        [
            "",
            "## 读取原则",
            "",
            "- 接口实现时不要猜 header key，先读本文件。",
            "- 具体接口入参/出参只读命中的 contract，不遍历全部接口文档。",
            "- token、loginId、device 信息以本文件和项目登录态来源为准；只有检测到真实原生交互证据时，app 节点才会额外生成原生交互入口。",
            "",
        ]
    )
    return "\n".join(lines)


def extract_ts_object(text: str, name: str) -> dict[str, str]:
    match = re.search(rf"export\s+const\s+{re.escape(name)}\s*=\s*{{", text)
    if not match:
        return {}
    start = text.find("{", match.start())
    end = find_matching_brace(text, start)
    if end == -1:
        return {}
    body = text[start + 1 : end]
    values: dict[str, str] = {}
    for item in re.finditer(r"([A-Za-z_$][\w$]*)\s*:\s*['\"]([^'\"]+)['\"]", body):
        values[item.group(1)] = item.group(2)
    return values


def collect_native_bridge(root: Path, extra_mapping: dict[str, str] | None = None) -> dict[str, dict[str, str]]:
    path = root / "src" / "utils" / "nativeFieldMap.ts"
    text = read_text(path) if path.exists() else ""
    methods = extract_ts_object(text, "NATIVE_METHOD_CODES")
    callbacks = extract_ts_object(text, "NATIVE_CALLBACK_CODES")
    fields = extract_ts_object(text, "NATIVE_FIELD_CODES")
    callback_allowlist = {
        "getDataInfo",
        "getDataInfoCallback",
        "imageCallBack",
        "openAlbumCallBack",
        "openCameraCallBack",
        "submitFirstStepCallBack",
    }
    for source_file in iter_source_files(root):
        source_text = read_text(source_file)
        constants = collect_string_constants(source_text)
        for match in re.finditer(r"postAppMessage\(\s*['\"]([^'\"]+)['\"]", source_text):
            method = match.group(1)
            methods.setdefault(method, method)
        for match in re.finditer(r"postAppMessage\(\s*([A-Z][A-Z0-9_]*)\b", source_text):
            method = constants.get(match.group(1))
            if method:
                methods.setdefault(method, method)
        for match in re.finditer(r"window\.([A-Za-z_$][\w$]*)\s*=", source_text):
            callback = match.group(1)
            if callback in callback_allowlist or callback.endswith("CallBack"):
                callbacks.setdefault(callback, callback)
    extra_mapping = extra_mapping or {}
    method_names = set(methods)
    callback_names = set(callbacks)
    for key, value in extra_mapping.items():
        if key in callback_names or key.endswith("CallBack") or key == "onNativeBack":
            callbacks.setdefault(key, value)
        elif key in method_names or key in {
            "goBack",
            "logOut",
            "getToken",
            "getDeviceInfo",
            "getAllPermissions",
            "openAlbum",
            "openContact",
            "updateUserInfo",
            "reload",
            "toEditStepInfo",
            "controlTab",
            "firstLoanApplySuc",
            "openBrowser",
            "toLoanAgreement",
            "openWebView",
            "bannerJump",
            "uploadAllRiskData",
        }:
            methods.setdefault(key, value)
        else:
            fields.setdefault(key, value)
    return {"methods": methods, "callbacks": callbacks, "fields": fields}


def has_native_bridge(native_bridge: dict[str, dict[str, str]]) -> bool:
    return any(native_bridge.get(name) for name in ("methods", "callbacks", "fields"))


def build_native_bridge(root: Path, app_name: str, extra_mapping: dict[str, str] | None = None) -> str:
    native_bridge = collect_native_bridge(root, extra_mapping)
    if not has_native_bridge(native_bridge):
        return ""
    methods = native_bridge["methods"]
    callbacks = native_bridge["callbacks"]
    fields = native_bridge["fields"]
    extra_mapping = extra_mapping or {}
    today = date.today().isoformat()
    lines = [
        "---",
        f"title: {app_name} 原生交互",
        "type: api-native-bridge",
        "status: active",
        "tags:",
        "  - api",
        "  - native-bridge",
        f"  - {app_name}",
        f"created: {today}",
        f"updated: {today}",
        f"summary: {app_name} 的原生方法、callback、字段和混淆名。",
        "next_action: 涉及 WebView/Native 交互时先读本文件确认方法名和字段名。",
        "---",
        "",
        f"# {app_name} 原生交互",
        "",
        "## 方法",
        "",
        "| 语义方法 | 混淆名 | 方向 | 来源 |",
        "| --- | --- | --- | --- |",
    ]
    for key, value in sorted(methods.items()):
        source = "用户提供" if extra_mapping.get(key) == value else "项目代码"
        lines.append(f"| `{key}` | `{value}` | H5 -> Native | {source} |")
    lines.extend(["", "## Callback", "", "| 语义 callback | 混淆名 | 方向 | 来源 |", "| --- | --- | --- | --- |"])
    for key, value in sorted(callbacks.items()):
        source = "用户提供" if extra_mapping.get(key) == value else "项目代码"
        lines.append(f"| `{key}` | `{value}` | Native -> H5 | {source} |")
    lines.extend(["", "## 字段", "", "| 语义字段 | 混淆名 | 用途/状态 | 来源 |", "| --- | --- | --- | --- |"])
    pending = {"status", "adid", "deviceId"}
    for key, value in sorted(fields.items()):
        source = "用户提供" if extra_mapping.get(key) == value else "项目代码"
        status = "使用点待确认" if key in pending and source == "用户提供" else "原生交互字段"
        lines.append(f"| `{key}` | `{value}` | {status} | {source} |")
    lines.extend(
        [
            "",
            "## 使用原则",
            "",
            "- 服务端接口字段和原生 bridge 字段分开处理，不把原生字段当作服务端 response key 替换。",
            "- H5 发送给 Native 前可按混淆字段编码，Native 回调进入业务前再还原为语义字段。",
            "- URL query 中的 token、loginId、device key 以本文件和 [[Work/API/apps/{}/全局配置]] 为准。".format(app_name),
            "",
        ]
    )
    return "\n".join(lines)


def write_indexes(app_dir: Path, app_name: str, contracts: list[dict[str, Any]], file_by_path: dict[str, str]) -> None:
    index_dir = app_dir / "_indexes"
    index_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    by_path = {}
    by_symbol = {}
    for contract in contracts:
        rel_file = f"contracts/{file_by_path[contract['path']]}"
        row = {
            "appName": app_name,
            "module": contract["module"],
            "title": contract["title"],
            "symbols": contract["symbols"],
            "path": contract["path"],
            "method": contract["method"],
            "contract_file": rel_file,
            "keywords": contract["keywords"],
            "request_field_count": len(contract["request_fields"]),
            "response_field_count": len(contract["response_fields"]),
            "doc_status": "正式接口文档" if contract["source_type"] == "swagger" else "项目已用，待正式文档校准",
            "source_type": contract["source_type"],
        }
        rows.append(row)
        by_path[contract["path"]] = row
        for symbol in contract["symbols"]:
            by_symbol[symbol] = row
    write_text(index_dir / "contracts.jsonl", "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows))
    write_text(index_dir / "by-path.json", json.dumps(by_path, ensure_ascii=False, indent=2) + "\n")
    write_text(index_dir / "by-symbol.json", json.dumps(by_symbol, ensure_ascii=False, indent=2) + "\n")


def write_human_index(app_dir: Path, app_name: str, contracts: list[dict[str, Any]], file_by_path: dict[str, str]) -> None:
    today = date.today().isoformat()
    lines = [
        "---",
        f"title: {app_name} 接口索引",
        "type: api-contract-index",
        "status: active",
        "tags:",
        "  - api",
        "  - api-contract-index",
        f"  - {app_name}",
        f"created: {today}",
        f"updated: {today}",
        f"summary: {app_name} 的接口快速定位入口。",
        "next_action: 按接口作用、API symbol 或 path 定位 contract。",
        "---",
        "",
        f"# {app_name} 接口索引",
        "",
        f"- appName：`{app_name}`",
        f"- 接口数：{len(contracts)}",
        f"- 正式 Swagger 覆盖：{len([item for item in contracts if item['source_type'] == 'swagger'])}",
        f"- 项目已用待校准：{len([item for item in contracts if item['source_type'] != 'swagger'])}",
        "",
        "## 使用方式",
        "",
        "- 人看：先在本页按中文用途、API symbol 或 path 找接口，再打开 contract。",
        "- 工作流看：先读 `_indexes/contracts.jsonl`，命中后只打开对应 contract。",
        "",
    ]
    modules = sorted({contract["module"] for contract in contracts})
    for module in modules:
        lines.extend([f"## {module}", "", "| 用途 | API symbol | Method / Path | 入参 | 出参 | 文档状态 |", "| --- | --- | --- | --- | --- | --- |"])
        for contract in [item for item in contracts if item["module"] == module]:
            link = f"[[Work/API/apps/{app_name}/contracts/{Path(file_by_path[contract['path']]).stem}|{contract['title']}]]"
            status = "正式接口文档" if contract["source_type"] == "swagger" else "项目已用，待正式文档校准"
            lines.append(
                "| {link} | {symbols} | `{method} {path}` | {req} | {resp} | {status} |".format(
                    link=link,
                    symbols=", ".join(f"`{symbol}`" for symbol in contract["symbols"]),
                    method=contract["method"],
                    path=contract["path"],
                    req=len(contract["request_fields"]),
                    resp=len(contract["response_fields"]),
                    status=status,
                )
            )
        lines.append("")
    write_text(app_dir / "contracts" / "索引.md", "\n".join(lines))


def known_scene_knowledge_links(app_name: str) -> list[dict[str, str]]:
    known = {
        "confiq": [
            {"path": "Work/H5/业务场景/进件流程", "title": "进件流程"},
            {"path": "Work/H5/公共规范/App WebView兼容", "title": "App WebView兼容"},
            {"path": "Work/H5/公共规范/视觉还原与截图预算", "title": "视觉还原与截图预算"},
        ],
    }
    return known.get(app_name.lower(), [])


def write_app_docs(kb_root: Path, app_name: str, contracts: list[dict[str, Any]], project_root: Path, extra_mapping: dict[str, str] | None, swagger_path: Path | None, clean_legacy: bool) -> dict[str, Any]:
    api_root = kb_root / "Work" / "API"
    app_root = api_root / "apps"
    app_dir = app_root / app_name
    if app_dir.exists():
        shutil.rmtree(app_dir)
    (app_dir / "contracts").mkdir(parents=True, exist_ok=True)
    (app_dir / "raw").mkdir(parents=True, exist_ok=True)
    file_by_path: dict[str, str] = {}
    used_names: dict[str, int] = {}
    for contract in contracts:
        base = sanitize_filename(contract["title"])
        count = used_names.get(base, 0) + 1
        used_names[base] = count
        filename = f"{base}.md" if count == 1 else f"{base}{count}.md"
        file_by_path[contract["path"]] = filename
        write_text(app_dir / "contracts" / filename, contract_markdown(contract, app_name))
    write_human_index(app_dir, app_name, contracts, file_by_path)
    write_indexes(app_dir, app_name, contracts, file_by_path)
    write_text(app_dir / "全局配置.md", build_global_config(project_root, app_name))
    native_bridge_text = build_native_bridge(project_root, app_name, extra_mapping)
    has_native = bool(native_bridge_text.strip())
    if has_native:
        write_text(app_dir / "原生交互.md", native_bridge_text)
    if swagger_path and swagger_path.exists():
        shutil.copyfile(swagger_path, app_dir / "raw" / swagger_path.name)
    today = date.today().isoformat()
    contract_links = [
        f"- [[Work/API/apps/{app_name}/contracts/{Path(file_by_path[contract['path']]).stem}|{contract['title']}]]"
        for contract in contracts
    ]
    scene_knowledge = known_scene_knowledge_links(app_name)
    scene_links = [f"- [[{item['path']}|{item['title']}]]" for item in scene_knowledge]
    app_entry_lines = [
        f"- 工作流入口：[[Work/API/apps/{app_name}/README|README]]",
        f"- 接口索引：[[Work/API/apps/{app_name}/contracts/索引]]",
        f"- 全局配置：[[Work/API/apps/{app_name}/全局配置]]",
    ]
    if has_native:
        app_entry_lines.append(f"- 原生交互：[[Work/API/apps/{app_name}/原生交互]]")
    app_summary = f"{app_name} 的接口 contract、全局配置" + ("和 app-specific 原生交互" if has_native else "") + "中心节点。"
    app_next_action = "先进入接口索引定位 contract；涉及 H5 工作实践时再读取相关 Work/H5 知识。"
    write_text(
        app_dir / f"{app_name}.md",
        "\n".join(
            [
                "---",
                f"title: {app_name}",
                "type: api-app",
                "status: active",
                "tags:",
                "  - api",
                "  - app",
                f"  - {app_name}",
                f"appName: {app_name}",
                f"created: {today}",
                f"updated: {today}",
                f"summary: {app_summary}",
                f"next_action: {app_next_action}",
                "---",
                "",
                f"# {app_name}",
                "",
                "## 入口",
                "",
                *app_entry_lines,
                "",
                "## 接口",
                "",
                *contract_links,
                "",
                *(["## 相关场景知识", "", *scene_links, ""] if scene_links else []),
            ]
        ),
    )
    readme_entry_lines = [
        f"- App 节点：[[Work/API/apps/{app_name}/{app_name}|{app_name}]]",
        f"- 全局配置：[[Work/API/apps/{app_name}/全局配置]]",
        f"- 接口索引：[[Work/API/apps/{app_name}/contracts/索引]]",
    ]
    readme_steps = [
        "1. 读取本文件确认 appName。",
        "2. 读取 `_indexes/contracts.jsonl` 按 path、symbol 或关键词命中接口。",
        "3. 只打开命中的 `contracts/<中文接口作用>.md`。",
        "4. 涉及 baseURL/header/响应码时读取 `全局配置.md`。",
    ]
    readme_summary = f"{app_name} 的接口契约、全局配置" + ("、app-specific 原生交互" if has_native else "") + "和快速索引入口。"
    if has_native:
        readme_entry_lines.insert(2, f"- 原生交互：[[Work/API/apps/{app_name}/原生交互]]")
        readme_steps.append("5. 涉及 app-specific Native bridge/callback/混淆字段时读取 `原生交互.md`。")
    write_text(
        app_dir / "README.md",
        "\n".join(
            [
                "---",
                f"title: {app_name} API 入口",
                "type: api-app-index",
                "status: active",
                "tags:",
                "  - api",
                f"  - {app_name}",
                f"created: {today}",
                f"updated: {today}",
                f"summary: {readme_summary}",
                "next_action: 工作流使用时先读 _indexes，再打开命中的 contract。",
                "---",
                "",
                f"# {app_name} API 入口",
                "",
                "## 入口",
                "",
                *readme_entry_lines,
                "",
                "## 工作流读取顺序",
                "",
                *readme_steps,
                "",
                *(["## 相关场景知识", "", *scene_links, ""] if scene_links else []),
            ]
        ),
    )
    write_text(
        api_root / "MOC.md",
        "\n".join(
            [
                "---",
                "title: API 接口契约知识地图",
                "type: index",
                "status: active",
                "tags:",
                "  - api",
                "  - contract",
                "  - moc",
                f"created: {today}",
                f"updated: {today}",
                "summary: Work 下的 API 模块只维护按 appName 归档的接口 contract、全局配置、app-specific 原生交互和快速索引。",
                "next_action: 新增或更新 app 接口时进入 Work/API/apps/<appName>；H5 工作实践读取 Work/H5。",
                "---",
                "",
                "# API 接口契约知识地图",
                "",
                "## 入口",
                "",
                "- 返回工作实践入口：[[Work/MOC]]",
                "- App 接口归档：[[Work/API/apps/MOC]]",
                "",
                "## 使用原则",
                "",
                "- 只按 appName 划分，不按新/旧系统或国家划分。",
                "- API 只放接口事实：path、method、request/response、header、响应码、baseURL 和 app-specific 原生字段。",
                "- H5 进件、首复贷、App WebView 兼容、视觉还原、截图预算等工作实践知识归 `Work/H5`。",
                "- 每个 app 的真实接口 contract 是该 app 的接口实现依据。",
                "- 工作流先读 app 索引，再打开命中的接口 contract，不遍历全量内容。",
                "- App 入口页可以聚合相关 `Work/H5` 场景知识；单个接口 contract 不反向链接公共规范。",
                "- 服务端接口和全局 header 分开记录；只有检测到真实原生 bridge/callback 证据时才额外生成 app-specific 原生交互文档。",
                "",
            ]
        ),
    )
    app_index_row = {
        "appName": app_name,
        "app_dir": f"Work/API/apps/{app_name}",
        "app_node": f"Work/API/apps/{app_name}/{app_name}.md",
        "readme": f"Work/API/apps/{app_name}/README.md",
        "global_config": f"Work/API/apps/{app_name}/全局配置.md",
        "contract_index": f"Work/API/apps/{app_name}/_indexes/contracts.jsonl",
        "contract_count": len(contracts),
        "updated": today,
    }
    if has_native:
        app_index_row["native_bridge"] = f"Work/API/apps/{app_name}/原生交互.md"
    if scene_knowledge:
        app_index_row["scene_knowledge"] = [item["path"] + ".md" for item in scene_knowledge]
    app_index_path = app_root / "_app-index.jsonl"
    app_index_rows: dict[str, dict[str, Any]] = {}
    if app_index_path.exists():
        for line in read_text(app_index_path).splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("appName"):
                app_index_rows[str(row["appName"])] = row
    app_index_rows[app_name] = app_index_row
    sorted_app_rows = [app_index_rows[key] for key in sorted(app_index_rows)]
    write_text(app_index_path, "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in sorted_app_rows))
    app_links = [f"- [[Work/API/apps/{row['appName']}/README|{row['appName']}]]" for row in sorted_app_rows]
    write_text(
        app_root / "MOC.md",
        "\n".join(
            [
                "---",
                "title: API App 索引",
                "type: index",
                "status: active",
                "tags:",
                "  - api",
                "  - app-index",
                f"created: {today}",
                f"updated: {today}",
                "summary: 所有按 appName 归档的接口 contract 入口，H5 工作实践知识由 app 入口聚合到 Work/H5。",
                "next_action: 使用 _app-index.jsonl 快速定位 app 目录，再按 app README 读取命中 contract 或相关 Work/H5 场景。",
                "---",
                "",
                "# API App 索引",
                "",
                *app_links,
                "",
                "## 工作流读取",
                "",
                "- 先读 `_app-index.jsonl` 定位 appName。",
                "- 再读对应 app 的 `_indexes/contracts.jsonl` 定位接口。",
                "- 只打开命中的 contract；不要遍历全量接口内容。",
                "- 进件、首复贷、App WebView、视觉还原和截图预算等公共规范读取 `Work/H5`，不写入 API contract。",
                "",
            ]
        ),
    )
    legacy = kb_root / "API"
    if clean_legacy and legacy.exists():
        shutil.rmtree(legacy)
    return {"app_dir": str(app_dir), "contract_count": len(contracts), "file_by_path": file_by_path}


def parse_extra_mapping(value: str) -> dict[str, str]:
    if not value:
        return {}
    raw = value
    path = Path(value)
    if path.exists():
        raw = read_text(path)
    raw = raw.lstrip("\ufeff").strip()
    data = json.loads(raw)
    return {str(key): str(item) for key, item in data.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--kb-root", required=True, type=Path)
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--swagger", type=Path)
    parser.add_argument("--extra-native-mapping-json", default="")
    parser.add_argument("--clean-legacy", action="store_true")
    args = parser.parse_args()

    swagger_path = args.swagger or (args.project_root / "swaggerApi.json")
    contracts = build_contracts(args.project_root, args.app_name, swagger_path if swagger_path.exists() else None)
    result = write_app_docs(
        args.kb_root,
        args.app_name,
        contracts,
        args.project_root,
        parse_extra_mapping(args.extra_native_mapping_json),
        swagger_path if swagger_path.exists() else None,
        args.clean_legacy,
    )
    print(
        json.dumps(
            {
                "appName": args.app_name,
                "app_dir": result["app_dir"],
                "contracts": result["contract_count"],
                "swagger": len([item for item in contracts if item["source_type"] == "swagger"]),
                "project_extracted": len([item for item in contracts if item["source_type"] != "swagger"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
