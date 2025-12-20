#!/usr/bin/env python3
"""
币安 USDT 合约 MCP 服务器

提供币安 USDT-M 永续合约交易相关的 MCP 工具集:
- 账户余额查询
- 持仓信息查询
- 杠杆设置
- 开仓/平仓
- 止损止盈订单
- 订单管理 (查询/撤销)

安全说明:
- API 密钥必须通过环境变量配置
"""

import json
import os
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from binance.error import ClientError, ServerError
from binance.um_futures import UMFutures
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# 加载项目根目录的 .env 文件
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")

# 初始化 MCP 服务器
mcp = FastMCP[Any]("binance_futures_mcp")


# ============ 枚举定义 ============


class OrderSide(str, Enum):
    """订单方向"""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """订单类型"""

    LIMIT = "LIMIT"  # 限价单
    MARKET = "MARKET"  # 市价单
    STOP = "STOP"  # 止损限价单
    STOP_MARKET = "STOP_MARKET"  # 止损市价单
    TAKE_PROFIT = "TAKE_PROFIT"  # 止盈限价单
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"  # 止盈市价单
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"  # 跟踪止损单


class PositionSide(str, Enum):
    """持仓方向 (对冲模式)"""

    BOTH = "BOTH"  # 单向持仓模式
    LONG = "LONG"  # 多头
    SHORT = "SHORT"  # 空头


class TimeInForce(str, Enum):
    """订单有效期"""

    GTC = "GTC"  # Good Till Cancel 成交为止
    IOC = "IOC"  # Immediate or Cancel 立即成交或取消
    FOK = "FOK"  # Fill or Kill 全部成交或取消
    GTX = "GTX"  # Post Only 只做maker


class WorkingType(str, Enum):
    """触发价格类型"""

    MARK_PRICE = "MARK_PRICE"  # 标记价格
    CONTRACT_PRICE = "CONTRACT_PRICE"  # 最新价格


class MarginType(str, Enum):
    """保证金类型"""

    ISOLATED = "ISOLATED"  # 逐仓
    CROSSED = "CROSSED"  # 全仓


# ============ Pydantic 输入模型 ============


class GetBalanceInput(BaseModel):
    """获取账户余额输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    asset: Optional[str] = Field(
        default=None, description="资产名称 (如 USDT), 不传则返回所有资产"
    )


class GetPositionsInput(BaseModel):
    """获取持仓信息输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: Optional[str] = Field(
        default=None, description="交易对 (如 BTCUSDT), 不传则返回所有持仓"
    )


