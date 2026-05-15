#!/usr/bin/env python3
"""
DeepSeek API 消费监控脚本

查询余额 + 可选阈值告警。
依赖: pip install requests

用法:
  ./deepseek-monitor.py                         # 只查余额
  ./deepseek-monitor.py --alert 10               # 余额低于 10 时退出码 2
  ./deepseek-monitor.py --track ~/.hermes/sessions  # 从 session 日志估算用量
"""

import os, sys, json
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=Warning, module="urllib3")

try:
    import requests
except ImportError:
    print("错误: 需要 requests 库，请执行: pip install requests")
    sys.exit(1)


def get_api_key() -> str:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY="):
                    key = line.split("=", 1)[1].strip("\"'")
                    return key
    print("错误: 未设置 DEEPSEEK_API_KEY")
    sys.exit(1)


def query_balance(api_key: str) -> dict:
    url = "https://api.deepseek.com/user/balance"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def track_usage(session_dir: str) -> dict:
    """从 Hermes session JSONL 文件中累计 token 用量。"""
    import glob

    stats = {"prompt_tokens": 0, "completion_tokens": 0, "cached_tokens": 0, "sessions": 0}

    for fpath in glob.glob(os.path.join(session_dir, "**", "*.jsonl"), recursive=True):
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                usage = msg.get("usage") or {}
                if not usage:
                    continue
                stats["prompt_tokens"] += usage.get("prompt_tokens", 0)
                stats["completion_tokens"] += usage.get("completion_tokens", 0)
                stats["cached_tokens"] += usage.get("prompt_cache_hit_tokens", 0)
                stats["sessions"] += 1

    return stats


def format_balance(data: dict) -> str:
    bi = data.get("balance_infos", [{}])[0]
    available = data.get("is_available", False)
    currency = bi.get("currency", "?")
    total = bi.get("total_balance", "?")
    granted = bi.get("granted_balance", "?")
    topped = bi.get("topped_up_balance", "?")

    status_icon = "✅ 可用" if available else "❌ 不可用"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "══════════════════════════════════════════",
        "  DeepSeek API 消费监控",
        "══════════════════════════════════════════",
        f"  状态:       {status_icon}",
        f"  总余额:     {total} {currency}",
        f"  充值余额:   {topped} {currency}",
        f"  赠金余额:   {granted} {currency}",
        f"  查询时间:   {now}",
        "──────────────────────────────────────────",
    ]

    return "\n".join(lines)


def format_usage(stats: dict) -> str:
    total = stats["prompt_tokens"] + stats["completion_tokens"]
    # deepseek-v4-flash 定价: $0.15/M input, $0.60/M output
    input_cost = stats["prompt_tokens"] * 0.15 / 1_000_000
    output_cost = stats["completion_tokens"] * 0.60 / 1_000_000

    lines = [
        "",
        "  ── Token 用量统计 ──",
        f"  扫描 session: {stats['sessions']} 条",
        f"  Prompt:      {stats['prompt_tokens']:,} tokens",
        f"  Completion:  {stats['completion_tokens']:,} tokens",
        f"  缓存命中:    {stats['cached_tokens']:,} tokens",
        f"  总计:        {total:,} tokens",
        f"  估算费用:    ~${input_cost:.4f} (input) + ~${output_cost:.4f} (output)",
    ]

    return "\n".join(lines)


def main():
    alert_threshold = None
    track_dir = None

    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg == "--alert" and args:
            alert_threshold = float(args.pop(0))
        elif arg == "--track" and args:
            track_dir = args.pop(0)
        else:
            print(f"未知参数: {arg}")
            sys.exit(1)

    api_key = get_api_key()

    # 查询余额
    try:
        data = query_balance(api_key)
    except requests.RequestException as e:
        print(f"错误: 无法查询 DeepSeek API — {e}")
        sys.exit(1)

    print(format_balance(data))

    # 累计用量（可选）
    if track_dir:
        if os.path.isdir(track_dir):
            stats = track_usage(track_dir)
            print(format_usage(stats))
        else:
            print(f"\n  用量目录不存在: {track_dir}")

    print("──────────────────────────────────────────")

    # 阈值告警
    if alert_threshold is not None:
        bi = data.get("balance_infos", [{}])[0]
        total = float(bi.get("total_balance", 0))
        currency = bi.get("currency", "?")
        if total < alert_threshold:
            print(f"  ⚠️  余额 ({total:.2f} {currency}) 低于阈值 ({alert_threshold:.2f} {currency})")
            sys.exit(2)
        else:
            print(f"  余额充足 ({total:.2f} {currency})")

    print("══════════════════════════════════════════")


if __name__ == "__main__":
    main()
