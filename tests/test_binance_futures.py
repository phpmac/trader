#!/usr/bin/env python3
"""
binance_futures MCP 集成测试

运行命令:
    uv run pytest tests/test_binance_futures.py -v -s

注意:
    1. 需要设置环境变量 BINANCE_API_KEY 和 BINANCE_API_SECRET
    2. 测试会进行真实交易, 使用极小仓位 (0.001 BTC)
    3. 测试顺序: 查询 -> 设置杠杆 -> 开仓 -> 设置止损止盈 -> 查询持仓 -> 平仓
"""

import json
import time

import pytest

from mcps.binance_futures import (
    CancelAllAlgoOrdersInput,
    ChangeLeverageInput,
    ClosePositionInput,
    GetBalanceInput,
    GetOpenOrdersInput,
    OrderSide,
    PlaceOrderInput,
    SetStopLossTakeProfitInput,
    binance_cancel_all_algo_orders,
    binance_change_leverage,
    binance_close_position,
    binance_get_balance,
    binance_get_open_algo_orders,
    binance_get_open_orders,
    binance_get_positions,
    binance_place_order,
    binance_set_stop_loss_take_profit,
)

# 测试配置
TEST_SYMBOL = "BTCUSDT"
TEST_QUANTITY = 0.001  # 最小交易量
TEST_LEVERAGE = 5


class TestBinanceQueries:
    """查询类测试 (只读, 安全)"""

    def test_get_balance(self):
        """测试查询账户余额"""
        result = binance_get_balance.fn(GetBalanceInput(asset="USDT"))
        print(f"\n账户余额:\n{result}")
        assert "Error" not in result

    def test_get_positions(self):
        """测试查询持仓"""
        result = binance_get_positions.fn()
        print(f"\n当前持仓:\n{result}")
        assert "Error" not in result

    def test_get_open_orders(self):
        """测试查询挂单"""
        result = binance_get_open_orders.fn(GetOpenOrdersInput())
        print(f"\n当前挂单:\n{result}")
        assert "Error" not in result

    def test_get_open_algo_orders(self):
        """测试查询条件单"""
        result = binance_get_open_algo_orders.fn()
        print(f"\n当前条件单:\n{result}")
        assert "Error" not in result


class TestBinanceTrading:
    """交易类测试 (会产生真实交易)"""

    @pytest.mark.skip(reason="真实交易测试, 需要手动运行")
    def test_full_trading_flow(self):
        """
        完整交易流程测试

        流程:
        1. 设置杠杆
        2. 市价开多
        3. 设置止损止盈
        4. 查询持仓和条件单
        5. 撤销条件单
        6. 市价平仓
        """
        print("\n" + "=" * 50)
        print("开始完整交易流程测试")
        print("=" * 50)

        # 1. 设置杠杆
        print(f"\n[1] 设置杠杆 {TEST_LEVERAGE}x")
        result = binance_change_leverage.fn(
            ChangeLeverageInput(symbol=TEST_SYMBOL, leverage=TEST_LEVERAGE)
        )
        print(f"结果: {result}")
        assert "Error" not in result

        # 2. 市价开多
        print(f"\n[2] 市价开多 {TEST_QUANTITY} {TEST_SYMBOL}")
        result = binance_place_order.fn(
            PlaceOrderInput(
                symbol=TEST_SYMBOL,
                side=OrderSide.BUY,
                quantity=TEST_QUANTITY,
            )
        )
        print(f"结果: {result}")
        assert "Error" not in result

        time.sleep(1)  # 等待订单成交

        # 3. 查询持仓, 获取开仓价格
        print("\n[3] 查询持仓")
        result = binance_get_positions.fn({"symbol": TEST_SYMBOL})
        print(f"结果: {result}")
        assert "Error" not in result

        positions = json.loads(result)
        if isinstance(positions, list) and len(positions) > 0:
            entry_price = float(positions[0]["entryPrice"])
            print(f"开仓价格: {entry_price}")

            # 4. 设置止损止盈 (止损 -2%, 止盈 +2%)
            stop_loss = round(entry_price * 0.98, 1)
            take_profit = round(entry_price * 1.02, 1)

            print(f"\n[4] 设置止损止盈 (SL: {stop_loss}, TP: {take_profit})")
            result = binance_set_stop_loss_take_profit.fn(
                SetStopLossTakeProfitInput(
                    symbol=TEST_SYMBOL,
                    **{"stopLossPrice": stop_loss, "takeProfitPrice": take_profit},
                )
            )
            print(f"结果: {result}")
            assert "Error" not in result

            time.sleep(1)

        # 5. 查询条件单
        print("\n[5] 查询条件单")
        result = binance_get_open_algo_orders.fn()
        print(f"结果: {result}")

        # 6. 撤销所有条件单
        print(f"\n[6] 撤销 {TEST_SYMBOL} 所有条件单")
        result = binance_cancel_all_algo_orders.fn(
            CancelAllAlgoOrdersInput(symbol=TEST_SYMBOL)
        )
        print(f"结果: {result}")

        # 7. 市价平仓
        print(f"\n[7] 市价平仓 {TEST_SYMBOL}")
        result = binance_close_position.fn(ClosePositionInput(symbol=TEST_SYMBOL))
        print(f"结果: {result}")
        assert "Error" not in result

        # 8. 确认平仓完成
        print("\n[8] 确认平仓完成")
        result = binance_get_positions.fn({"symbol": TEST_SYMBOL})
        print(f"结果: {result}")

        print("\n" + "=" * 50)
        print("交易流程测试完成")
        print("=" * 50)


# 单独的交易测试函数 (方便单独运行)
@pytest.mark.skip(reason="真实交易测试, 需要手动运行")
def test_open_long():
    """单独测试: 开多"""
    result = binance_place_order.fn(
        PlaceOrderInput(
            symbol=TEST_SYMBOL,
            side=OrderSide.BUY,
            quantity=TEST_QUANTITY,
        )
    )
    print(f"\n开多结果:\n{result}")


@pytest.mark.skip(reason="真实交易测试, 需要手动运行")
def test_close_position():
    """单独测试: 平仓"""
    result = binance_close_position.fn(ClosePositionInput(symbol=TEST_SYMBOL))
    print(f"\n平仓结果:\n{result}")
