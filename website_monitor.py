#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""网站可用性监听脚本。

功能说明：
1. 每 10 分钟轮询一次配置的网站。
2. 单次请求超时时间为 10 秒。
3. 当网站访问异常时，通过飞书机器人发送告警消息。
4. 首次异常立即推送，持续异常时每隔 30 分钟重复推送一次。
5. 网站恢复正常时不发送通知。
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from urllib import error, request


CHECK_INTERVAL_SECONDS = 600
REQUEST_TIMEOUT_SECONDS = 10
ALERT_INTERVAL_SECONDS = 1800
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/2b72b20a-0f76-437b-b577-bdf2463d2f25"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "monitor_config.json")
STATE_FILE = os.path.join(BASE_DIR, "monitor_state.json")


class MonitorTarget:
    """定义单个监控目标。"""

    def __init__(self, app_name: str, url: str) -> None:
        """初始化单个监控目标。"""

        self.app_name = app_name
        self.url = url


def setup_logging() -> None:
    """初始化日志配置，便于在控制台查看巡检结果。"""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def build_request(url: str) -> request.Request:
    """构造 HTTP 请求对象，附带常见请求头以提高兼容性。"""

    return request.Request(
        url=url,
        method="GET",
        headers={
            "User-Agent": "WebsiteMonitor/1.0",
            "Accept": "*/*",
        },
    )


def load_monitors(config_path: str) -> List[MonitorTarget]:
    """从 JSON 配置文件加载监控目标列表。"""

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"未找到配置文件: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        raw_config = json.load(file)

    if not isinstance(raw_config, list) or not raw_config:
        raise ValueError("配置文件内容必须是非空数组。")

    monitors: List[MonitorTarget] = []
    for item in raw_config:
        if not isinstance(item, dict):
            raise ValueError("配置项必须是对象。")

        app_name = str(item.get("app_name", "")).strip()
        url = str(item.get("url", "")).strip()

        if not app_name or not url:
            raise ValueError(f"配置项缺少必要字段: {item}")

        monitors.append(MonitorTarget(app_name=app_name, url=url))

    return monitors


def parse_args() -> argparse.Namespace:
    """解析命令行参数，默认执行单次巡检，适配定时任务。"""

    parser = argparse.ArgumentParser(description="网站可用性监听脚本")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="启用常驻循环模式；未传入时默认只执行一轮，适合宝塔定时任务。",
    )
    return parser.parse_args()


def load_state(state_path: str) -> Dict[str, Dict[str, Union[float, bool]]]:
    """从本地状态文件加载上次巡检结果，用于跨进程保留告警节奏。"""

    if not os.path.exists(state_path):
        return {}

    try:
        with open(state_path, "r", encoding="utf-8") as file:
            state = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        logging.warning("读取状态文件失败，将按首次启动处理: %s", exc)
        return {}

    if not isinstance(state, dict):
        return {}

    return state


def save_state(state_path: str, state: Dict[str, Dict[str, Union[float, bool]]]) -> None:
    """将当前巡检状态写入本地文件，供下次定时任务继续使用。"""

    with open(state_path, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)


