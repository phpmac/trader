#!/usr/bin/env python3
"""
Coinank MCP 服务器

提供 Coinank 交易数据 API 的 MCP 工具集, 包括:
- 实时价格查询
- 持仓量K线数据
- CVD (累积成交量差) 数据
- 资金流向数据
- 资金费率K线
- 多空持仓人数比
- RSI选币器
- 大额订单数据
- 排行榜数据 (持仓/交易量/价格变化)
- K线数据
"""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# 加载项目根目录的 .env 文件
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")

# 初始化 MCP 服务器
mcp = FastMCP[Any]("coinank_mcp")

# API 配置
COINANK_API_BASE = "https://open-api.coinank.com/api"


# ============ 枚举定义 ============


class Exchange(str, Enum):
    """交易所"""

    BINANCE = "Binance"
    BYBIT = "Bybit"


class ProductType(str, Enum):
    """产品类型"""

    SPOT = "SPOT"
    SWAP = "SWAP"


class ExchangeType(str, Enum):
    """交易所类型"""

    SWAP = "SWAP"  # 永续合约
    SPOT = "SPOT"  # 现货
    FUTURES = "FUTURES"  # 交割


class Interval(str, Enum):
    """K线时间间隔"""

    MINUTE_1 = "1m"
    MINUTE_3 = "3m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_6 = "6h"
    HOUR_8 = "8h"
    HOUR_12 = "12h"
    DAY_1 = "1d"


class RSIInterval(str, Enum):
    """RSI时间间隔"""

    HOUR_1 = "1H"
    HOUR_4 = "4H"
    HOUR_8 = "8H"
    HOUR_24 = "24H"


class SortType(str, Enum):
    """排序类型"""

    ASC = "asc"
    DESC = "desc"


class FundSortBy(str, Enum):
    """资金流排序字段"""

    M5 = "m5net"
    M15 = "m15net"
    M30 = "m30net"
    H1 = "h1net"
    H2 = "h2net"
    H4 = "h4net"
    H6 = "h6net"
    H8 = "h8net"
    H12 = "h12net"
    D1 = "d1net"
    D2 = "d2net"
    D3 = "d3net"
    D5 = "d5net"
    D7 = "d7net"
    D30 = "d30net"


class PriceRankSortBy(str, Enum):
    """价格排行筛选字段"""

    PRICE_CHANGE_H24 = "priceChangeH24"
    PRICE_CHANGE_M5 = "priceChangeM5"
    PRICE_CHANGE_M15 = "priceChangeM15"
    PRICE_CHANGE_M30 = "priceChangeM30"
    PRICE_CHANGE_H1 = "priceChangeH1"
    PRICE_CHANGE_H2 = "priceChangeH2"
    PRICE_CHANGE_H4 = "priceChangeH4"
    PRICE_CHANGE_H6 = "priceChangeH6"
    PRICE_CHANGE_H8 = "priceChangeH8"
    PRICE_CHANGE_H12 = "priceChangeH12"


class OrderSide(str, Enum):
    """订单方向"""

    BUY = "bid"
    SELL = "ask"


# ============ Pydantic 输入模型 ============


class GetLastPriceInput(BaseModel):
    """获取最新价格输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    )


class GetOpenInterestKlineInput(BaseModel):
    """获取持仓量K线输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    symbol: str = Field(..., description="交易对")
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期")
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    )
    size: int = Field(default=1, description="返回数据数量")


class GetCVDKlineInput(BaseModel):
    """获取CVD K线输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    symbol: str = Field(..., description="交易对")
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期")
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    )
    size: int = Field(default=1, description="返回数据数量")
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    )


class GetAggregatedCVDInput(BaseModel):
    """获取聚合CVD输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    base_coin: str = Field(..., description="币种, 如 BTC", alias="baseCoin")
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期")
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    )
    size: int = Field(default=1, description="返回数据数量")
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    )


class GetRealTimeFundFlowInput(BaseModel):
    """获取实时资金流入流出输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    )
    base_coin: Optional[str] = Field(
        default=None, description="加密货币", alias="baseCoin"
    )
    page: int = Field(default=1, description="当前页")
    size: int = Field(default=10, description="每页大小")
    sort_by: FundSortBy = Field(
        default=FundSortBy.H1, description="排序字段", alias="sortBy"
    )
    sort_type: SortType = Field(
        default=SortType.DESC, description="排序类型", alias="sortType"
    )


class GetFundingRateKlineInput(BaseModel):
    """获取资金费率K线输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    symbol: Optional[str] = Field(default=None, description="交易对")
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期")
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    )
    size: int = Field(default=1, description="返回数据数量")