class ChangeLeverageInput(BaseModel):
    """修改杠杆倍数输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")
    leverage: int = Field(..., description="杠杆倍数 (1-125)", ge=1, le=125)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()


class ChangeMarginTypeInput(BaseModel):
    """修改保证金模式输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")
    margin_type: MarginType = Field(
        ..., description="保证金模式: ISOLATED(逐仓) 或 CROSSED(全仓)"
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()


class PlaceOrderInput(BaseModel):
    """下单输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")
    side: OrderSide = Field(
        ..., description="订单方向: BUY(买入/做多) 或 SELL(卖出/做空)"
    )
    order_type: OrderType = Field(
        default=OrderType.MARKET,
        description="订单类型",
        alias="type",
    )
    quantity: float = Field(..., description="下单数量", gt=0)
    price: Optional[float] = Field(default=None, description="限价单价格", gt=0)
    position_side: PositionSide = Field(
        default=PositionSide.BOTH,
        description="持仓方向 (对冲模式使用)",
        alias="positionSide",
    )
    time_in_force: TimeInForce = Field(
        default=TimeInForce.GTC, description="订单有效期", alias="timeInForce"
    )
    reduce_only: bool = Field(
        default=False, description="是否只减仓", alias="reduceOnly"
    )
    stop_price: Optional[float] = Field(
        default=None, description="止损/止盈触发价格", alias="stopPrice", gt=0
    )
    working_type: WorkingType = Field(
        default=WorkingType.CONTRACT_PRICE,
        description="触发价格类型",
        alias="workingType",
    )
    close_position: bool = Field(
        default=False,
        description="是否全部平仓 (用于止损/止盈单)",
        alias="closePosition",
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()


class ClosePositionInput(BaseModel):
    """平仓输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")
    position_side: PositionSide = Field(
        default=PositionSide.BOTH,
        description="持仓方向 (对冲模式使用)",
        alias="positionSide",
    )
    quantity: Optional[float] = Field(
        default=None, description="平仓数量, 不传则全部平仓", gt=0
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()


class SetStopLossTakeProfitInput(BaseModel):
    """设置止损止盈输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")
    position_side: PositionSide = Field(
        default=PositionSide.BOTH,
        description="持仓方向",
        alias="positionSide",
    )
    stop_loss_price: Optional[float] = Field(
        default=None, description="止损触发价格", alias="stopLossPrice", gt=0
    )
    take_profit_price: Optional[float] = Field(
        default=None, description="止盈触发价格", alias="takeProfitPrice", gt=0
    )
    working_type: WorkingType = Field(
        default=WorkingType.CONTRACT_PRICE,
        description="触发价格类型",
        alias="workingType",
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()


class CancelOrderInput(BaseModel):
    """撤销订单输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")
    order_id: Optional[int] = Field(default=None, description="订单ID", alias="orderId")
    client_order_id: Optional[str] = Field(
        default=None, description="客户端订单ID", alias="origClientOrderId"
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()


class CancelAllOrdersInput(BaseModel):
    """撤销所有订单输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: str = Field(..., description="交易对, 如 BTCUSDT")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()


class GetOpenOrdersInput(BaseModel):
    """查询当前挂单输入"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    symbol: Optional[str] = Field(
        default=None, description="交易对 (如 BTCUSDT), 不传则返回所有挂单"
    )


# ============ 客户端工具函数 ============


def _get_client() -> UMFutures:
    """获取币安 USDT-M 期货客户端"""
    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError("环境变量 BINANCE_API_KEY 和 BINANCE_API_SECRET 必须设置")

    return UMFutures(key=api_key, secret=api_secret)


def _is_hedge_mode(client: UMFutures) -> bool:
    """检查账户是否为对冲模式 (双向持仓)"""
    result = client.get_position_mode()
    return result.get("dualSidePosition", False)


def _auto_position_side(
    client: UMFutures, side: OrderSide, position_side: PositionSide
) -> PositionSide:
    """
    自动确定 positionSide

    - 单向持仓模式: 始终返回 BOTH
    - 对冲模式: 根据订单方向自动设置
      - BUY 开仓 -> LONG
      - SELL 开仓 -> SHORT
    """
    if position_side != PositionSide.BOTH:
        # 用户明确指定了, 直接使用
        return position_side

    if not _is_hedge_mode(client):
        # 单向持仓模式, 使用 BOTH
        return PositionSide.BOTH

    # 对冲模式, 根据订单方向自动设置
    if side == OrderSide.BUY:
        return PositionSide.LONG
    else:
        return PositionSide.SHORT


def _handle_error(e: Exception) -> str:
    """统一错误处理"""
    if isinstance(e, ClientError):
        return f"Error: [{e.error_code}] {e.error_message}"
    elif isinstance(e, ServerError):
        return f"Error: 币安服务器错误 - {str(e)}"
    elif isinstance(e, ValueError):
        return f"Error: {str(e)}"
    return f"Error: {type(e).__name__}: {str(e)}"


# ============ MCP 工具定义 ============


@mcp.tool(
    name="binance_get_balance",
    annotations={
        "title": "查询账户余额",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def binance_get_balance(params: GetBalanceInput = GetBalanceInput()) -> str:
    """
    查询币安 USDT 合约账户余额

    返回字段:
    - asset: 资产名称
    - walletBalance: 钱包余额
    - unrealizedProfit: 未实现盈亏
    - marginBalance: 保证金余额
    - availableBalance: 可用余额
    - maxWithdrawAmount: 最大可提取金额
    """
    try:
        client = _get_client()
        result = client.balance()

        # 过滤资产
        if params.asset:
            asset_upper = params.asset.upper()
            result = [item for item in result if item.get("asset") == asset_upper]
            if not result:
                return f"Error: 未找到资产 {params.asset}"

        # 只保留关键字段, 并过滤零余额
        filtered = []
        for item in result:
            wallet_balance = Decimal(item.get("balance", "0"))
            if wallet_balance != 0 or params.asset:
                filtered.append(
                    {
                        "asset": item.get("asset"),
                        "walletBalance": str(wallet_balance),
                        "unrealizedProfit": item.get("crossUnPnl"),
                        "marginBalance": item.get("marginBalance"),
                        "availableBalance": item.get("availableBalance"),
                        "maxWithdrawAmount": item.get("maxWithdrawAmount"),
                    }
                )

        return json.dumps(filtered, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_get_positions",
    annotations={
        "title": "查询持仓信息",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def binance_get_positions(params: GetPositionsInput = GetPositionsInput()) -> str:
    """
    查询币安 USDT 合约持仓信息

    返回字段:
    - symbol: 交易对
    - positionAmt: 持仓数量 (正数为多, 负数为空)
    - entryPrice: 开仓均价
    - markPrice: 标记价格
    - unRealizedProfit: 未实现盈亏
    - liquidationPrice: 强平价格
    - leverage: 杠杆倍数
    - marginType: 保证金模式 (isolated/cross)
    - positionSide: 持仓方向
    """
    try:
        client = _get_client()

        if params.symbol:
            result = client.get_position_risk(symbol=params.symbol.upper())
        else:
            result = client.get_position_risk()

        # 只保留有持仓的记录
        filtered = []
        for item in result:
            position_amt = Decimal(item.get("positionAmt", "0"))
            if position_amt != 0:
                filtered.append(
                    {
                        "symbol": item.get("symbol"),
                        "positionAmt": str(position_amt),
                        "entryPrice": item.get("entryPrice"),
                        "markPrice": item.get("markPrice"),
                        "unRealizedProfit": item.get("unRealizedProfit"),
                        "liquidationPrice": item.get("liquidationPrice"),
                        "leverage": item.get("leverage"),
                        "marginType": item.get("marginType"),
                        "positionSide": item.get("positionSide"),
                    }
                )

        if not filtered:
            return json.dumps({"message": "当前无持仓"}, ensure_ascii=False)

        return json.dumps(filtered, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_change_leverage",
    annotations={
        "title": "设置杠杆倍数",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def binance_change_leverage(params: ChangeLeverageInput) -> str:
    """
    设置交易对的杠杆倍数

    参数:
    - symbol: 交易对 (如 BTCUSDT)
    - leverage: 杠杆倍数 (1-125)

    返回:
    - leverage: 设置后的杠杆倍数
    - maxNotionalValue: 当前杠杆下最大名义价值
    """
    try:
        client = _get_client()
        result = client.change_leverage(
            symbol=params.symbol,
            leverage=params.leverage,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_change_margin_type",
    annotations={
        "title": "设置保证金模式",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def binance_change_margin_type(params: ChangeMarginTypeInput) -> str:
    """
    设置交易对的保证金模式

    参数:
    - symbol: 交易对 (如 BTCUSDT)
    - margin_type: ISOLATED(逐仓) 或 CROSSED(全仓)

    注意: 有持仓时无法切换保证金模式
    """
    try:
        client = _get_client()
        result = client.change_margin_type(
            symbol=params.symbol,
            marginType=params.margin_type.value,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_place_order",
    annotations={
        "title": "下单",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
def binance_place_order(params: PlaceOrderInput) -> str:
    """
    币安 USDT 合约下单

    订单类型:
    - MARKET: 市价单 (立即成交)
    - LIMIT: 限价单 (需指定 price)
    - STOP_MARKET: 止损市价单 (需指定 stopPrice)
    - TAKE_PROFIT_MARKET: 止盈市价单 (需指定 stopPrice)
    - STOP: 止损限价单 (需指定 price 和 stopPrice)
    - TAKE_PROFIT: 止盈限价单 (需指定 price 和 stopPrice)

    做多流程: side=BUY, 平多用 side=SELL + reduceOnly=true
    做空流程: side=SELL, 平空用 side=BUY + reduceOnly=true

    注意: positionSide 会根据账户模式自动设置
    - 单向持仓模式: 使用 BOTH
    - 对冲模式: BUY -> LONG, SELL -> SHORT (开仓时)
    """
    try:
        client = _get_client()

        # 自动确定 positionSide (仅开仓时自动设置, reduceOnly 平仓时需要正确的方向)
        position_side = params.position_side
        if not params.reduce_only and not params.close_position:
            # 开仓时自动设置
            position_side = _auto_position_side(
                client, params.side, params.position_side
            )

        order_params: dict[str, Any] = {
            "symbol": params.symbol,
            "side": params.side.value,
            "type": params.order_type.value,
            "quantity": params.quantity,
            "positionSide": position_side.value,
        }

        # 限价单需要价格和有效期
        if params.order_type in (
            OrderType.LIMIT,
            OrderType.STOP,
            OrderType.TAKE_PROFIT,
        ):
            if params.price is None:
                return "Error: 限价单必须指定 price"
            order_params["price"] = params.price
            order_params["timeInForce"] = params.time_in_force.value

        # 止损/止盈单需要触发价格
        if params.order_type in (
            OrderType.STOP,
            OrderType.STOP_MARKET,
            OrderType.TAKE_PROFIT,
            OrderType.TAKE_PROFIT_MARKET,
        ):
            if params.stop_price is None:
                return "Error: 止损/止盈单必须指定 stopPrice"
            order_params["stopPrice"] = params.stop_price
            order_params["workingType"] = params.working_type.value

        # 平仓相关 (单向持仓模式才需要 reduceOnly, 对冲模式不支持)
        if params.reduce_only and position_side == PositionSide.BOTH:
            order_params["reduceOnly"] = "true"
        if params.close_position:
            order_params["closePosition"] = "true"

        result = client.new_order(**order_params)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_close_position",
    annotations={
        "title": "平仓",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
def binance_close_position(params: ClosePositionInput) -> str:
    """
    平仓指定交易对的持仓

    参数:
    - symbol: 交易对
    - positionSide: 持仓方向 (对冲模式使用)
    - quantity: 平仓数量, 不传则全部平仓
    """
    try:
        client = _get_client()

        # 先获取当前持仓
        positions = client.get_position_risk(symbol=params.symbol)

        # 找到对应的持仓
        target_position = None
        for pos in positions:
            if pos.get("positionSide") == params.position_side.value:
                position_amt = Decimal(pos.get("positionAmt", "0"))
                if position_amt != 0:
                    target_position = pos
                    break
            elif params.position_side == PositionSide.BOTH:
                position_amt = Decimal(pos.get("positionAmt", "0"))
                if position_amt != 0:
                    target_position = pos
                    break

        if not target_position:
            return json.dumps(
                {"message": f"未找到 {params.symbol} 的持仓"}, ensure_ascii=False
            )

        position_amt = Decimal(target_position.get("positionAmt", "0"))
        close_quantity = params.quantity if params.quantity else abs(position_amt)

        # 确定平仓方向
        if position_amt > 0:
            side = OrderSide.SELL  # 多仓用卖单平仓
        else:
            side = OrderSide.BUY  # 空仓用买单平仓

        # 执行平仓
        order_params: dict[str, Any] = {
            "symbol": params.symbol,
            "side": side.value,
            "type": OrderType.MARKET.value,
            "quantity": float(close_quantity),
            "positionSide": params.position_side.value,
        }
        # 单向持仓模式才需要 reduceOnly
        if params.position_side == PositionSide.BOTH:
            order_params["reduceOnly"] = "true"

        result = client.new_order(**order_params)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_set_stop_loss_take_profit",
    annotations={
        "title": "设置止损止盈",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
def binance_set_stop_loss_take_profit(params: SetStopLossTakeProfitInput) -> str:
    """
    为当前持仓设置止损止盈订单 (使用 Algo Order API)

    参数:
    - symbol: 交易对
    - stopLossPrice: 止损触发价格
    - takeProfitPrice: 止盈触发价格
    - workingType: 触发价格类型 (MARK_PRICE 或 CONTRACT_PRICE)

    注意: 至少需要设置一个价格 (止损或止盈)
    """
    if params.stop_loss_price is None and params.take_profit_price is None:
        return "Error: 至少需要设置 stopLossPrice 或 takeProfitPrice"

    try:
        client = _get_client()

        # 获取当前持仓
        positions = client.get_position_risk(symbol=params.symbol)

        # 找到对应的持仓
        target_position = None
        for pos in positions:
            if pos.get("positionSide") == params.position_side.value:
                position_amt = Decimal(pos.get("positionAmt", "0"))
                if position_amt != 0:
                    target_position = pos
                    break
            elif params.position_side == PositionSide.BOTH:
                position_amt = Decimal(pos.get("positionAmt", "0"))
                if position_amt != 0:
                    target_position = pos
                    break

        if not target_position:
            return json.dumps(
                {"message": f"未找到 {params.symbol} 的持仓, 无法设置止损止盈"},
                ensure_ascii=False,
            )

        position_amt = Decimal(target_position.get("positionAmt", "0"))
        quantity = abs(position_amt)
        results = []

        # 确定止损止盈方向
        if position_amt > 0:
            # 多仓: 止损用卖单, 止盈用卖单
            side = OrderSide.SELL
        else:
            # 空仓: 止损用买单, 止盈用买单
            side = OrderSide.BUY

        # 使用 Algo Order API 设置条件单
        # API endpoint: POST /fapi/v1/algo/futures/newOrderVp
        algo_url = "/fapi/v1/algo/futures/newOrderVp"

        # 设置止损
        if params.stop_loss_price:
            sl_params = {
                "symbol": params.symbol,
                "side": side.value,
                "positionSide": params.position_side.value,
                "quantity": float(quantity),
                "triggerPrice": params.stop_loss_price,
                "workingType": params.working_type.value,
                "reduceOnly": "true",
            }
            sl_result = client.sign_request("POST", algo_url, sl_params)
            results.append({"type": "STOP_LOSS", "order": sl_result})

        # 设置止盈
        if params.take_profit_price:
            tp_params = {
                "symbol": params.symbol,
                "side": side.value,
                "positionSide": params.position_side.value,
                "quantity": float(quantity),
                "triggerPrice": params.take_profit_price,
                "workingType": params.working_type.value,
                "reduceOnly": "true",
            }
            tp_result = client.sign_request("POST", algo_url, tp_params)
            results.append({"type": "TAKE_PROFIT", "order": tp_result})

        return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_cancel_order",
    annotations={
        "title": "撤销订单",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
def binance_cancel_order(params: CancelOrderInput) -> str:
    """
    撤销指定订单

    参数:
    - symbol: 交易对
    - orderId: 订单ID (二选一)
    - origClientOrderId: 客户端订单ID (二选一)
    """
    if params.order_id is None and params.client_order_id is None:
        return "Error: 必须指定 orderId 或 origClientOrderId"

    try:
        client = _get_client()

        cancel_params: dict[str, Any] = {"symbol": params.symbol}
        if params.order_id:
            cancel_params["orderId"] = params.order_id
        if params.client_order_id:
            cancel_params["origClientOrderId"] = params.client_order_id

        result = client.cancel_order(**cancel_params)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_cancel_all_orders",
    annotations={
        "title": "撤销所有订单",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
def binance_cancel_all_orders(params: CancelAllOrdersInput) -> str:
    """
    撤销指定交易对的所有挂单

    参数:
    - symbol: 交易对
    """
    try:
        client = _get_client()
        result = client.cancel_open_orders(symbol=params.symbol)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="binance_get_open_orders",
    annotations={
        "title": "查询当前挂单",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def binance_get_open_orders(params: GetOpenOrdersInput = GetOpenOrdersInput()) -> str:
    """
    查询当前挂单

    返回字段:
    - orderId: 订单ID
    - symbol: 交易对
    - side: 方向
    - type: 订单类型
    - price: 价格
    - origQty: 原始数量
    - executedQty: 已成交数量
    - status: 状态
    - stopPrice: 触发价格
    """
    try:
        client = _get_client()

        # 使用 get_orders() 方法查询所有挂单 (对应 /fapi/v1/openOrders)
        # 注意: get_open_orders() 是查询单个订单 (对应 /fapi/v1/openOrder)
        if params.symbol:
            result = client.get_orders(symbol=params.symbol.upper())
        else:
            result = client.get_orders()

        if not result:
            return json.dumps({"message": "当前无挂单"}, ensure_ascii=False)

        # 只保留关键字段
        filtered = [
            {
                "orderId": item.get("orderId"),
                "symbol": item.get("symbol"),
                "side": item.get("side"),
                "type": item.get("type"),
                "price": item.get("price"),
                "origQty": item.get("origQty"),
                "executedQty": item.get("executedQty"),
                "status": item.get("status"),
                "stopPrice": item.get("stopPrice"),
                "positionSide": item.get("positionSide"),
                "reduceOnly": item.get("reduceOnly"),
            }
            for item in result
        ]

        return json.dumps(filtered, indent=2, ensure_ascii=False)
    except Exception as e:
        return _handle_error(e)


# 运行服务器
if __name__ == "__main__":
    mcp.run()