def check_website(target: MonitorTarget) -> Tuple[bool, str]:
    """检查单个网站是否可访问，并返回检查结果与描述信息。"""

    req = build_request(target.url)
    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            status_code = response.getcode()
            if 200 <= status_code < 400:
                return True, f"HTTP {status_code}"
            return False, f"HTTP {status_code}"
    except error.HTTPError as exc:
        return False, f"HTTPError {exc.code}: {exc.reason}"
    except error.URLError as exc:
        return False, f"URLError: {exc.reason}"
    except TimeoutError:
        return False, f"Timeout: 超过 {REQUEST_TIMEOUT_SECONDS} 秒未响应"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def format_alert_text(target: MonitorTarget, status_text: str) -> str:
    """生成飞书异常告警文本，仅说明对应应用与网址。"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"[网站异常告警]\n"
        f"时间: {now}\n"
        f"网页: {target.app_name}\n"
        f"网址: {target.url}\n"
        f"异常: {status_text}"
    )


def send_feishu_message(text: str) -> bool:
    """调用飞书机器人 webhook 发送文本消息。"""

    payload = json.dumps(
        {
            "msg_type": "text",
            "content": {
                "text": text,
            },
        }
    ).encode("utf-8")

    req = request.Request(
        url=FEISHU_WEBHOOK,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
    )

    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8", errors="replace")
            logging.info("飞书推送成功: %s", body)
            return True
    except Exception as exc:  # noqa: BLE001
        logging.error("飞书推送失败: %s", exc)
        return False


def handle_status_change(
    target: MonitorTarget,
    is_ok: bool,
    status_text: str,
    previous_status: Optional[bool],
    alert_time_map: Dict[str, float],
) -> None:
    """在首次异常或异常持续超过告警间隔时推送飞书消息。"""

    if is_ok:
        alert_time_map.pop(target.url, None)
        return

    now = time.time()
    last_alert_time = alert_time_map.get(target.url)

    if previous_status is not False or last_alert_time is None:
        message = format_alert_text(target, status_text)
        if send_feishu_message(message):
            alert_time_map[target.url] = now
        return

    if now - last_alert_time >= ALERT_INTERVAL_SECONDS:
        message = format_alert_text(target, status_text)
        if send_feishu_message(message):
            alert_time_map[target.url] = now


def sync_state_from_record(
    monitors: List[MonitorTarget],
    state: Dict[str, Dict[str, Union[float, bool]]],
) -> Tuple[Dict[str, bool], Dict[str, float]]:
    """从持久化状态中恢复状态映射，仅保留当前配置内的监控项。"""

    status_map: Dict[str, bool] = {}
    alert_time_map: Dict[str, float] = {}

    for target in monitors:
        record = state.get(target.url, {})
        is_ok = record.get("is_ok")
        last_alert_time = record.get("last_alert_time")

        if isinstance(is_ok, bool):
            status_map[target.url] = is_ok
        if isinstance(last_alert_time, (int, float)):
            alert_time_map[target.url] = float(last_alert_time)

    return status_map, alert_time_map


def build_state_record(
    monitors: List[MonitorTarget],
    status_map: Dict[str, bool],
    alert_time_map: Dict[str, float],
) -> Dict[str, Dict[str, Union[float, bool]]]:
    """将当前状态映射转换为可持久化的字典结构。"""

    state: Dict[str, Dict[str, Union[float, bool]]] = {}
    for target in monitors:
        state[target.url] = {
            "is_ok": status_map.get(target.url, True),
            "last_alert_time": alert_time_map.get(target.url, 0.0),
        }
    return state


def run_once(
    monitors: List[MonitorTarget],
    status_map: Dict[str, bool],
    alert_time_map: Dict[str, float],
) -> None:
    """执行一轮巡检，并按状态变化触发通知。"""

    for target in monitors:
        is_ok, status_text = check_website(target)
        previous_status = status_map.get(target.url)
        status_map[target.url] = is_ok

        if is_ok:
            logging.info("检查正常 | 应用=%s | 网址=%s | %s", target.app_name, target.url, status_text)
        else:
            logging.warning("检查异常 | 应用=%s | 网址=%s | %s", target.app_name, target.url, status_text)

        handle_status_change(target, is_ok, status_text, previous_status, alert_time_map)


def main() -> None:
    """启动网站监听任务，默认单次执行，可选循环模式。"""

    args = parse_args()
    setup_logging()
    monitors = load_monitors(CONFIG_FILE)
    state = load_state(STATE_FILE)
    status_map, alert_time_map = sync_state_from_record(monitors, state)

    if args.loop:
        logging.info("网站监听启动，模式=循环，监控数量: %s，轮询间隔: %s 秒", len(monitors), CHECK_INTERVAL_SECONDS)
        while True:
            run_once(monitors, status_map, alert_time_map)
            save_state(STATE_FILE, build_state_record(monitors, status_map, alert_time_map))
            time.sleep(CHECK_INTERVAL_SECONDS)
    else:
        logging.info("网站监听启动，模式=单次，监控数量: %s", len(monitors))
        run_once(monitors, status_map, alert_time_map)
        save_state(STATE_FILE, build_state_record(monitors, status_map, alert_time_map))


if __name__ == "__main__":
    main()
