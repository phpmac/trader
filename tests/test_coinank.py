#!/usr/bin/env python3
"""
coinank MCP 集成测试

运行命令:
    uv run pytest tests/test_coinank.py -v -s
    uv run pytest tests/test_coinank.py::test_get_rsi_map -v -s

注意: 需要设置环境变量 COINANK_API_KEY
"""

import pytest
from fastmcp import Client

from mcps.coinank import mcp


@pytest.fixture
async def client():
    """创建 FastMCP 测试客户端"""
    async with Client(mcp) as c:
        yield c


@pytest.mark.asyncio
async def test_get_last_price(client: Client):
    """测试获取最新价格"""
    result = await client.call_tool("coinank_get_last_price", {"symbol": "BTCUSDT"})
    print(f"\n最新价格:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_klines(client: Client):
    """测试获取K线数据"""
    result = await client.call_tool(
        "coinank_get_klines", {"symbol": "BTCUSDT", "size": 3}
    )
    print(f"\nK线数据:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_open_interest_kline(client: Client):
    """测试获取持仓量K线"""
    result = await client.call_tool(
        "coinank_get_open_interest_kline", {"symbol": "BTCUSDT", "size": 3}
    )
    print(f"\n持仓量K线:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_cvd_kline(client: Client):
    """测试获取CVD K线"""
    result = await client.call_tool(
        "coinank_get_cvd_kline", {"symbol": "BTCUSDT", "size": 3}
    )
    print(f"\nCVD K线:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_aggregated_cvd(client: Client):
    """测试获取聚合CVD"""
    result = await client.call_tool(
        "coinank_get_aggregated_cvd", {"baseCoin": "BTC", "size": 3}
    )
    print(f"\n聚合CVD:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_realtime_fund_flow(client: Client):
    """测试获取实时资金流"""
    result = await client.call_tool("coinank_get_realtime_fund_flow", {"size": 5})
    print(f"\n实时资金流:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_funding_rate_kline(client: Client):
    """测试获取资金费率K线"""
    result = await client.call_tool(
        "coinank_get_funding_rate_kline", {"symbol": "BTCUSDT", "size": 3}
    )
    print(f"\n资金费率K线:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_long_short_ratio(client: Client):
    """测试获取多空比"""
    result = await client.call_tool(
        "coinank_get_long_short_ratio", {"symbol": "BTCUSDT", "size": 3}
    )
    print(f"\n多空比:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_rsi_map(client: Client):
    """测试获取RSI选币器"""
    result = await client.call_tool("coinank_get_rsi_map", {"lowest": 3, "highest": 3})
    print(f"\nRSI选币器:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_large_market_orders(client: Client):
    """测试获取大额市价订单"""
    result = await client.call_tool(
        "coinank_get_large_market_orders", {"symbol": "BTCUSDT", "size": 5}
    )
    print(f"\n大额市价订单:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_open_interest_rank(client: Client):
    """测试获取持仓排行榜"""
    result = await client.call_tool("coinank_get_open_interest_rank", {"size": 5})
    print(f"\n持仓排行榜:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_volume_rank(client: Client):
    """测试获取交易量排行榜"""
    result = await client.call_tool("coinank_get_volume_rank", {"size": 5})
    print(f"\n交易量排行榜:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text


@pytest.mark.asyncio
async def test_get_price_rank(client: Client):
    """测试获取价格变化排行榜"""
    result = await client.call_tool("coinank_get_price_rank", {"size": 5})
    print(f"\n价格变化排行榜:\n{result.content[0].text}")
    assert "Error" not in result.content[0].text
