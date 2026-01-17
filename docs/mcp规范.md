# MCP 工具参数规范

基于 Model Context Protocol 官方规范整理.

## 1. 工具定义结构

```json
{
  "name": "tool_name",
  "description": "工具描述",
  "inputSchema": {
    "type": "object",
    "properties": {
      "param1": { "type": "string", "description": "参数1说明" },
      "param2": { "type": "number", "description": "参数2说明" }
    },
    "required": ["param1"]
  }
}
```

## 2. 工具调用格式 (JSON-RPC 2.0)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1",
      "param2": 123
    }
  }
}
```

## 3. 关键规则

| 规则 | 说明 |
|------|------|
| 扁平结构 | `inputSchema.properties` 必须是扁平的, 不要嵌套对象 |
| JSON Schema | 参数定义遵循 JSON Schema 标准 |
| 类型明确 | 每个参数必须有 `type` 定义 |
| 描述清晰 | 每个参数应有 `description` 帮助 LLM 理解 |

## 4. FastMCP 正确写法

### 错误写法 (嵌套结构)

```python
class ChangeLeverageInput(BaseModel):
    symbol: str = Field(..., description="交易对")
    leverage: int = Field(..., description="杠杆倍数")

@mcp.tool()
def change_leverage(params: ChangeLeverageInput) -> str:
    ...
```

生成的 schema (错误):

```json
{
  "properties": {
    "params": {
      "type": "object",
      "properties": {
        "symbol": { "type": "string" },
        "leverage": { "type": "integer" }
      }
    }
  }
}
```

### 正确写法 (扁平结构)

```python
@mcp.tool()
def change_leverage(
    symbol: str = Field(..., description="交易对, 如 BTCUSDT"),
    leverage: int = Field(..., description="杠杆倍数 (1-125)", ge=1, le=125)
) -> str:
    ...
```

生成的 schema (正确):

```json
{
  "properties": {
    "symbol": { "type": "string", "description": "交易对, 如 BTCUSDT" },
    "leverage": { "type": "integer", "description": "杠杆倍数 (1-125)" }
  }
}
```

## 5. 参考资料

- [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [MCP Concepts - Tools](https://modelcontextprotocol.io/docs/concepts/tools)
