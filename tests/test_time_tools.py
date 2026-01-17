#!/usr/bin/env python3
"""
time_tools MCP 集成测试

运行命令:
    uv run pytest tests/test_time_tools.py -v -s
"""

from mcps.time_tools import get_current_time


def test_get_current_time():
    """测试获取当前时间"""
    # 调用原始函数 (被 @mcp.tool 装饰后需要用 .fn)
    result = get_current_time.fn()
    print(f"\n当前时间: {result.datetime_cst}")
    print(f"时间戳: {result.timestamp}")
    print(f"日期: {result.date}")
    print(f"时间: {result.time}")
    print(f"星期: {result.weekday_name}")

    assert result.timestamp > 0
    assert 0 <= result.hour <= 23
