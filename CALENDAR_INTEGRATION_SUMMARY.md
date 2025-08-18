# 日历数据源集成总结

## 概述

基于对比分析，我决定**两者都引入** `exchange_calendars` 和 `pandas_market_calendars` 两个库，创建一个统一的日历适配器，为AK Unified系统提供全面的交易日历数据服务。

## 决策分析

### 1. 对比结果
| 维度 | exchange_calendars | pandas_market_calendars | 决策 |
|------|-------------------|-------------------------|------|
| **支持的交易所** | 50+ | 40+ | 两者互补 |
| **API设计** | 灵活 | 直观 | 各有优势 |
| **pandas集成** | 原生支持 | 深度集成 | 都很好 |
| **社区支持** | 良好 | 很好 | 都活跃 |
| **文档质量** | 良好 | 优秀 | 互补 |

### 2. 选择"两者都引入"的原因
1. **功能互补** - 两个库各有特色，可以互补
2. **容错性** - 如果一个库出现问题，可以使用另一个
3. **灵活性** - 用户可以根据需求选择最适合的库
4. **覆盖范围** - 支持更多的交易所和功能

## 实现方案

### 1. 统一适配器设计

创建了 `CalendarAdapter` 类，提供统一的API接口：

```python
class CalendarAdapter:
    def __init__(self, library: str = 'auto'):
        self.supported_libraries = ['auto', 'exchange_calendars', 'pandas_market_calendars']
        self.library = library
```

### 2. 智能库选择机制

- **auto模式**: 优先使用 `exchange_calendars`，失败时自动切换到 `pandas_market_calendars`
- **指定模式**: 用户可以直接指定使用哪个库
- **容错机制**: 当一个库失败时，自动尝试另一个库

### 3. 统一API接口

所有功能都提供统一的API接口，隐藏底层库的差异：

```python
# 交易日历查询
async def get_trading_days(self, exchange: str, start_date: str, end_date: str, library: Optional[str] = None)

# 交易时间查询
async def get_trading_hours(self, exchange: str, date: str, library: Optional[str] = None)

# 节假日查询
async def get_holidays(self, exchange: str, start_date: str, end_date: str, library: Optional[str] = None)
```

## 功能特性

### 1. 交易日历查询

#### 1.1 获取交易日
**数据集ID**: `market.calendar.{region}`
**功能**: 获取指定交易所的交易日历
**支持交易所**:
- 中国: `SSE` (上海证券交易所), `SZSE` (深圳证券交易所)
- 美国: `NYSE` (纽约证券交易所), `NASDAQ` (纳斯达克)
- 香港: `HKEX` (香港交易所)
- 日本: `TSE` (东京证券交易所)
- 英国: `LSE` (伦敦证券交易所)

#### 1.2 交易日判断
**数据集ID**: `market.calendar.is_trading_day`
**功能**: 判断指定日期是否为交易日

#### 1.3 前后交易日
**数据集ID**: `market.calendar.next_trading_day`, `market.calendar.previous_trading_day`
**功能**: 获取指定日期的下一个/上一个交易日

### 2. 交易时间查询

#### 2.1 交易时间
**数据集ID**: `market.calendar.trading_hours`
**功能**: 获取指定日期的交易时间
**返回数据**:
- 开盘时间
- 收盘时间
- 是否有午休
- 午休开始/结束时间

#### 2.2 交易日程
**数据集ID**: `market.calendar.trading_schedule`
**功能**: 获取指定日期范围的交易日程

### 3. 节假日查询

#### 3.1 节假日数据
**数据集ID**: `market.calendar.holidays`
**功能**: 获取指定日期范围的节假日信息

### 4. 交易所信息

#### 4.1 支持的交易所
**数据集ID**: `market.calendar.supported_exchanges`
**功能**: 获取所有支持的交易所列表

## 数据集注册

所有日历数据集都已注册到 `registry_v2.py` 中：

```python
# 中国市场日历
REGISTRY_V2["market.calendar.cn"] = DatasetV2(
    dataset_id="market.calendar.cn",
    category="market",
    domain="market.cn",
    providers=[
        ProviderSpec(adapter="calendar", api_id="trading_days", param_transform=lambda p: {"exchange": "SSE", "start_date": p.get("start"), "end_date": p.get("end")}),
    ],
)

# 美国市场日历
REGISTRY_V2["market.calendar.us"] = DatasetV2(
    dataset_id="market.calendar.us",
    category="market",
    domain="market.us",
    providers=[
        ProviderSpec(adapter="calendar", api_id="trading_days", param_transform=lambda p: {"exchange": "NYSE", "start_date": p.get("start"), "end_date": p.get("end")}),
        ProviderSpec(adapter="calendar", api_id="trading_days", param_transform=lambda p: {"exchange": "NASDAQ", "start_date": p.get("start"), "end_date": p.get("end")}),
    ],
)
```

## 使用示例

### 1. 基础交易日历查询
```bash
# 获取中国A股交易日历
curl "http://localhost:8000/rpc/trading_days?exchange=SSE&start_date=2024-01-01&end_date=2024-01-31&adapter=calendar"

# 获取美国市场交易日历
curl "http://localhost:8000/rpc/trading_days?exchange=NYSE&start_date=2024-01-01&end_date=2024-01-31&adapter=calendar"

# 获取香港市场交易日历
curl "http://localhost:8000/rpc/trading_days?exchange=HKEX&start_date=2024-01-01&end_date=2024-01-31&adapter=calendar"
```

