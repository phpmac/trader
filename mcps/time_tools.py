#!/usr/bin/env python3
"""
时间工具 MCP 服务器

提供时间相关的工具:
- 获取当前 CST (中国标准时间) 时间
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 初始化 MCP 服务器
mcp = FastMCP[Any]("time_tools")

# 中国标准时间 (UTC+8)
CST = timezone(timedelta(hours=8))


class TimeInfo(BaseModel):
    """时间信息"""

    timestamp: int = Field(description="Unix 时间戳 (毫秒)")
    datetime_cst: str = Field(description="CST 时间字符串 (YYYY-MM-DD HH:MM:SS)")
    date: str = Field(description="日期 (YYYY-MM-DD)")
    time: str = Field(description="时间 (HH:MM:SS)")
    hour: int = Field(description="小时 (0-23)")
    minute: int = Field(description="分钟 (0-59)")
    weekday: int = Field(description="星期几 (0=周一, 6=周日)")
    weekday_name: str = Field(description="星期几名称")


def get_weekday_name(weekday: int) -> str:
    """获取星期几名称"""
    names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return names[weekday]


@mcp.tool(name="get_current_time")
def get_current_time() -> TimeInfo:
    """
    获取当前 CST (中国标准时间) 时间

    返回:
    - timestamp: Unix 时间戳 (毫秒)
    - datetime_cst: 完整时间字符串
    - date: 日期
    - time: 时间
    - hour/minute: 小时/分钟
    - weekday: 星期几 (0=周一)
    """
    now = datetime.now(CST)
    return TimeInfo(
        timestamp=int(now.timestamp() * 1000),
        datetime_cst=now.strftime("%Y-%m-%d %H:%M:%S"),
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
        hour=now.hour,
        minute=now.minute,
        weekday=now.weekday(),
        weekday_name=get_weekday_name(now.weekday()),
    )


if __name__ == "__main__":
    mcp.run()