class GetLongShortPersonRatioInput(BaseModel):
    """获取多空持仓人数比输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    symbol: Optional[str] = Field(default=None, description="交易对")
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期")
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    )
    size: int = Field(default=1, description="返回数据数量")


class GetRSIMapInput(BaseModel):
    """获取RSI选币器输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    interval: RSIInterval = Field(default=RSIInterval.HOUR_1, description="时间周期")
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    lowest: int = Field(default=5, description="筛选最低RSI数量")
    highest: int = Field(default=5, description="筛选最高RSI数量")


class GetLargeMarketOrdersInput(BaseModel):
    """获取大额市价订单输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    symbol: str = Field(..., description="交易对")
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    )
    amount: int = Field(default=100000, description="查询的最小金额")
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    )
    size: int = Field(default=10, description="返回数据数量")


class GetLargeLimitOrdersInput(BaseModel):
    """获取大额限价订单输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    symbol: str = Field(..., description="交易对")
    exchange_type: ExchangeType = Field(
        default=ExchangeType.SWAP, description="交易所类型", alias="exchangeType"
    )
    amount: int = Field(default=100000, description="查询的最小金额")
    side: OrderSide = Field(default=OrderSide.BUY, description="订单方向")
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    start_time: Optional[int] = Field(
        default=None, description="开始时间(时间戳毫秒)", alias="startTime"
    )
    size: int = Field(default=10, description="返回数据数量")
    is_history: bool = Field(
        default=False, description="是否查询历史数据", alias="isHistory"
    )


class GetOpenInterestRankInput(BaseModel):
    """获取持仓排行榜输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    page: int = Field(default=1, description="页码")
    size: int = Field(default=50, description="每页大小")
    sort_by: str = Field(default="openInterest", description="排序字段", alias="sortBy")
    sort_type: SortType = Field(
        default=SortType.DESC, description="排序类型", alias="sortType"
    )


class GetVolumeRankInput(BaseModel):
    """获取交易量变化排行榜输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    sort_by: Optional[str] = Field(default=None, description="排序字段", alias="sortBy")
    sort_type: SortType = Field(
        default=SortType.DESC, description="排序类型", alias="sortType"
    )
    size: int = Field(default=3, description="返回数据数量")
    page: int = Field(default=1, description="页码")


