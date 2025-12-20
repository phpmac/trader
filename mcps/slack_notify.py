#!/usr/bin/env python3
"""
Slack 通知 MCP 服务器

提供 Slack 通知功能:
- 发送消息到 Slack 频道 (通过 Webhook)
"""

import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 加载项目根目录的 .env 文件
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")

# 初始化 MCP 服务器
mcp = FastMCP[Any]("slack-notify")


class SendMessageInput(BaseModel):
    """发送消息输入"""

    text: str = Field(description="消息内容")
    username: str | None = Field(default=None, description="发送者名称 (可选)")
    icon_emoji: str | None = Field(
        default=None, description="发送者图标 emoji (可选, 如 :robot_face:)"
    )


class SendMessageResult(BaseModel):
    """发送消息结果"""

    success: bool = Field(description="是否发送成功")
    message: str = Field(description="结果说明")


def get_webhook_url() -> str:
    """获取 Slack Webhook URL"""
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        raise ValueError("环境变量 SLACK_WEBHOOK_URL 未设置")
    return url


@mcp.tool(name="slack_send_message")
def slack_send_message(params: SendMessageInput) -> SendMessageResult:
    """
    发送消息到 Slack 频道

    参数:
    - text: 消息内容 (支持 Slack 格式化语法)
    - username: 发送者名称 (可选)
    - icon_emoji: 发送者图标 (可选, 如 :robot_face:)

    返回:
    - success: 是否成功
    - message: 结果说明
    """
    webhook_url = get_webhook_url()

    # 构建 payload
    payload: dict[str, Any] = {"text": params.text}

    if params.username:
        payload["username"] = params.username

    if params.icon_emoji:
        payload["icon_emoji"] = params.icon_emoji

    # 发送请求
    with httpx.Client(timeout=10) as client:
        response = client.post(webhook_url, json=payload)

    if response.status_code == 200 and response.text == "ok":
        return SendMessageResult(success=True, message="消息发送成功")
    else:
        return SendMessageResult(
            success=False,
            message=f"发送失败: status={response.status_code}, body={response.text}",
        )


if __name__ == "__main__":
    mcp.run()
