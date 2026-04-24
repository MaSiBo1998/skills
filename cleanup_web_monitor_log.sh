#!/bin/bash

set -euo pipefail

LOG_FILE="${1:-/www/wwwlogs/web-monitor.log}"
ARCHIVE_DIR="${2:-/www/wwwlogs/web-monitor-archive}"
KEEP_DAYS="${KEEP_DAYS:-3}"

# 函数说明：确保日志文件和归档目录存在，避免后续操作失败。
ensure_paths() {
  mkdir -p "$ARCHIVE_DIR"

  if [ ! -f "$LOG_FILE" ]; then
    mkdir -p "$(dirname "$LOG_FILE")"
    : > "$LOG_FILE"
  fi
}

# 函数说明：将当前日志按时间归档，再安全清空原日志文件。
archive_and_truncate_log() {
  local timestamp archive_file
  timestamp="$(date '+%Y%m%d_%H%M%S')"
  archive_file="$ARCHIVE_DIR/web-monitor-$timestamp.log"

  if [ -s "$LOG_FILE" ]; then
    cp "$LOG_FILE" "$archive_file"
  fi

  : > "$LOG_FILE"
}

# 函数说明：删除超过保留天数的历史归档日志，控制磁盘占用。
cleanup_old_archives() {
  find "$ARCHIVE_DIR" -type f -name 'web-monitor-*.log' -mtime +"$KEEP_DAYS" -delete
}

# 函数说明：串联执行日志清理流程并输出执行结果。
main() {
  ensure_paths
  archive_and_truncate_log
  cleanup_old_archives

  echo "[$(date '+%F %T')] web-monitor 日志清理完成: $LOG_FILE"
}

main "$@"
