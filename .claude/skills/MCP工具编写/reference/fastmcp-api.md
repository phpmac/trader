# FastMCP API 快速参考

## 服务器初始化

```python
from fastmcp import FastMCP

# 基础初始化
mcp = FastMCP("trading_mcp")

# 带生命周期管理
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    # 初始化资源 (如数据库连接、API 客户端)
    client = await create_api_client()
    yield {"client": client}
    # 清理资源
    await client.close()

mcp = FastMCP("trading_mcp", lifespan=app_lifespan)
```

## 工具注册

### 装饰器模式

```python
@mcp.tool
def simple_tool(x: int) -> str:
    """简单工具"""
    return str(x)

@mcp.tool("custom_name")
def named_tool(x: int) -> str:
    """自定义名称"""
    return str(x)

@mcp.tool(
    name="full_config",
    annotations={
        "title": "完整配置工具",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def full_tool(params: InputModel) -> str:
    """带完整配置的工具"""
    pass
```

### 工具注解 (annotations)

| 注解 | 类型 | 说明 |
|------|------|------|
| `title` | str | 人类可读的工具标题 |
| `readOnlyHint` | bool | 工具是否只读 (不修改状态) |
| `destructiveHint` | bool | 工具是否有破坏性操作 |
| `idempotentHint` | bool | 重复调用是否产生相同结果 |
| `openWorldHint` | bool | 工具是否与外部服务交互 |

## Pydantic 输入模型

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator

class TradeInput(BaseModel):
    """交易输入模型"""
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 自动去除字符串首尾空白
        validate_assignment=True,    # 赋值时验证
        extra='forbid'              # 禁止额外字段
    )
    
    symbol: str = Field(
        ...,  # 必填
        description="交易对符号",
        min_length=1,
        max_length=20
    )
    side: str = Field(
        ...,
        description="交易方向: BUY 或 SELL"
    )
    quantity: float = Field(
        ...,
        description="数量",
        gt=0  # 必须大于 0
    )
    price: Optional[float] = Field(
        default=None,
        description="限价单价格",
        gt=0
    )
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return v.upper().strip()
    
    @field_validator('side')
    @classmethod
    def validate_side(cls, v: str) -> str:
        v = v.upper()
        if v not in ['BUY', 'SELL']:
            raise ValueError("side 必须是 BUY 或 SELL")
        return v
```

## 上下文注入 (Context)

```python
from fastmcp import FastMCP, Context

@mcp.tool()
async def advanced_tool(query: str, ctx: Context) -> str:
    """使用上下文的工具"""
    
    # 进度报告 (长时间操作)
    await ctx.report_progress(0.25, "开始处理...")
    
    # 日志记录
    await ctx.log_info("处理查询", {"query": query})
    await ctx.log_debug("调试信息")
    await ctx.log_error("错误信息")
    
    # 获取生命周期资源
    client = ctx.request_context.lifespan_state["client"]
    
    # 获取服务器名称
    server_name = ctx.fastmcp.name
    
    return "完成"
```

## 资源注册

```python
@mcp.resource("config://trading/{key}")
async def get_trading_config(key: str) -> str:
    """暴露配置为 MCP 资源"""
    configs = {
        "risk_per_trade": "2%",
        "max_positions": "5"
    }
    return configs.get(key, "未找到配置")

@mcp.resource("data://symbols")
async def get_symbols() -> str:
    """暴露交易对列表"""
    return json.dumps(["BTCUSDT", "ETHUSDT", "BNBUSDT"])
```

## 动态工具管理

```python
# 移除工具
mcp.remove_tool("tool_name")

# 添加工具 (运行时)
from fastmcp import Tool

def new_tool_fn(a: int) -> int:
    return a * 2

new_tool = Tool.from_function(fn=new_tool_fn, name="dynamic_tool")
mcp.add_tool(new_tool)
```

## 传输配置

```python
# stdio (默认, 本地工具)
if __name__ == "__main__":
    mcp.run()

# HTTP (远程服务)
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")

# SSE (兼容旧客户端)
if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
```

## 客户端使用

```python
from fastmcp import Client
import asyncio

async def main():
    # 连接 stdio 服务器
    async with Client("server.py") as client:
        # 列出工具
        tools = await client.list_tools()
        
        # 调用工具
        result = await client.call_tool("binance_get_price", {"symbol": "BTCUSDT"})
        print(result.content[0].text)
    
    # 连接 HTTP 服务器
    async with Client("http://localhost:8000/mcp") as client:
        pass
    
    # 内存测试 (直接连接 FastMCP 实例)
    from server import mcp
    async with Client(mcp) as client:
        result = await client.call_tool("test_tool", {})

asyncio.run(main())
```

## HTTP 认证

```python
from fastmcp.server.auth.providers.bearer import BearerAuthProvider

# API Key 认证
auth = BearerAuthProvider(
    token=os.environ["API_TOKEN"],
    header_name="X-API-Key"
)

mcp = FastMCP("secure_mcp", auth=auth)
```

## 错误处理最佳实践

```python
import httpx

def handle_exchange_error(e: Exception, exchange: str = "交易所") -> str:
    """统一的交易所 API 错误处理"""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        try:
            error_body = e.response.json()
            code = error_body.get("code", "")
            msg = error_body.get("msg", "")
        except:
            code, msg = "", str(e)
        
        error_map = {
            400: f"请求参数错误: {msg}",
            401: "API 认证失败, 请检查 API Key",
            403: "权限不足, 请检查 API 权限",
            429: "请求频率过高, 请稍后重试",
            500: f"{exchange}服务器错误",
            502: f"{exchange}网关错误",
            503: f"{exchange}服务不可用"
        }
        return f"Error: {error_map.get(status, f'HTTP {status}: {msg}')}"
    
    elif isinstance(e, httpx.TimeoutException):
        return f"Error: 请求{exchange}超时, 请重试"
    
    elif isinstance(e, httpx.ConnectError):
        return f"Error: 无法连接{exchange}, 请检查网络"
    
    return f"Error: {type(e).__name__}: {str(e)}"
```

