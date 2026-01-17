#!/usr/bin/env python3
"""
coinank MCP 集成测试

运行命令:
    uv run pytest tests/test_coinank.py -v -s

注意: 需要设置环境变量 COINANK_API_KEY
"""

import pytest

from mcps.coinank import (
    GetAggregatedCVDInput,
    GetCVDKlineInput,
    GetFundingRateKlineInput,
    GetKlinesInput,
    GetLargeMarketOrdersInput,
    GetLastPriceInput,
    GetLongShortPersonRatioInput,
    GetOpenInterestKlineInput,
    GetOpenInterestRankInput,
    GetPriceRankInput,
    GetRealTimeFundFlowInput,
    GetRSIMapInput,
    GetVolumeRankInput,
    coinank_get_aggregated_cvd,
    coinank_get_cvd_kline,
    coinank_get_funding_rate_kline,
    coinank_get_klines,
    coinank_get_large_market_orders,
    coinank_get_last_price,
    coinank_get_long_short_ratio,
    coinank_get_open_interest_kline,
    coinank_get_open_interest_rank,
    coinank_get_price_rank,
    coinank_get_realtime_fund_flow,
    coinank_get_rsi_map,
    coinank_get_volume_rank,
)


@pytest.mark.asyncio
async def test_get_last_price():
    """测试获取最新价格"""
    result = await coinank_get_last_price.fn(GetLastPriceInput(symbol="BTCUSDT"))
    print(f"\n最新价格:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_klines():
    """测试获取K线数据"""
    result = await coinank_get_klines.fn(GetKlinesInput(symbol="BTCUSDT", size=3))
    print(f"\nK线数据:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_open_interest_kline():
    """测试获取持仓量K线"""
    result = await coinank_get_open_interest_kline.fn(
        GetOpenInterestKlineInput(symbol="BTCUSDT", size=3)
    )
    print(f"\n持仓量K线:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_cvd_kline():
    """测试获取CVD K线"""
    result = await coinank_get_cvd_kline.fn(GetCVDKlineInput(symbol="BTCUSDT", size=3))
    print(f"\nCVD K线:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_aggregated_cvd():
    """测试获取聚合CVD"""
    result = await coinank_get_aggregated_cvd.fn(
        GetAggregatedCVDInput(baseCoin="BTC", size=3)
    )
    print(f"\n聚合CVD:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_realtime_fund_flow():
    """测试获取实时资金流"""
    result = await coinank_get_realtime_fund_flow.fn(GetRealTimeFundFlowInput(size=5))
    print(f"\n实时资金流:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_funding_rate_kline():
    """测试获取资金费率K线"""
    result = await coinank_get_funding_rate_kline.fn(
        GetFundingRateKlineInput(symbol="BTCUSDT", size=3)
    )
    print(f"\n资金费率K线:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_long_short_ratio():
    """测试获取多空比"""
    result = await coinank_get_long_short_ratio.fn(
        GetLongShortPersonRatioInput(symbol="BTCUSDT", size=3)
    )
    print(f"\n多空比:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_rsi_map():
    """测试获取RSI选币器"""
    result = await coinank_get_rsi_map.fn(GetRSIMapInput(lowest=3, highest=3))
    print(f"\nRSI选币器:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_large_market_orders():
    """测试获取大额市价订单"""
    result = await coinank_get_large_market_orders.fn(
        GetLargeMarketOrdersInput(symbol="BTCUSDT", size=5)
    )
    print(f"\n大额市价订单:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_open_interest_rank():
    """测试获取持仓排行榜"""
    result = await coinank_get_open_interest_rank.fn(GetOpenInterestRankInput(size=5))
    print(f"\n持仓排行榜:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_volume_rank():
    """测试获取交易量排行榜"""
    result = await coinank_get_volume_rank.fn(GetVolumeRankInput(size=5))
    print(f"\n交易量排行榜:\n{result}")
    assert "Error" not in result


@pytest.mark.asyncio
async def test_get_price_rank():
    """测试获取价格变化排行榜"""
    result = await coinank_get_price_rank.fn(GetPriceRankInput(size=5))
    print(f"\n价格变化排行榜:\n{result}")
    assert "Error" not in result
