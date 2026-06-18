#!/usr/bin/env python3
"""Extract request and response field structures from a project Swagger document."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def clean(value: Any) -> str:
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()


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


def flatten_schema(
    schema: dict[str, Any],
    data: dict[str, Any],
    prefix: str = "",
    required: set[str] | None = None,
    seen_refs: set[str] | None = None,
) -> list[dict[str, Any]]:
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


def request_fields(operation: dict[str, Any], data: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    parameters = operation.get("parameters", [])
    if not isinstance(parameters, list):
        return fields
    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue
        location = clean(parameter.get("in", ""))
        name = clean(parameter.get("name", ""))
        schema = parameter.get("schema")
        if isinstance(schema, dict):
            body_fields = flatten_schema(schema, data)
            if body_fields:
                for field in body_fields:
                    field["location"] = location or "body"
                fields.extend(body_fields)
            else:
                fields.append(
                    {
                        "location": location or "body",
                        "field": name or "body",
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


def response_fields(operation: dict[str, Any], data: dict[str, Any]) -> list[dict[str, Any]]:
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


def extract_contracts(source: Path, app_name: str) -> list[dict[str, Any]]:
    data = json.loads(read_text(source))
    paths = data.get("paths", {})
    if not isinstance(paths, dict):
        return []
    contracts: list[dict[str, Any]] = []
    for path_value, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in HTTP_METHODS:
                continue
            operation = operation if isinstance(operation, dict) else {}
            tags = operation.get("tags") if isinstance(operation.get("tags"), list) else []
            contracts.append(
                {
                    "appName": app_name,
                    "module": str(tags[0]) if tags else "",
                    "title": clean(operation.get("summary") or operation.get("operationId") or path_value),
                    "path": str(path_value),
                    "method": method.upper(),
                    "source_file": source.name,
                    "request_fields": request_fields(operation, data),
                    "response_fields": response_fields(operation, data),
                }
            )
    return sorted(contracts, key=lambda item: (item["module"], item["path"], item["method"]))


def write_jsonl(contracts: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for contract in contracts:
            handle.write(json.dumps(contract, ensure_ascii=False, separators=(",", ":")) + "\n")


def field_row(field: dict[str, Any]) -> str:
    def cell(value: Any) -> str:
        return clean(value).replace("|", "\\|").replace("\n", "<br>")

    enum_desc = cell(field.get("enumDesc", ""))
    enum_value = field.get("enum", [])
    enum_text = ", ".join(str(item) for item in enum_value) if isinstance(enum_value, list) else clean(enum_value)
    desc = cell(field.get("description", ""))
    return "| `{field}` | {type} | {required} | {desc} | {enum_text} | {enum_desc} |".format(
        field=cell(field.get("field", "")),
        type=cell(field.get("type", "")),
        required="yes" if field.get("required") else "no",
        desc=desc,
        enum_text=cell(enum_text),
        enum_desc=enum_desc,
    )


def write_markdown(contracts: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"title: {path.stem}",
        "type: api-contracts",
        "status: active",
        "tags:",
        "  - api",
        "  - endpoint-contracts",
        "summary: Request and response structures extracted from a project API document.",
        "---",
        "",
        f"# {path.stem}",
        "",
    ]
    for contract in contracts:
        lines.extend(
            [
                f"## {contract['method']} {contract['path']}",
                "",
                f"- 模块：{contract['module']}",
                f"- 标题：{contract['title']}",
                "",
                "### Request Fields",
                "",
                "| Field | Type | Required | Description | Enum | Enum Desc |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        request = contract.get("request_fields", [])
        if request:
            lines.extend(field_row(field) for field in request)
        else:
            lines.append("|  |  |  | 无请求字段 |  |  |")
        lines.extend(
            [
                "",
                "### Response Fields",
                "",
                "| Field | Type | Required | Description | Enum | Enum Desc |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        response = contract.get("response_fields", [])
        if response:
            lines.extend(field_row(field) for field in response)
        else:
            lines.append("|  |  |  | 未解析到响应字段 |  |  |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def endpoint_slug(contract: dict[str, Any]) -> str:
    raw = f"{contract.get('method', '')}-{contract.get('path', '')}"
    slug = re.sub(r"[^A-Za-z0-9]+", "-", raw).strip("-").lower()
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}"


def contract_markdown(contract: dict[str, Any]) -> str:
    lines = [
        "---",
        f"title: {contract.get('method', '')} {contract.get('path', '')}",
        "type: api-contract",
        "status: active",
        "tags:",
        "  - api",
        "  - api-contract",
        f"appName: {contract.get('appName', '')}",
        f"path: {contract.get('path', '')}",
        f"method: {contract.get('method', '')}",
        "source_type: swagger",
        "---",
        "",
        f"# {contract.get('method', '')} {contract.get('path', '')}",
        "",
        f"- 模块：{contract.get('module', '')}",
        f"- 标题：{contract.get('title', '')}",
        "- 文档状态：正式接口文档",
        "",
        "## Request Fields",
        "",
        "| Field | Type | Required | Description | Enum | Enum Desc |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    request = contract.get("request_fields", [])
    lines.extend(field_row(field) for field in request) if request else lines.append("|  |  |  | 无请求字段 |  |  |")
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
    lines.extend(field_row(field) for field in response) if response else lines.append("|  |  |  | 未解析到响应字段 |  |  |")
    return "\n".join(lines) + "\n"


def write_endpoint_files(contracts: list[dict[str, Any]], out_dir: Path) -> list[dict[str, Any]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    index: list[dict[str, Any]] = []
    for contract in contracts:
        slug = endpoint_slug(contract)
        json_path = out_dir / f"{slug}.json"
        md_path = out_dir / f"{slug}.md"
        json_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_path.write_text(contract_markdown(contract), encoding="utf-8")
        index.append(
            {
                "appName": contract.get("appName", ""),
                "module": contract.get("module", ""),
                "title": contract.get("title", ""),
                "path": contract.get("path", ""),
                "method": contract.get("method", ""),
                "json_file": json_path.name,
                "markdown_file": md_path.name,
                "request_field_count": len(contract.get("request_fields", [])),
                "response_field_count": len(contract.get("response_fields", [])),
                "source_type": "swagger",
            }
        )
    (out_dir / "index.jsonl").write_text(
        "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in index),
        encoding="utf-8",
    )
    return index


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--app-name", default="")
    parser.add_argument("--out-jsonl", required=True, type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    contracts = extract_contracts(args.source, args.app_name)
    write_jsonl(contracts, args.out_jsonl)
    if args.out_md:
        write_markdown(contracts, args.out_md)
    endpoint_file_count = 0
    if args.out_dir:
        endpoint_file_count = len(write_endpoint_files(contracts, args.out_dir))
    response_field_count = sum(len(contract.get("response_fields", [])) for contract in contracts)
    print(
        json.dumps(
            {
                "source": str(args.source),
                "count": len(contracts),
                "response_field_count": response_field_count,
                "endpoint_file_count": endpoint_file_count,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
