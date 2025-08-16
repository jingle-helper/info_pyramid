# AK Unified - 统一金融数据获取框架

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AK Unified 是一个统一的金融数据获取框架，集成了多个数据源和适配器，提供一致的API接口。

## 🚀 特性

- **多数据源支持**: akshare, baostock, mootdx, qmt, efinance, qstock, adata, yfinance, Alpha Vantage, IBKR
- **统一API接口**: 一致的参数格式和返回数据结构
- **智能路由**: 自动选择最佳数据源，支持fallback机制
- **参数转换**: 自动处理不同数据源的参数格式要求
- **v2架构**: 新的多提供商路由系统，支持adapter优先级和vendor选择
- **高性能**: 异步支持，并发请求处理
- **可扩展**: 易于添加新的数据源和适配器

## 📦 安装

```bash
pip install ak-unified
```

或者从源码安装：

```bash
git clone https://github.com/your-org/ak-unified.git
cd ak-unified
pip install -e .
```

## 🏗️ 架构设计

### v1 架构 (传统)
- 单一数据源路由
- 基于akshare函数名的路由
- 简单的fallback机制

### v2 架构 (新)
- **多提供商路由**: 一个数据集支持多个适配器
- **智能优先级**: 基于环境变量和配置的adapter优先级
- **vendor支持**: 同一适配器的不同数据源选择
- **统一参数转换**: 所有适配器使用一致的参数处理逻辑
- **灵活配置**: 支持数据集级别的adapter和vendor优先级

## 🔧 配置

### 环境变量配置

#### Adapter优先级
```bash
# 全局adapter优先级
export AKU_PROVIDER_PRIORITY="akshare,efinance,yfinance,baostock"

# 特定数据集的adapter优先级
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily="efinance,akshare,yfinance"
```

#### Vendor优先级
```bash
# 特定adapter的vendor优先级
export AKU_VENDOR_PRIORITY__akshare="eastmoney,sina,legulegu"

# 特定数据集和adapter的vendor优先级
export AKU_VENDOR_PRIORITY__securities.equity.cn.ohlcv_daily__akshare="eastmoney,sina"
```

### 配置文件示例

创建 `.env` 文件：

```env
# Adapter优先级配置
AKU_PROVIDER_PRIORITY=akshare,efinance,yfinance,baostock,mootdx

# Vendor优先级配置
AKU_VENDOR_PRIORITY__akshare=eastmoney,sina,legulegu
AKU_VENDOR_PRIORITY__yfinance=yahoo,alpha_vantage

# 特定数据集配置
AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily=efinance,akshare
AKU_VENDOR_PRIORITY__securities.equity.cn.ohlcv_daily__akshare=eastmoney
```

## 📊 支持的数据集

### 股票数据 (Equity)
- **日线数据**: `securities.equity.cn.ohlcv_daily`, `securities.equity.cn.ohlcva_daily`
- **分钟数据**: `securities.equity.cn.ohlcv_min`, `securities.equity.cn.ohlcva_min`
- **实时行情**: `securities.equity.cn.quote`
- **美国市场**: `securities.equity.us.ohlcv_daily`, `securities.equity.us.ohlcv_min`
- **香港市场**: `securities.equity.hk.ohlcv_daily`, `securities.equity.hk.ohlcv_min`

### 指数数据 (Index)
- **日线数据**: `market.index.cn.ohlcv_daily`, `market.index.cn.ohlcva_daily`

### 基金数据 (Fund)
- **净值数据**: `securities.fund.cn.nav_daily`

### 板块数据 (Board)
- **行业列表**: `securities.board.cn.industry.list`
- **概念列表**: `securities.board.cn.concept.list`
- **成分股**: `securities.board.cn.industry.constituents`, `securities.board.cn.concept.constituents`

### 宏观数据 (Macro)
- **CPI**: `macro.cn.cpi`
- **PPI**: `macro.cn.ppi`
- **GDP**: `macro.cn.gdp`

### 市场数据 (Market)
- **交易日历**: `market.calendar.cn`

## 🚀 使用示例

### 基本使用

```python
from ak_unified import fetch_data_v2

# 获取股票日线数据
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"}
)

# 指定adapter
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
    adapter=["efinance"]
)

# 禁用fallback
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
    allow_fallback=False
)
```

### API调用示例

#### 股票数据
```bash
# 日线数据 (v2)
curl "http://localhost:8000/rpc/ohlcv?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=efinance"

# 分钟数据 (v2)
curl "http://localhost:8000/rpc/ohlcv_min?symbol=600000.SH&start=2024-01-01&end=2024-01-31&freq=min5&adapter=efinance"

# OHLCVA数据 (v2)
curl "http://localhost:8000/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=efinance"
```

#### 指数数据
```bash
# 指数日线数据 (v2)
curl "http://localhost:8000/rpc/index_ohlcv?symbol=000300.SH&start=2024-01-01&end=2024-01-31"

# 指数OHLCVA数据 (v2)
curl "http://localhost:8000/rpc/index_ohlcva?symbol=000300.SH&start=2024-01-01&end=2024-01-31"
```

#### 基金数据
```bash
# 基金净值数据 (v2)
curl "http://localhost:8000/rpc/fund_nav?fund_code=000001&start=2024-01-01&end=2024-01-31"
```

#### 板块数据
```bash
# 行业列表 (v2)
curl "http://localhost:8000/rpc/industry_list"

# 概念列表 (v2)
curl "http://localhost:8000/rpc/concept_list"

# 行业成分股 (v2)
curl "http://localhost:8000/rpc/industry_constituents?industry_code=银行"

# 概念成分股 (v2)
curl "http://localhost:8000/rpc/concept_constituents?concept_code=人工智能"
```

