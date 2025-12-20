# AGENTS.md

本项目是一个交易系统, 由专业交易员主导开发和使用.

## 项目概述

这是一个专业的交易系统项目, 涵盖市场分析、策略开发、风险管理和订单执行等核心功能.

## 交易员核心概念

作为 AI 代理, 你需要理解以下交易员必须掌握的核心概念:

### 市场结构 (Market Structure)

- **趋势识别**: 上升趋势(Higher Highs, Higher Lows) / 下降趋势(Lower Highs, Lower Lows)
- **结构突破**: BOS(Break of Structure) / CHoCH(Change of Character)
- **支撑与阻力**: 关键价格区域的识别和验证
- **市场周期**: 积累(Accumulation) -> 上涨(Markup) -> 派发(Distribution) -> 下跌(Markdown)

### SMC/ICT 聪明钱概念 (Smart Money Concepts)

- **流动性 (Liquidity)**:
  - BSL(Buy Side Liquidity) - 买方流动性, 止损单聚集区
  - SSL(Sell Side Liquidity) - 卖方流动性, 止损单聚集区
  - 流动性猎取(Liquidity Grab/Sweep) - 机构扫盘行为
- **订单块 (Order Block)**:
  - OB(Order Block) - 机构建仓区域, 通常是反转前的最后一根反向K线
  - Bullish OB / Bearish OB
  - Mitigation - OB 被价格回测并产生反应
- **公允价值缺口 (Fair Value Gap / Imbalance)**:
  - FVG - 价格快速移动形成的缺口区域
  - IFVG(Inversion FVG) - 反转后的FVG, 原阻力变支撑或原支撑变阻力
  - BISI(Buyside Imbalance Sellside Inefficiency)
  - SIBI(Sellside Imbalance Buyside Inefficiency)
- **折扣区与溢价区 (Discount/Premium)**:
  - 使用 Fibonacci 回撤划分区域
  - 折扣区(50%以下) - 寻找做多机会
  - 溢价区(50%以上) - 寻找做空机会
- **时间与价格理论 (ICT Time & Price)**:
  - Killzones - 伦敦开盘/纽约开盘等关键时段
  - Power of 3 (AMD) - 积累(Accumulation), 操纵(Manipulation), 派发(Distribution)
  - 每日偏见(Daily Bias) - 基于高时间框架确定方向
- **其他关键概念**:
  - EQH/EQL(Equal Highs/Lows) - 流动性目标
  - Inducement - 诱导散户入场的假突破
  - Breaker Block - 失效的OB转换为支撑/阻力
  - Propulsion Block - 推进块, 强势移动后的回调区域
  - Rejection Block - 长影线形成的区域
  - POI(Point of Interest) - 关键关注区域
  - CISD(Change In State of Delivery) - 交付状态变化
  - BPR(Balanced Price Range) - 平衡价格区间
  - SMT Divergence - 聪明钱背离, 相关资产间的背离信号
  - Breakaway Gap - 突破缺口

### 订单流与市场微观结构 (Order Flow)

- **订单类型**: 限价单(Limit), 市价单(Market), 止损单(Stop), 冰山单(Iceberg)
- **订单簿分析**: Bid/Ask Spread, Depth, Imbalance
- **成交量分析**: Volume Delta, CVD(Cumulative Volume Delta)
- **足迹图**: Footprint Chart, 成交量分布

### 风险管理 (Risk Management)

- **仓位管理**: 固定比例法, 凯利公式, 反马丁格尔
- **止损策略**: 固定止损, ATR止损, 结构止损, 追踪止损
- **风险指标**: 最大回撤(MDD), 夏普比率(Sharpe), 索提诺比率(Sortino), 盈亏比(R:R)
- **相关性**: 持仓相关性分析, 分散化

### 交易心理 (Trading Psychology)

- **情绪管理**: FOMO(错失恐惧), 贪婪, 恐惧, 复仇交易
- **纪律执行**: 严格遵守交易计划
- **交易日志**: 记录每笔交易的理由、情绪、结果

### 资金管理 (Money Management)

- **单笔风险**: 通常不超过账户的 1-2%
- **每日/每周风险上限**: 防止连续亏损
- **盈利保护**: 浮盈管理, 分批止盈

## 开发规范

### 代码风格