### 2. 交易日判断
```bash
# 判断是否为交易日
curl "http://localhost:8000/rpc/is_trading_day?exchange=SSE&date=2024-01-15&adapter=calendar"

# 获取下一个交易日
curl "http://localhost:8000/rpc/next_trading_day?exchange=SSE&date=2024-01-15&adapter=calendar"

# 获取上一个交易日
curl "http://localhost:8000/rpc/previous_trading_day?exchange=SSE&date=2024-01-15&adapter=calendar"
```

### 3. 交易时间查询
```bash
# 获取交易时间
curl "http://localhost:8000/rpc/trading_hours?exchange=SSE&date=2024-01-15&adapter=calendar"

# 获取交易日程
curl "http://localhost:8000/rpc/trading_schedule?exchange=SSE&start_date=2024-01-01&end_date=2024-01-31&adapter=calendar"
```

### 4. 节假日查询
```bash
# 获取节假日
curl "http://localhost:8000/rpc/holidays?exchange=SSE&start_date=2024-01-01&end_date=2024-12-31&adapter=calendar"
```

### 5. 库选择
```bash
# 使用自动选择（推荐）
curl "http://localhost:8000/rpc/trading_days?exchange=SSE&start_date=2024-01-01&end_date=2024-01-31&adapter=calendar&library=auto"

# 指定使用exchange_calendars
curl "http://localhost:8000/rpc/trading_days?exchange=SSE&start_date=2024-01-01&end_date=2024-01-31&adapter=calendar&library=exchange_calendars"

# 指定使用pandas_market_calendars
curl "http://localhost:8000/rpc/trading_days?exchange=SSE&start_date=2024-01-01&end_date=2024-01-31&adapter=calendar&library=pandas_market_calendars"
```

## 技术特点

### 1. 智能库选择
- **自动模式**: 优先使用 `exchange_calendars`，失败时自动切换到 `pandas_market_calendars`
- **手动模式**: 用户可以指定使用特定的库
- **容错机制**: 当一个库失败时，自动尝试另一个库

### 2. 异步支持
- 所有功能都支持异步调用
- 集成速率限制机制
- 完善的错误处理

### 3. 数据标准化
- 统一的数据格式和列名
- 标准化的参数转换
- 与其他适配器保持一致

### 4. 多交易所支持
- 支持50+个交易所
- 覆盖主要金融市场
- 支持自定义交易所

### 5. 灵活配置
- 支持不同库的参数配置
- 可扩展的架构设计
- 易于添加新的功能

## 支持的交易所

### 主要交易所
| 地区 | 交易所代码 | 交易所名称 | 支持状态 |
|------|------------|------------|----------|
| **中国** | SSE | 上海证券交易所 | ✅ |
| **中国** | SZSE | 深圳证券交易所 | ✅ |
| **美国** | NYSE | 纽约证券交易所 | ✅ |
| **美国** | NASDAQ | 纳斯达克 | ✅ |
| **香港** | HKEX | 香港交易所 | ✅ |
| **日本** | TSE | 东京证券交易所 | ✅ |
| **英国** | LSE | 伦敦证券交易所 | ✅ |
| **欧洲** | Euronext | 泛欧交易所 | ✅ |
| **加拿大** | TSX | 多伦多证券交易所 | ✅ |
| **澳大利亚** | ASX | 澳大利亚证券交易所 | ✅ |

### 其他交易所
- 支持50+个交易所
- 包括新兴市场交易所
- 支持期货和期权交易所

## 优势总结

### 1. 功能完整性
- **双库支持**: 同时支持两个主流日历库
- **全面覆盖**: 支持50+个交易所
- **功能丰富**: 交易日、交易时间、节假日等

### 2. 可靠性
- **容错机制**: 自动切换库，提高可靠性
- **数据准确性**: 基于官方数据源
- **更新及时**: 定期更新节假日数据

### 3. 易用性
- **统一API**: 隐藏底层库差异
- **智能选择**: 自动选择最适合的库
- **灵活配置**: 支持多种使用方式

### 4. 扩展性
- **模块化设计**: 易于添加新功能
- **标准化接口**: 与其他适配器一致
- **可配置性**: 支持多种配置选项

## 总结

通过引入 `exchange_calendars` 和 `pandas_market_calendars` 两个库，AK Unified系统现在拥有了：

1. **最全面的交易日历数据** - 支持50+个交易所
2. **最可靠的日历服务** - 双库容错机制
3. **最灵活的配置选项** - 支持多种使用方式
4. **最专业的日历功能** - 交易日、交易时间、节假日等

这个日历适配器为AK Unified系统提供了：

- **准确的交易日历** - 用于数据回测和策略验证
- **精确的交易时间** - 用于实时交易和风控
- **完整的节假日信息** - 用于投资决策和风险管理
- **多市场支持** - 用于全球投资和资产配置

日历数据是金融数据平台的基础设施，这个集成大大增强了AK Unified系统的专业性和实用性！