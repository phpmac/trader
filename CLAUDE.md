# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/claude-code) when working with code in this repository.

## 交易员核心概念

本项目是专业交易系统, 使用 SMC/ICT (Smart Money Concepts) 分析方法。

### 市场结构
- **BOS** (Break of Structure) - 结构突破确认趋势方向
- **CHoCH** (Change of Character) - 趋势反转信号
- **流动性** - BSL(买方)/SSL(卖方) 止损单聚集区, 机构猎取目标

### 关键价格区域
- **OB** (Order Block) - 机构建仓区域, 反转前最后一根反向K线
- **FVG** (Fair Value Gap) - 价格快速移动形成的缺口/失衡
- **折扣/溢价区** - Fibonacci回撤划分, 折扣区做多/溢价区做空

### 风险管理
- 单笔风险不超过账户 1-2%
- 使用固定风险仓位管理法 (R值法)
- 必须设置止损, 追踪止盈保护盈利

### 交易时段
可交易时间: 07:00-24:00 CST

## 默认交易方法

当前默认使用 **BOS突破交易法** 进行交易分析和执行:

- 技能路径: `.claude/skills/交易方法整理/BOS突破交易法/`
- 核心逻辑: 等待 BOS (Break of Structure) 确认后, 在回调至 OB/FVG 区域时入场
- 详细规则请参考该 skill 的 SKILL.md 文件

### 安全要求
- API 密钥使用环境变量, 禁止硬编码
- 策略必须回测验证后才能实盘
- MCP 工具调用出错时必须停止并报告, 不要绕过