- 使用中文注释
- 标点符号使用英文
- 变量命名使用 snake_case (Python) 或 camelCase (TypeScript)
- 函数/方法需要完整的类型注解
- 业务目录使用中文命名 (系统/第三方约定目录除外, 如 `.git`, `node_modules`, `.claude` 等)

### 安全要求

- API 密钥必须使用环境变量, 禁止硬编码
- 所有外部输入必须验证
- 交易逻辑必须有完整的错误处理
- 关键操作需要日志记录

### 测试要求

- 策略必须经过回测验证, 不能盲目进行实盘交易
- 未经验证的策略只能使用模拟交易模式 (仅记录数据, 不执行真实订单)
- 实盘交易前必须确保策略逻辑已得到充分验证

## Skills 技能系统

本项目使用 [Claude Skills](https://github.com/anthropics/skills) 系统来扩展 AI 代理的专业能力. Skills 是包含指令、脚本和资源的文件夹, AI 代理可以动态加载以提升特定任务的表现.

### Skills 的用途

Skills 的作用非常广泛, 不仅限于技术开发, 还包括:

- **开发工具**: MCP 工具编写、数据接口使用等
- **风险管理**: 仓位管理方法、资金管理策略等
- **交易方法**: 各种交易思路、交易策略的整理和文档化
- **市场分析**: 分析框架、指标使用方法等

**交易员可以将任何交易思路、交易方法整理成 skill**, 便于 AI 代理理解和辅助执行.

### 官方 Skills 资源

- **GitHub 仓库**: https://github.com/anthropics/skills
- **本地示例目录**: `/Users/a/Downloads/skills` (包含大量 skill 示例, 如 mcp-builder、pdf、xlsx 等)

### Skills 目录位置

```
.claude/skills/         # 本项目技能定义目录
```

### 当前已有 Skills

| Skill 名称 | 描述 | 路径 |
|------------|------|------|
| `交易前必读` | **每次对话必读** - 行为规范, 消息类型识别, 检查流程 | `.claude/skills/交易前必读/` |
| `最新指令` | **每次对话必读** - 交易员临时指令/任务管理 | `.claude/skills/最新指令/` |
| `交易时段` | 可交易时间配置 (07:00-24:00 CST) | `.claude/skills/交易时段/` |
| `固定风险仓位管理` | 固定风险金额仓位管理法 (R值法) | `.claude/skills/固定风险仓位管理/` |
| `MCP工具编写` | MCP 工具开发指南 (FastMCP) | `.claude/skills/MCP工具编写/` |
| `Coinank数据接口` | Coinank MCP 数据接口使用指南 | `.claude/skills/Coinank数据接口/` |
| `币安合约交易` | 币安合约交易接口 | `.claude/skills/币安合约交易/` |
| `交易方法整理` | 交易方法/策略汇总目录 | `.claude/skills/交易方法整理/` |

### 交易方法整理

`交易方法整理` 是一个特殊的 skill 目录, 用于收录各种交易方法和交易思路:

```
.claude/skills/交易方法整理/
├── SKILL.md                    # 目录说明
├── BOS突破交易法/              # 独立 skill
│   └── SKILL.md
└── [更多交易方法]/
    └── SKILL.md
```

注意: 每个交易方法都是独立的 skill, 目录名使用中文, SKILL.md 中的 name 字段使用 hyphen-case (小写+连字符).

交易员可以持续向此目录添加新的交易方法.

### Skill 文件结构

每个 skill 是一个独立文件夹, 必须包含 `SKILL.md` 文件:

```
.claude/skills/
├── 交易前必读/                  # 行为规范 (每次对话必读)
│   └── SKILL.md
├── 最新指令/                    # 临时指令管理 (每次对话必读)
│   └── SKILL.md
├── 交易时段/                    # 可交易时间配置
│   └── SKILL.md
├── 固定风险仓位管理/            # R值仓位管理法
│   └── SKILL.md
├── MCP工具编写/                 # MCP 工具开发 (FastMCP)
│   ├── SKILL.md
│   └── reference/
│       └── fastmcp-api.md
├── Coinank数据接口/             # Coinank 数据接口
│   └── SKILL.md
├── 币安合约交易/                # 币安合约交易接口
│   └── SKILL.md
└── 交易方法整理/                # 交易方法/策略汇总
    ├── SKILL.md
    └── BOS突破交易法/
        └── SKILL.md
```

### SKILL.md 格式

```markdown
---
name: skill-name        # 技能名称 (小写, 连字符分隔)
description: 技能描述    # 描述技能用途和触发条件
---

# 技能指令内容
```

### 使用方式

- AI 代理会根据任务自动加载相关 skill
- 也可以在对话中明确提及 skill 名称来触发
- Skills 提供专业领域的知识和操作指南
- 参考 `/Users/a/Downloads/skills` 目录获取更多 skill 示例和模板

## MCP 工具

本项目使用 MCP (Model Context Protocol) 提供交易相关的工具能力.

### 当前已有 MCP 服务

| MCP 服务 | 文件 | 说明 |
|---------|------|------|
| `time-tools` | `mcps/time_tools.py` | 时间工具 - 获取 CST 时间, 检查交易时段 |
| `coinank-tools` | `mcps/coinank.py` | Coinank 数据 - 行情/持仓/CVD/资金流等 |
| `binance-futures` | `mcps/binance_futures.py` | 币安合约 - 账户/持仓/下单/平仓等 |
| `slack-tools` | `mcps/slack_notify.py` | Slack 通知 - 交易通知/风险预警 |

### 常用工具速查

| 工具 | MCP 服务 | 用途 |
|-----|---------|------|
| `get_current_time` | time-tools | 获取当前 CST 时间 |
| `coinank_get_last_price` | coinank-tools | 获取实时价格 |
| `coinank_get_klines` | coinank-tools | 获取 K 线数据 |
| `binance_get_balance` | binance-futures | 查询账户余额 |
| `binance_get_positions` | binance-futures | 查询当前持仓 |
| `binance_place_order` | binance-futures | 下单 |
| `binance_close_position` | binance-futures | 平仓 |
| `slack_send_message` | slack-tools | 发送 Slack 通知 |

## 目录结构

```
trader/
├── AGENTS.md           # AI 代理指南 (本文档)
├── README.md           # 项目自述文件
├── main.py             # 主入口文件
├── pyproject.toml      # Python 项目配置
├── uv.lock             # uv 依赖锁定文件
├── .claude/
│   └── skills/         # Claude 技能定义
│       ├── 交易前必读/             # 行为规范 (每次对话必读)
│       ├── 最新指令/               # 临时指令管理 (每次对话必读)
│       ├── 交易时段/               # 可交易时间配置
│       ├── 固定风险仓位管理/
│       ├── MCP工具编写/
│       ├── Coinank数据接口/
│       ├── 币安合约交易/
│       └── 交易方法整理/       # 交易方法/策略汇总
│           └── BOS突破交易法/  # 具体交易方法
├── docs/               # 文档目录
│   ├── todo.md
│   ├── 交易前必读.md       # 核心风控规则 (每次对话必读)
│   ├── 最新指令.md         # 交易员临时指令 (每次对话必读)
│   └── 历史指令/           # 已归档的任务记录
└── mcps/               # MCP 服务器 (交易工具)
    ├── time_tools.py       # 时间工具 MCP 服务
    ├── coinank.py          # Coinank 数据 MCP 服务
    ├── binance_futures.py  # 币安 USDT-M 合约交易 MCP 服务
    └── slack_notify.py     # Slack 通知 MCP 服务
```

## 默认交易方法

当前默认使用 **BOS突破交易法** 进行交易分析和执行:

- 技能路径: `.claude/skills/交易方法整理/BOS突破交易法/`
- 核心逻辑: 等待 BOS (Break of Structure) 确认后, 在回调至 OB/FVG 区域时入场
- 详细规则请参考该 skill 的 SKILL.md 文件

---

## 注意事项

- 交易涉及真金白银, 所有代码修改必须谨慎
- 不确定的功能必须先讨论方案
- 实盘代码必须有完整的异常处理和回退机制
- **交易分析时必须尽可能使用 MCP 提供的工具**, 获取实时行情、订单簿深度、K线数据等, 以确保分析基于最新市场数据, 获得更好的盈亏比
- **MCP 工具调用出现代码错误时 (如 AttributeError、TypeError 等), 必须停止当前任务, 报告错误并等待交易员修复**, 不要尝试绕过或使用其他方式继续
- 本文档 (AGENTS.md) 可随时进化更新, 但修改前必须经过交易员人工确认