class GetPriceRankInput(BaseModel):
    """获取价格变化排行榜输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    sort_by: PriceRankSortBy = Field(
        default=PriceRankSortBy.PRICE_CHANGE_H24,
        description="排序字段",
        alias="sortBy",
    )
    sort_type: SortType = Field(
        default=SortType.DESC,
        description="排序类型, desc为涨, asc为跌",
        alias="sortType",
    )
    size: int = Field(default=10, description="返回数据数量")
    page: int = Field(default=1, description="页码")
    only_binance: bool = Field(
        default=True, description="是否只返回币安数据", alias="onlyBinance"
    )


class GetKlinesInput(BaseModel):
    """获取K线数据输入"""

    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", populate_by_name=True
    )

    symbol: Optional[str] = Field(default=None, description="交易对")
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所")
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    )
    size: int = Field(default=1, description="返回数据数量")
    interval: Interval = Field(default=Interval.MINUTE_15, description="K线时间间隔")
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    )


# ============ API 客户端 ============


def _get_api_key() -> str:
    """获取 API Key"""
    api_key = os.environ.get("COINANK_API_KEY")
    if not api_key:
        raise ValueError("环境变量 COINANK_API_KEY 未设置")
    return api_key


def _get_current_timestamp_ms() -> int:
    """获取当前时间戳(毫秒)"""
    return int(datetime.now().timestamp() * 1000)


async def _coinank_request(endpoint: str, params: dict[str, Any] | None = None) -> Any:
    """发起 Coinank API 请求"""
    api_key = _get_api_key()

    # 过滤 None 值
    if params:
        params = {k: v for k, v in params.items() if v is not None}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{COINANK_API_BASE}{endpoint}",
            params=params,
            headers={
                "apikey": api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        result = response.json()

    # 处理响应格式
    data = result.get("data")
    if data is None:
        raise ValueError(result.get("msg", "请求不到数据, 请检查参数"))

    # API 响应格式:
    # 1. 嵌套格式 (分页数据): {"data": {"data": [...], "pagination": {...}}}
    #    或 {"data": {"list": [...], "pagination": {...}}}
    # 2. 直接格式 (数组): {"data": [...]}
    # 3. 直接格式 (对象): {"data": {...}}
    if isinstance(data, list):
        # 直接返回数组数据
        return data
    elif isinstance(data, dict):
        # 检查是否是嵌套格式
        if "data" in data:
            return data["data"]
        elif "list" in data:
            # 分页格式, 返回整个对象 (包含 list 和 pagination)
            return data
        else:
            # 直接对象格式
            return data
    else:
        raise ValueError(f"无效的API响应格式: {json.dumps(result)}")


def _handle_api_error(e: Exception) -> str:
    """统一错误处理"""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        error_messages = {
            400: "请求参数错误, 请检查参数是否正确",
            401: "API 认证失败, 请检查 COINANK_API_KEY",
            403: "权限不足",
            429: "请求频率过高, 请稍后重试",
            500: "服务器错误, 请稍后重试",
        }
        return f"Error: {error_messages.get(status, f'API 请求失败, 状态码 {status}')}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: 请求超时, 请重试"
    elif isinstance(e, ValueError):
        return f"Error: {str(e)}"
    return f"Error: {type(e).__name__}: {str(e)}"


# ============ 辅助函数 ============


def filter_rsi_map(
    rsi_map: list[list[str]], lowest: int = 5, highest: int = 5
) -> dict[str, list[dict[str, Any]]]:
    """
    从RSI数据中筛选出最高和最低的币种

    Args:
        rsi_map: RSI数据 [[symbol, rsi], ...]
        lowest: 筛选最低RSI数量
        highest: 筛选最高RSI数量

    Returns:
        包含 lowest 和 highest 列表的字典
    """
    data = [{"symbol": item[0], "rsi": float(item[1])} for item in rsi_map]
    sorted_data = sorted(data, key=lambda x: x["rsi"])

    return {
        "lowest": sorted_data[:lowest],
        "highest": list(reversed(sorted_data[-highest:])),
    }


# ============ MCP 工具定义 ============


@mcp.tool(
    name="coinank_get_last_price",
    annotations={
        "title": "获取最新价格",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_last_price(
    symbol: Optional[str] = Field(default=None, description="交易对, 如 BTCUSDT"),
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    ),
) -> str:
    """
    获取指定加密货币交易对的最新价格信息

    返回字段:
    - lastPrice: 最新价
    - high24h: 24小时最高价
    - low24h: 24小时最低价
    - priceChange24h: 24小时涨跌幅 (0.0001 = 0.0001%)
    - volCcy24h: 24小时交易量
    - fundingRate: 资金费率
    - markPrice: 标记价格
    """
    if symbol is None:
        raise ValueError("symbol 必须提供")
    try:
        result = await _coinank_request(
            "/instruments/getLastPrice",
            {
                "symbol": symbol,
                "exchange": exchange.value,
                "productType": product_type.value,
            },
        )
        # 移除 open24h 字段
        if isinstance(result, dict) and "open24h" in result:
            del result["open24h"]
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_open_interest_kline",
    annotations={
        "title": "获取持仓量K线数据",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_open_interest_kline(
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    symbol: Optional[str] = Field(default=None, description="交易对"),
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期"),
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    ),
    size: int = Field(default=1, description="返回数据数量"),
) -> str:
    """
    获取交易对持仓量K线数据

    返回字段:
    - begin: 开始时间
    - open: 开盘持仓量
    - close: 收盘持仓量
    - low: 最低持仓量
    - high: 最高持仓量
    """
    if symbol is None:
        raise ValueError("symbol 必须提供")
    try:
        result = await _coinank_request(
            "/openInterest/kline",
            {
                "exchange": exchange.value,
                "symbol": symbol,
                "interval": interval.value,
                "endTime": end_time or _get_current_timestamp_ms(),
                "size": size,
            },
        )
        # 只保留关键字段
        filtered = [
            {
                "begin": item["begin"],
                "open": item["open"],
                "close": item["close"],
                "low": item["low"],
                "high": item["high"],
            }
            for item in result
        ]
        return json.dumps(filtered, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_cvd_kline",
    annotations={
        "title": "获取CVD K线数据",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_cvd_kline(
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    symbol: Optional[str] = Field(default=None, description="交易对"),
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期"),
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    ),
    size: int = Field(default=1, description="返回数据数量"),
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    ),
) -> str:
    """
    获取CVD (Cumulative Volume Delta) K线数据

    CVD 反映买卖力量对比:
    - 正值: 买方力量强
    - 负值: 卖方力量强

    返回数组格式: [timestamp, buyVolume, sellVolume, netVolume]
    """
    if symbol is None:
        raise ValueError("symbol 必须提供")
    try:
        result = await _coinank_request(
            "/marketOrder/getCvd",
            {
                "exchange": exchange.value,
                "symbol": symbol,
                "interval": interval.value,
                "endTime": end_time or _get_current_timestamp_ms(),
                "size": size,
                "productType": product_type.value,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_aggregated_cvd",
    annotations={
        "title": "获取聚合CVD数据",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_aggregated_cvd(
    base_coin: Optional[str] = Field(
        default=None, description="币种, 如 BTC", alias="baseCoin"
    ),
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期"),
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    ),
    size: int = Field(default=1, description="返回数据数量"),
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    ),
) -> str:
    """
    获取指定币种的聚合CVD数据 (跨交易所汇总)

    返回数组格式: [timestamp, buyVolume, sellVolume, netVolume]
    """
    if base_coin is None:
        raise ValueError("baseCoin 必须提供")
    try:
        result = await _coinank_request(
            "/marketOrder/getAggCvd",
            {
                "baseCoin": base_coin,
                "interval": interval.value,
                "endTime": end_time or _get_current_timestamp_ms(),
                "size": size,
                "productType": product_type.value,
                "exchanges": "",  # API要求必须传空字符串
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_realtime_fund_flow",
    annotations={
        "title": "获取实时资金流入流出",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_realtime_fund_flow(
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    ),
    base_coin: Optional[str] = Field(
        default=None, description="加密货币", alias="baseCoin"
    ),
    page: int = Field(default=1, description="当前页"),
    size: int = Field(default=10, description="每页大小"),
    sort_by: FundSortBy = Field(
        default=FundSortBy.H1, description="排序字段", alias="sortBy"
    ),
    sort_type: SortType = Field(
        default=SortType.DESC, description="排序类型", alias="sortType"
    ),
) -> str:
    """
    获取实时资金流入流出数据

    返回字段:
    - baseCoin: 币种
    - m5net/m15net/h1net等: 不同时间段净流入 (正值流入, 负值流出)
    """
    try:
        result = await _coinank_request(
            "/fund/fundReal",
            {
                "productType": product_type.value,
                "baseCoin": base_coin,
                "page": page,
                "size": size,
                "sortBy": sort_by.value,
                "sortType": sort_type.value,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_funding_rate_kline",
    annotations={
        "title": "获取资金费率K线",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_funding_rate_kline(
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    symbol: Optional[str] = Field(default=None, description="交易对"),
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期"),
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    ),
    size: int = Field(default=1, description="返回数据数量"),
) -> str:
    """
    获取交易对资金费率K线数据

    返回字段:
    - begin: 开始时间
    - open/close/low/high: 资金费率OHLC
    """
    try:
        result = await _coinank_request(
            "/fundingRate/kline",
            {
                "exchange": exchange.value,
                "symbol": symbol,
                "interval": interval.value,
                "endTime": end_time or _get_current_timestamp_ms(),
                "size": size,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_long_short_ratio",
    annotations={
        "title": "获取多空持仓人数比",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_long_short_ratio(
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    symbol: Optional[str] = Field(default=None, description="交易对"),
    interval: Interval = Field(default=Interval.MINUTE_15, description="时间周期"),
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    ),
    size: int = Field(default=1, description="返回数据数量"),
) -> str:
    """
    获取多空持仓人数比数据 (支持 Binance, OKX, Bybit)

    返回字段:
    - tss: 时间戳数组
    - longShortRatio: 多空比数组 (>1 多头人数多, <1 空头人数多)
    """
    try:
        result = await _coinank_request(
            "/longshort/person",
            {
                "exchange": exchange.value,
                "symbol": symbol,
                "interval": interval.value,
                "endTime": end_time or _get_current_timestamp_ms(),
                "size": size,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_rsi_map",
    annotations={
        "title": "RSI选币器",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_rsi_map(
    interval: RSIInterval = Field(default=RSIInterval.HOUR_1, description="时间周期"),
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    lowest: int = Field(default=5, description="筛选最低RSI数量"),
    highest: int = Field(default=5, description="筛选最高RSI数量"),
) -> str:
    """
    RSI选币器 - 筛选RSI最高和最低的币种

    RSI解读:
    - RSI < 30: 超卖区域, 可能反弹
    - RSI > 70: 超买区域, 可能回调

    返回:
    - lowest: RSI最低的币种列表
    - highest: RSI最高的币种列表
    """
    try:
        result = await _coinank_request(
            "/rsiMap/list",
            {
                "interval": interval.value,
                "exchange": exchange.value,
            },
        )
        filtered = filter_rsi_map(result["rsiMap"], lowest, highest)
        return json.dumps(filtered, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_large_market_orders",
    annotations={
        "title": "获取大额市价订单",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_large_market_orders(
    symbol: Optional[str] = Field(default=None, description="交易对"),
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    ),
    amount: int = Field(default=100000, description="查询的最小金额"),
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    ),
    size: int = Field(default=10, description="返回数据数量"),
) -> str:
    """
    获取大额市价订单数据

    返回字段:
    - side: 方向 (buy/sell)
    - price: 成交价格
    - tradeTurnover: 成交金额
    - ts: 时间戳
    """
    if symbol is None:
        raise ValueError("symbol 必须提供")
    params = GetLargeMarketOrdersInput(
        symbol=symbol,
        product_type=product_type,
        amount=amount,
        end_time=end_time,
        size=size,
    )
    try:
        result = await _coinank_request(
            "/trades/largeTrades",
            {
                "symbol": params.symbol,
                "productType": params.product_type.value,
                "amount": params.amount,
                "endTime": params.end_time or _get_current_timestamp_ms(),
                "size": params.size,
            },
        )
        # 只保留关键字段
        filtered = [
            {
                "side": item["side"],
                "price": item["price"],
                "tradeTurnover": item["tradeTurnover"],
                "ts": item["ts"],
            }
            for item in result
        ]
        return json.dumps(filtered, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_large_limit_orders",
    annotations={
        "title": "获取大额限价订单",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_large_limit_orders(
    symbol: Optional[str] = Field(default=None, description="交易对"),
    exchange_type: ExchangeType = Field(
        default=ExchangeType.SWAP, description="交易所类型", alias="exchangeType"
    ),
    amount: int = Field(default=100000, description="查询的最小金额"),
    side: OrderSide = Field(default=OrderSide.BUY, description="订单方向"),
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    start_time: Optional[int] = Field(
        default=None, description="开始时间(时间戳毫秒)", alias="startTime"
    ),
    size: int = Field(default=10, description="返回数据数量"),
    is_history: bool = Field(
        default=False, description="是否查询历史数据", alias="isHistory"
    ),
) -> str:
    """
    获取大额限价订单数据

    返回订单薄中的大额挂单, 可用于分析支撑/阻力位
    """
    if symbol is None:
        raise ValueError("symbol 必须提供")
    try:
        # 默认开始时间为4小时前
        actual_start_time = start_time
        if actual_start_time is None:
            actual_start_time = _get_current_timestamp_ms() - 4 * 60 * 60 * 1000

        result = await _coinank_request(
            "/bigOrder/queryOrderList",
            {
                "symbol": symbol,
                "exchangeType": exchange_type.value,
                "amount": amount,
                "side": side.value,
                "exchange": exchange.value,
                "startTime": actual_start_time,
                "size": size,
                "isHistory": str(is_history).lower(),
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_open_interest_rank",
    annotations={
        "title": "获取持仓排行榜",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_open_interest_rank(
    page: int = Field(default=1, description="页码"),
    size: int = Field(default=50, description="每页大小"),
    sort_by: str = Field(
        default="openInterest", description="排序字段", alias="sortBy"
    ),
    sort_type: SortType = Field(
        default=SortType.DESC, description="排序类型", alias="sortType"
    ),
) -> str:
    """
    获取持仓量排行榜数据

    返回字段:
    - baseCoin: 币种
    - openInterest: 持仓量
    - openInterestCh1/Ch4/Ch24: 1小时/4小时/24小时持仓变化
    """
    try:
        result = await _coinank_request(
            "/instruments/oiRank",
            {
                "page": page,
                "size": size,
                "sortBy": sort_by,
                "sortType": sort_type.value,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_volume_rank",
    annotations={
        "title": "获取交易量变化排行榜",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_volume_rank(
    sort_by: Optional[str] = Field(
        default=None, description="排序字段", alias="sortBy"
    ),
    sort_type: SortType = Field(
        default=SortType.DESC, description="排序类型", alias="sortType"
    ),
    size: int = Field(default=3, description="返回数据数量"),
    page: int = Field(default=1, description="页码"),
) -> str:
    """
    获取交易量变化排行榜

    返回字段:
    - baseCoin: 币种
    - turnover24h: 24小时成交额
    - turnoverChg24h/4h/1h: 成交额变化率
    """
    try:
        result = await _coinank_request(
            "/instruments/volumeRank",
            {
                "sortBy": sort_by,
                "sortType": sort_type.value,
                "size": size,
                "page": page,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_price_rank",
    annotations={
        "title": "获取价格变化排行榜",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_price_rank(
    sort_by: PriceRankSortBy = Field(
        default=PriceRankSortBy.PRICE_CHANGE_H24,
        description="排序字段",
        alias="sortBy",
    ),
    sort_type: SortType = Field(
        default=SortType.DESC,
        description="排序类型, desc为涨, asc为跌",
        alias="sortType",
    ),
    size: int = Field(default=10, description="返回数据数量"),
    page: int = Field(default=1, description="页码"),
    only_binance: bool = Field(
        default=True, description="是否只返回币安数据", alias="onlyBinance"
    ),
) -> str:
    """
    获取价格变化排行榜

    返回字段:
    - baseCoin: 币种
    - price: 当前价格
    - priceChangeH24/H1等: 各时间段涨跌幅
    - turnover24h: 24小时成交额
    """
    try:
        result = await _coinank_request(
            "/instruments/priceRank",
            {
                "sortBy": sort_by.value,
                "sortType": sort_type.value,
                "size": size,
                "page": page,
            },
        )
        # 只保留币安合约数据
        if only_binance and "list" in result:
            result["list"] = [
                {**item, "coinImage": ""}
                for item in result["list"]
                if item.get("exchangeName") == "Binance" and item.get("supportContract")
            ]
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="coinank_get_klines",
    annotations={
        "title": "获取K线数据",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def coinank_get_klines(
    symbol: Optional[str] = Field(default=None, description="交易对"),
    exchange: Exchange = Field(default=Exchange.BINANCE, description="交易所"),
    end_time: Optional[int] = Field(
        default=None, description="结束时间(时间戳毫秒)", alias="endTime"
    ),
    size: int = Field(default=1, description="返回数据数量"),
    interval: Interval = Field(default=Interval.MINUTE_15, description="K线时间间隔"),
    product_type: ProductType = Field(
        default=ProductType.SWAP, description="产品类型", alias="productType"
    ),
) -> str:
    """
    获取价格K线数据

    返回数组格式:
    [开始时间, 结束时间, 开盘价, 收盘价, 最高价, 最低价, 成交量, 成交额]

    提示: 查询最近一周数据, 15分钟K线 size=672, 1小时K线 size=168
    """
    try:
        result = await _coinank_request(
            "/kline/lists",
            {
                "symbol": symbol,
                "exchange": exchange.value,
                "endTime": end_time or _get_current_timestamp_ms(),
                "size": size,
                "interval": interval.value,
                "productType": product_type.value,
            },
        )
        # 只保留前8个字段
        filtered = [item[:8] if len(item) >= 8 else item for item in result]
        return json.dumps(filtered, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_api_error(e)


# 运行服务器
if __name__ == "__main__":
    mcp.run()
