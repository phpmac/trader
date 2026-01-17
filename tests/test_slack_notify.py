#!/usr/bin/env python3
"""
slack_notify MCP 集成测试

运行命令:
    uv run pytest tests/test_slack_notify.py -v -s

注意: 需要设置环境变量 SLACK_WEBHOOK_URL
"""

import pytest

from mcps.slack_notify import slack_send_message


# @pytest.mark.skip(reason="需要手动运行, 避免频繁发送消息")
def test_slack_send_message():
    """测试发送 Slack 消息"""
    result = slack_send_message.fn(
        text="[测试] MCP 单元测试消息",
        username="TestBot",
        icon_emoji=":test_tube:",
    )
    print(f"\n发送结果: {result}")
    assert result.success is True
