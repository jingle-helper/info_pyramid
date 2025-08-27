# Core Schema 使用指南

## 概述

AK Unified 现在支持使用 `schemas/core.py` 中定义的标准数据模型来验证和约束各个 adapter 的结果。这确保了所有数据源返回的数据都符合统一的标准格式。

## 核心功能

### 1. 数据验证器 (DataValidator)

`DataValidator` 类提供了将不同数据源的数据转换为标准 core schema 格式的功能：

- **字段映射**: 自动识别不同数据源的字段名称差异
- **数据类型转换**: 确保数据类型符合 schema 要求
- **默认值处理**: 为缺失的必需字段提供合理的默认值
- **数据标准化**: 统一不同数据源的数据格式

### 2. 支持的 Schema 类型

| Schema 类 | 用途 | 主要字段 |
|-----------|------|----------|
| `MacroIndicator` | 宏观经济指标 | region, indicator_id, indicator_name, date, value |
| `MarketQuote` | 市场行情数据 | symbol, datetime, last, open, high, low |
| `OHLCVBar` | K线数据 | symbol, date, open, high, low, close, volume |
| `IndexConstituent` | 指数成分股 | index_symbol, symbol, weight |
| `CapitalFlow` | 资金流向 | symbol, date, main_inflow, main_outflow |
| `TradingCalendar` | 交易日历 | date, is_trading_day, market |
| `CorporateAction` | 公司行为 | symbol, action_type, ex_date |
| `FundNAV` | 基金净值 | fund_code, nav_date, nav |
| `BondQuote` | 债券报价 | symbol, date, yield, duration |
| `FuturesQuote` | 期货报价 | contract, date, open, high, low, close |
| `OptionQuote` | 期权报价 | contract, datetime, last, iv, delta |

## 使用方法

### 1. 在 API 中使用

现有的 API 端点已经集成了 core schema 验证：

```python
# OHLCV 数据会自动验证为 OHLCVBar schema
GET /rpc/ohlcv?symbol=000001.SZ&start=2024-01-01&end=2024-01-31

# 市场行情会自动验证为 MarketQuote schema  
GET /rpc/quote?symbols=000001.SZ

# 基金净值会自动验证为 FundNAV schema
GET /rpc/fund_nav?fund_code=000001&start=2024-01-01&end=2024-01-31

# 宏观经济数据会自动验证为 MacroIndicator schema
GET /rpc/macro_cpi

# 交易日历会自动验证为 TradingCalendar schema
GET /rpc/market_calendar?start=2024-01-01&end=2024-01-31
```

### 2. 在代码中使用验证器

```python
from ak_unified.schemas.validators import DataValidator, validate_dataframe_to_schema
import pandas as pd

# 创建验证器实例
validator = DataValidator()

# 验证单个数据记录
data = {
    'symbol': '000001.SZ',
    'date': '2024-01-01',
    'open': 10.0,
    'high': 10.8,
    'low': 9.8,
    'close': 10.5,
    'volume': 1000000
}

# 验证为 OHLCVBar schema
ohlcv_bar = validator.validate_ohlcv_bar(data)

# 验证 DataFrame
df = pd.DataFrame([data])
validated_records = validate_dataframe_to_schema(df, OHLCVBar)
```

### 3. 测试和调试

使用新的测试端点来验证 core schema 功能：

```bash
# 测试 core schema 验证功能
curl "http://localhost:8000/rpc/test/core_schema"

# 获取 core schema 信息
curl "http://localhost:8000/rpc/schema/core"
```

## 字段映射规则

### 1. 自动字段识别

验证器会自动识别不同数据源的字段名称：

```python
# 对于 OHLCV 数据，以下字段名都会被识别为 'open'
'open', 'open_price', '开盘价'

# 对于日期字段，以下字段名都会被识别为 'date'  
'date', 'datetime', 'time', 'timestamp', '日期'

# 对于成交量字段，以下字段名都会被识别为 'volume'
'volume', 'vol', 'trading_volume', '成交量'
```

### 2. 数据类型标准化

```python
# 周期字段标准化
'period': 'M' | 'Q' | 'Y'  # 月 | 季 | 年

# 复权字段标准化  
'adjust': 'none' | 'qfq' | 'hfq'  # 不复权 | 前复权 | 后复权

# 布尔字段标准化
'is_trading_day': True | False  # 交易日 | 非交易日
```

## 错误处理

### 1. 验证错误

如果数据无法通过验证，系统会：

- 记录验证错误日志
- 跳过无效记录
- 继续处理其他有效记录
- 返回部分验证成功的数据

### 2. 常见错误类型

- **缺失必需字段**: 缺少 symbol, date 等关键字段
- **数据类型不匹配**: 数值字段包含非数字数据
- **字段值无效**: 枚举字段包含未定义的值

## 扩展和自定义

### 1. 添加新的字段映射

```python
# 在 DataValidator 中添加新的字段映射
field_mapping = {
    'target_field': ['source_field1', 'source_field2', 'alias_field']
}
```

### 2. 自定义验证逻辑

```python
# 在验证方法中添加自定义验证逻辑
if target_field == 'custom_field':
    # 自定义验证逻辑
    value = self.custom_validation(value)
```

## 性能考虑

### 1. 批量处理

对于大量数据，建议使用批量验证：

```python
# 批量验证 DataFrame
validated_records = validate_dataframe_to_schema(df, OHLCVBar)
```

### 2. 缓存验证结果

对于重复的数据结构，可以考虑缓存验证结果以提高性能。

## 最佳实践

### 1. 数据源适配

- 确保所有 adapter 返回的数据都能通过 core schema 验证
- 在 adapter 中添加必要的数据转换逻辑
- 处理数据源特有的字段和格式

### 2. 错误监控

- 监控验证失败的情况
- 分析常见的数据质量问题
- 持续改进字段映射规则

### 3. 文档维护

- 及时更新字段映射规则
- 记录数据源特有的字段格式
- 维护验证规则的变更日志

## 总结

通过使用 core schema 验证，AK Unified 现在能够：

1. **统一数据格式**: 所有数据源返回的数据都符合统一标准
2. **提高数据质量**: 自动检测和修复常见的数据问题
3. **简化集成**: 第三方系统可以依赖一致的数据结构
4. **增强可维护性**: 集中管理数据格式定义和验证规则

这为构建可靠、一致的金融数据系统提供了坚实的基础。