#### 海外市场
```bash
# 美国股票数据 (v2)
curl "http://localhost:8000/rpc/us_ohlcv?symbol=AAPL&start=2024-01-01&end=2024-01-31"

# 香港股票数据 (v2)
curl "http://localhost:8000/rpc/hk_ohlcv?symbol=0700.HK&start=2024-01-01&end=2024-01-31"
```

#### 宏观数据
```bash
# CPI数据 (v2)
curl "http://localhost:8000/rpc/macro_cpi"

# PPI数据 (v2)
curl "http://localhost:8000/rpc/macro_ppi"

# GDP数据 (v2)
curl "http://localhost:8000/rpc/macro_gdp"
```

#### 市场数据
```bash
# 交易日历 (v2)
curl "http://localhost:8000/rpc/market_calendar?start=2024-01-01&end=2024-01-31"
```

### 参数转换示例

v2系统自动处理不同适配器的参数格式要求：

```python
# 输入参数
params = {
    "symbol": "600000.SH",  # 带后缀的股票代码
    "start": "2024-01-01",  # 带连字符的日期
    "end": "2024-01-31"
}

# efinance适配器自动转换
# symbol: "600000.SH" → "600000" (去掉.SH后缀)
# start: "2024-01-01" → "20240101" (去掉连字符)
# end: "2024-01-31" → "20240131" (去掉连字符)

# akshare适配器自动转换
# symbol: "600000.SH" → "600000" (去掉.SH后缀)
# start: "2024-01-01" → "20240101" (转换为YYYYMMDD格式)
# end: "2024-01-31" → "20240131" (转换为YYYYMMDD格式)

# mootdx适配器自动转换
# symbol: "600000.SH" → "600000.SH" (保留后缀，内部处理)
# start: "2024-01-01" → "20240101" (转换为YYYYMMDD格式)
# end: "2024-01-31" → "20240131" (转换为YYYYMMDD格式)
```

## 🔌 适配器配置

### 支持的适配器

| 适配器 | 平台支持 | 主要市场 | 特点 |
|--------|----------|----------|------|
| akshare | 跨平台 | 中国 | 功能全面，数据丰富 |
| efinance | 跨平台 | 中国 | 轻量级，响应快速 |
| yfinance | 跨平台 | 美国/香港 | 免费，数据稳定 |
| baostock | 跨平台 | 中国 | 开源，数据准确 |
| mootdx | 跨平台 | 中国 | 本地数据，速度快 |
| qmt | Windows | 中国 | 专业交易软件集成 |
| qstock | 跨平台 | 中国 | 基于R语言 |
| adata | 跨平台 | 中国 | 专业数据服务 |
| Alpha Vantage | 跨平台 | 全球 | 专业金融数据 |
| IBKR | 跨平台 | 全球 | 专业交易平台 |

### 适配器特性

#### 中国市场适配器
- **akshare**: 支持股票、指数、基金、板块、宏观等全品类数据
- **efinance**: 专注于股票数据，响应速度快
- **baostock**: 开源数据源，数据准确度高
- **mootdx**: 基于通达信数据，本地化部署
- **qmt**: Windows专业交易软件集成
- **qstock**: 基于R语言的数据分析工具

#### 海外市场适配器
- **yfinance**: 免费的美股和港股数据
- **Alpha Vantage**: 专业的全球金融数据服务
- **IBKR**: 专业交易平台数据

## 🎯 最佳实践

### 1. Adapter优先级配置
```bash
# 生产环境：优先使用稳定可靠的数据源
export AKU_PROVIDER_PRIORITY="akshare,efinance,baostock"

# 开发环境：优先使用快速响应的数据源
export AKU_PROVIDER_PRIORITY="efinance,akshare,yfinance"

# 特定数据集：针对特定需求优化
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily="efinance,akshare"
export AKU_PROVIDER_PRIORITY__market.index.cn.ohlcv_daily="akshare,baostock"
```

### 2. Vendor选择策略
```bash
# 股票数据：优先使用eastmoney
export AKU_VENDOR_PRIORITY__akshare="eastmoney,sina,legulegu"

# 指数数据：优先使用sina
export AKU_VENDOR_PRIORITY__market.index.cn.ohlcv_daily__akshare="sina,eastmoney"
```

### 3. 错误处理和Fallback
```python
# 启用fallback，确保数据可用性
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
    allow_fallback=True  # 默认启用
)

# 禁用fallback，确保数据一致性
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
    allow_fallback=False
)
```

### 4. 并发请求优化
```python
import asyncio
from ak_unified import fetch_data_v2

async def fetch_multiple_symbols(symbols, start, end):
    tasks = []
    for symbol in symbols:
        task = fetch_data_v2(
            "securities.equity.cn.ohlcv_daily",
            {"symbol": symbol, "start": start, "end": end}
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_v2_routing.py -v

# 运行覆盖率测试
pytest --cov=src/ak_unified --cov-report=html
```

## 📚 文档

- [API参考](docs/API_REFERENCE.md)
- [适配器开发指南](docs/ADAPTER_DEVELOPMENT.md)
- [v2架构设计](docs/V2_ARCHITECTURE.md)
- [配置指南](docs/CONFIGURATION.md)
- [最佳实践](docs/BEST_PRACTICES.md)

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有数据源提供商和开源社区的支持。