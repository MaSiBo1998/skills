#!/usr/bin/env python3
"""Build a readable project API summary from manifest and endpoint indexes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MODULE_BY_FILE = {
    "home.ts": "首复贷/首页",
    "product.ts": "产品/订单详情",
    "order.ts": "订单/还款",
    "banner.ts": "Banner",
    "user.ts": "用户/首页",
    "apply.ts": "进件",
    "monitor.ts": "飞书告警",
    "feedback.ts": "客服反馈",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def clean(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\r\n", " ").replace("\n", " ").strip()


def short_file(path_value: str) -> str:
    return path_value.replace("\\", "/").split("/")[-1]


def module_for(record: dict[str, Any]) -> str:
    for file_path in record.get("files", []):
        name = short_file(str(file_path))
        if name in MODULE_BY_FILE:
            return MODULE_BY_FILE[name]
    return clean(record.get("semantic_hint")) or "未归类"


def build_rows(manifest: list[dict[str, Any]], endpoints: list[dict[str, Any]], contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    endpoint_by_path = {item.get("path"): item for item in endpoints}
    contract_by_path = {item.get("path"): item for item in contracts}
    rows: list[dict[str, Any]] = []
    for record in manifest:
        path = record.get("path", "")
        endpoint = endpoint_by_path.get(path)
        contract = contract_by_path.get(path)
        contract_source_type = contract.get("source_type", "swagger") if contract else ""
        if endpoint:
            doc_status = "正式文档"
        elif contract_source_type == "project-extracted":
            doc_status = "待正式文档确认"
        else:
            doc_status = "待补文档"
        title = contract.get("title") if contract else ""
        if not title:
            title = endpoint.get("title", "") if endpoint else ""
        if not title:
            title = record.get("semantic_hint", "") or record.get("symbol", "")
        rows.append(
            {
                "module": module_for(record),
                "symbol": record.get("symbol", ""),
                "path": path,
                "title": title,
                "doc_status": doc_status,
                "official_doc_covered": bool(endpoint),
                "contract_source_type": contract_source_type,
                "contract_file": contract.get("markdown_file", "") if contract else "",
                "request_field_count": contract.get("request_field_count", 0) if contract else 0,
                "response_field_count": contract.get("response_field_count", 0) if contract else 0,
            }
        )
    return sorted(rows, key=lambda item: (item["module"], item["symbol"]))


def write_pending(rows: list[dict[str, Any]], path: Path) -> None:
    pending = [
        {
            "module": row.get("module", ""),
            "symbol": row.get("symbol", ""),
            "path": row.get("path", ""),
            "title": row.get("title", ""),
            "contract_file": row.get("contract_file", ""),
            "request_field_count": row.get("request_field_count", 0),
            "response_field_count": row.get("response_field_count", 0),
            "doc_status": row.get("doc_status", ""),
        }
        for row in rows
        if not row.get("official_doc_covered")
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in pending),
        encoding="utf-8",
    )


def write_markdown(rows: list[dict[str, Any]], path: Path, app_name: str, project_root: str) -> None:
    total = len(rows)
    covered = len([row for row in rows if row.get("official_doc_covered")])
    code_contracts = len([row for row in rows if row.get("contract_source_type") == "project-extracted"])
    pending = len([row for row in rows if not row.get("official_doc_covered")])
    contract_files = sorted({row.get("contract_file", "") for row in rows if row.get("contract_file")})
    modules = sorted({row["module"] for row in rows})
    lines = [
        "---",
        f"title: {app_name} 接口索引",
        "type: api-contract-index",
        "status: active",
        "tags:",
        "  - api",
        f"  - {app_name}",
        "  - api-contract-index",
        "created: 2026-06-18",
        "updated: 2026-06-18",
        f"summary: {app_name} 的接口 contract 快速定位入口。",
        "next_action: 使用时先通过本索引定位接口，再打开对应 contract 查看入参和出参。",
        "---",
        "",
        f"# {app_name} 接口索引",
        "",
        f"- appName：`{app_name}`",
        f"- 接口数：{total}",
        f"- 独立 contract 数：{len(contract_files)}",
        f"- 正式文档接口：{covered}",
        f"- 待正式文档确认：{pending}",
        f"- 模块数：{len(modules)}",
        "",
        "## 使用原则",
        "",
        "- 先通过接口用途、API symbol 或 path 在本页定位接口。",
        "- 再打开对应 contract 查看请求字段、响应字段和字段说明。",
        "- `正式文档` 表示接口结构来自项目接口文档。",
        "- `待正式文档确认` 表示已从项目用法提取出可用结构，后续拿到正式文档时需要校准。",
        "",
        "## 快速定位",
        "",
    ]

    for module in modules:
        module_rows = [row for row in rows if row["module"] == module]
        lines.extend(
            [
                f"### {module}",
                "",
                "| API symbol | Method | Path | 用途 | 入参 | 出参 | Contract | 文档状态 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in module_rows:
            contract = f"[{row['contract_file']}]({row['contract_file']})" if row["contract_file"] else ""
            lines.append(
                "| `{symbol}` | POST | `{path}` | {title} | {request_count} | {response_count} | {contract} | {status} |".format(
                    symbol=clean(row["symbol"]),
                    path=clean(row["path"]),
                    title=clean(row["title"]),
                    request_count=row["request_field_count"],
                    response_count=row["response_field_count"],
                    contract=contract,
                    status=clean(row["doc_status"]),
                )
            )
        lines.append("")

    lines.extend(
        [
            "## 待正式文档确认",
            "",
            "| API symbol | Path | 用途 | Contract |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in [item for item in rows if not item.get("official_doc_covered")]:
        contract = f"[{row['contract_file']}]({row['contract_file']})" if row["contract_file"] else ""
        lines.append(
            "| `{symbol}` | `{path}` | {title} | {contract} |".format(
                symbol=clean(row["symbol"]),
                path=clean(row["path"]),
                title=clean(row["title"]),
                contract=contract,
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--endpoint-index", required=True, type=Path)
    parser.add_argument("--contract-index", required=True, type=Path)
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--out-md", required=True, type=Path)
    parser.add_argument("--out-pending-jsonl", required=True, type=Path)
    args = parser.parse_args()

    rows = build_rows(
        read_jsonl(args.manifest),
        read_jsonl(args.endpoint_index),
        read_jsonl(args.contract_index),
    )
    write_markdown(rows, args.out_md, args.app_name, args.project_root)
    write_pending(rows, args.out_pending_jsonl)
    print(
        json.dumps(
            {
                "appName": args.app_name,
                "total": len(rows),
                "covered": len([row for row in rows if row.get("official_doc_covered")]),
                "project_extracted": len([row for row in rows if row.get("contract_source_type") == "project-extracted"]),
                "pending": len([row for row in rows if not row.get("official_doc_covered")]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
