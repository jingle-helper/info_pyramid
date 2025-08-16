# AK Unified 配置指南

## 📋 概述

AK Unified 提供了灵活的配置系统，支持通过环境变量、配置文件和环境变量等多种方式进行配置。本指南将详细介绍各种配置选项和使用方法。

## 🔧 配置方式

### 1. 环境变量配置

最直接和灵活的配置方式，支持运行时动态修改：

```bash
# 设置环境变量
export AKU_PROVIDER_PRIORITY="akshare,efinance,yfinance"

# 在Python中使用
import os
os.environ["AKU_PROVIDER_PRIORITY"] = "akshare,efinance,yfinance"
```

### 2. 配置文件配置

使用 `.env` 文件进行配置，支持项目级别的配置管理：

```bash
# 创建.env文件
touch .env

# 编辑.env文件
echo "AKU_PROVIDER_PRIORITY=akshare,efinance,yfinance" >> .env
```

### 3. 代码配置

在代码中直接设置配置：

```python
from ak_unified.config import Config

# 设置配置
Config.set("PROVIDER_PRIORITY", "akshare,efinance,yfinance")
```

## 🎯 核心配置选项

### Adapter优先级配置

控制不同适配器的使用优先级：

#### 全局优先级
```bash
# 设置全局adapter优先级
export AKU_PROVIDER_PRIORITY="akshare,efinance,yfinance,baostock,mootdx"
```

#### 数据集级别优先级
```bash
# 为特定数据集设置adapter优先级
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily="efinance,akshare"
export AKU_PROVIDER_PRIORITY__market.index.cn.ohlcv_daily="akshare,baostock"
export AKU_PROVIDER_PRIORITY__securities.fund.cn.nav_daily="akshare,baostock"
```

#### 优先级规则
1. **数据集级别优先级** > **全局优先级**
2. **数字越小优先级越高**
3. **相同优先级按注册顺序**

### Vendor优先级配置

控制同一适配器内不同数据源提供商的选择：

#### 适配器级别vendor优先级
```bash
# 为akshare设置vendor优先级
export AKU_VENDOR_PRIORITY__akshare="eastmoney,sina,legulegu"

# 为yfinance设置vendor优先级
export AKU_VENDOR_PRIORITY__yfinance="yahoo,alpha_vantage"
```

#### 数据集级别vendor优先级
```bash
# 为特定数据集和adapter设置vendor优先级
export AKU_VENDOR_PRIORITY__securities.equity.cn.ohlcv_daily__akshare="eastmoney,sina"
export AKU_VENDOR_PRIORITY__market.index.cn.ohlcv_daily__akshare="sina,eastmoney"
```

#### Vendor优先级规则
1. **数据集级别vendor优先级** > **适配器级别vendor优先级**
2. **从左到右优先级递减**
3. **支持通配符匹配**

## 📊 数据集配置

### 股票数据配置

#### 日线数据
```bash
# 股票日线数据 - 优先使用efinance
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily="efinance,akshare,yfinance"

# 股票OHLCVA数据 - 优先使用efinance
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcva_daily="efinance,akshare,yfinance"
```

#### 分钟数据
```bash
# 股票分钟数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_min="akshare,baostock,mootdx"

# 股票分钟OHLCVA数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcva_min="akshare,baostock,mootdx"
```

#### 实时行情
```bash
# 实时行情 - 优先使用efinance
export AKU_PROVIDER_PRIORITY__securities.equity.cn.quote="efinance,akshare,yfinance"
```

### 指数数据配置

```bash
# 指数日线数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__market.index.cn.ohlcv_daily="akshare,baostock"

# 指数OHLCVA数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__market.index.cn.ohlcva_daily="akshare,baostock"
```

### 基金数据配置

```bash
# 基金净值数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__securities.fund.cn.nav_daily="akshare,baostock"
```

### 板块数据配置

```bash
# 行业列表 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__securities.board.cn.industry.list="akshare,qstock"

# 概念列表 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__securities.board.cn.concept.list="akshare,qstock"

# 行业成分股 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__securities.board.cn.industry.constituents="akshare,qstock"

# 概念成分股 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__securities.board.cn.concept.constituents="akshare,qstock"
```

### 海外市场配置

#### 美国市场
```bash
# 美股日线数据 - 优先使用yfinance
export AKU_PROVIDER_PRIORITY__securities.equity.us.ohlcv_daily="yfinance,alphavantage"

# 美股分钟数据 - 优先使用yfinance
export AKU_PROVIDER_PRIORITY__securities.equity.us.ohlcv_min="yfinance,alphavantage"
```

#### 香港市场
```bash
# 港股日线数据 - 优先使用yfinance
export AKU_PROVIDER_PRIORITY__securities.equity.hk.ohlcv_daily="yfinance,alphavantage"

# 港股分钟数据 - 优先使用yfinance
export AKU_PROVIDER_PRIORITY__securities.equity.hk.ohlcv_min="yfinance,alphavantage"
```

### 宏观数据配置

```bash
# CPI数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__macro.cn.cpi="akshare"

# PPI数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__macro.cn.ppi="akshare"

# GDP数据 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__macro.cn.gdp="akshare"
```

### 市场数据配置

```bash
# 交易日历 - 优先使用akshare
export AKU_PROVIDER_PRIORITY__market.calendar.cn="akshare,baostock"
```

## 🔑 API密钥配置

### Alpha Vantage
```bash
# 设置Alpha Vantage API密钥
export AKU_ALPHAVANTAGE_API_KEY="your_api_key_here"
export ALPHAVANTAGE_API_KEY="your_api_key_here"  # 兼容性配置
```

### IBKR配置
```bash
# IBKR连接配置
export AKU_IB_HOST="127.0.0.1"
export AKU_IB_PORT="7497"
export AKU_IB_CLIENT_ID="1"
```

## 📝 配置文件示例

### 完整的.env文件示例

```env
# =============================================================================
# AK Unified 配置文件
# =============================================================================

# -----------------------------------------------------------------------------
# Adapter优先级配置
# -----------------------------------------------------------------------------

# 全局adapter优先级
AKU_PROVIDER_PRIORITY=akshare,efinance,yfinance,baostock,mootdx

# 股票数据优先级
AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily=efinance,akshare,yfinance
AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcva_daily=efinance,akshare,yfinance
AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_min=akshare,baostock,mootdx
AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcva_min=akshare,baostock,mootdx
AKU_PROVIDER_PRIORITY__securities.equity.cn.quote=efinance,akshare,yfinance

# 指数数据优先级
AKU_PROVIDER_PRIORITY__market.index.cn.ohlcv_daily=akshare,baostock
AKU_PROVIDER_PRIORITY__market.index.cn.ohlcva_daily=akshare,baostock

# 基金数据优先级
AKU_PROVIDER_PRIORITY__securities.fund.cn.nav_daily=akshare,baostock

# 板块数据优先级
AKU_PROVIDER_PRIORITY__securities.board.cn.industry.list=akshare,qstock
AKU_PROVIDER_PRIORITY__securities.board.cn.concept.list=akshare,qstock
AKU_PROVIDER_PRIORITY__securities.board.cn.industry.constituents=akshare,qstock
AKU_PROVIDER_PRIORITY__securities.board.cn.concept.constituents=akshare,qstock

# 海外市场优先级
AKU_PROVIDER_PRIORITY__securities.equity.us.ohlcv_daily=yfinance,alphavantage
AKU_PROVIDER_PRIORITY__securities.equity.us.ohlcv_min=yfinance,alphavantage
AKU_PROVIDER_PRIORITY__securities.equity.hk.ohlcv_daily=yfinance,alphavantage
AKU_PROVIDER_PRIORITY__securities.equity.hk.ohlcv_min=yfinance,alphavantage

# 宏观数据优先级
AKU_PROVIDER_PRIORITY__macro.cn.cpi=akshare
AKU_PROVIDER_PRIORITY__macro.cn.ppi=akshare
AKU_PROVIDER_PRIORITY__macro.cn.gdp=akshare

# 市场数据优先级
AKU_PROVIDER_PRIORITY__market.calendar.cn=akshare,baostock

# -----------------------------------------------------------------------------
# Vendor优先级配置
# -----------------------------------------------------------------------------

# akshare vendor优先级
AKU_VENDOR_PRIORITY__akshare=eastmoney,sina,legulegu

# yfinance vendor优先级
AKU_VENDOR_PRIORITY__yfinance=yahoo,alpha_vantage

# 特定数据集的vendor优先级
AKU_VENDOR_PRIORITY__securities.equity.cn.ohlcv_daily__akshare=eastmoney,sina
AKU_VENDOR_PRIORITY__market.index.cn.ohlcv_daily__akshare=sina,eastmoney

# -----------------------------------------------------------------------------
# API密钥配置
# -----------------------------------------------------------------------------

# Alpha Vantage API密钥
AKU_ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key_here

# IBKR连接配置
AKU_IB_HOST=127.0.0.1
AKU_IB_PORT=7497
AKU_IB_CLIENT_ID=1

# -----------------------------------------------------------------------------
# 日志配置
# -----------------------------------------------------------------------------

# 日志级别
AKU_LOG_LEVEL=INFO

# 日志格式
AKU_LOG_FORMAT=json

# 日志输出到文件
AKU_LOG_FILE=ak_unified.log

# -----------------------------------------------------------------------------
# 缓存配置
# -----------------------------------------------------------------------------

# 缓存TTL (秒)
AKU_CACHE_TTL_SECONDS=300

# 数据集级别缓存TTL
AKU_CACHE_TTL_PER_DATASET__securities.equity.cn.ohlcv_daily=60
AKU_CACHE_TTL_PER_DATASET__securities.equity.cn.quote=30

# -----------------------------------------------------------------------------
# 限速配置
# -----------------------------------------------------------------------------

# 启用限速
AKU_RATE_LIMIT_ENABLED=1

# Alpha Vantage限速 (请求/分钟)
AKU_AV_RATE_LIMIT_PER_MIN=5

# akshare eastmoney限速 (请求/分钟)
AKU_AKSHARE_EASTMONEY_RATE_LIMIT_PER_MIN=10
```

### 生产环境配置示例

```env
# 生产环境配置 - 优先使用稳定可靠的数据源
AKU_PROVIDER_PRIORITY=akshare,efinance,baostock
AKU_VENDOR_PRIORITY__akshare=eastmoney,sina
AKU_LOG_LEVEL=WARNING
AKU_CACHE_TTL_SECONDS=600
AKU_RATE_LIMIT_ENABLED=1
```

### 开发环境配置示例

```env
# 开发环境配置 - 优先使用快速响应的数据源
AKU_PROVIDER_PRIORITY=efinance,akshare,yfinance
AKU_VENDOR_PRIORITY__akshare=eastmoney
AKU_LOG_LEVEL=DEBUG
AKU_CACHE_TTL_SECONDS=60
AKU_RATE_LIMIT_ENABLED=0
```

### 测试环境配置示例

```env
# 测试环境配置 - 使用模拟数据源
AKU_PROVIDER_PRIORITY=akshare,efinance
AKU_VENDOR_PRIORITY__akshare=eastmoney
AKU_LOG_LEVEL=INFO
AKU_CACHE_TTL_SECONDS=0
AKU_RATE_LIMIT_ENABLED=0
```

## 🚀 动态配置

### 运行时配置修改

```python
import os
from ak_unified import fetch_data_v2

# 动态修改配置
os.environ["AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily"] = "efinance,akshare"

# 配置立即生效
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"}
)
```

### 配置热重载

```python
import os
import time
from ak_unified.config import Config

# 监控配置文件变化
def watch_config_file(config_file=".env"):
    last_modified = os.path.getmtime(config_file)
    
    while True:
        current_modified = os.path.getmtime(config_file)
        if current_modified > last_modified:
            print("配置文件已更新，重新加载...")
            Config.reload()
            last_modified = current_modified
        
        time.sleep(1)

# 启动配置监控
watch_config_file()
```

## 🔍 配置验证

### 配置检查工具

```python
from ak_unified.config import Config

def validate_config():
    """验证配置是否正确"""
    
    # 检查必需的配置
    required_configs = [
        "AKU_PROVIDER_PRIORITY",
        "AKU_VENDOR_PRIORITY__akshare"
    ]
    
    for config in required_configs:
        if not Config.get(config):
            print(f"警告: 缺少配置 {config}")
    
    # 检查adapter优先级配置
    provider_priority = Config.get("AKU_PROVIDER_PRIORITY")
    if provider_priority:
        adapters = provider_priority.split(",")
        print(f"全局adapter优先级: {adapters}")
    
    # 检查vendor优先级配置
    vendor_priority = Config.get("AKU_VENDOR_PRIORITY__akshare")
    if vendor_priority:
        vendors = vendor_priority.split(",")
        print(f"akshare vendor优先级: {vendors}")

# 运行配置验证
validate_config()
```

### 配置测试

```python
from ak_unified import fetch_data_v2

def test_config():
    """测试配置是否正确工作"""
    
    # 测试基本配置
    try:
        result = fetch_data_v2(
            "securities.equity.cn.ohlcv_daily",
            {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"}
        )
        print("✅ 基本配置测试通过")
    except Exception as e:
        print(f"❌ 基本配置测试失败: {e}")
    
    # 测试特定adapter配置
    try:
        result = fetch_data_v2(
            "securities.equity.cn.ohlcv_daily",
            {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
            adapter=["efinance"]
        )
        print("✅ 特定adapter配置测试通过")
    except Exception as e:
        print(f"❌ 特定adapter配置测试失败: {e}")

# 运行配置测试
test_config()
```

## 📚 最佳实践

### 1. 配置组织

- **按环境分离**: 为不同环境创建不同的配置文件
- **模块化配置**: 将相关配置分组到不同的配置文件中
- **版本控制**: 将配置文件纳入版本控制，但排除敏感信息

### 2. 配置命名

- **使用前缀**: 所有配置项使用 `AKU_` 前缀
- **使用下划线**: 使用下划线分隔单词
- **使用层次结构**: 使用双下划线表示层次关系

### 3. 配置安全

- **敏感信息**: 不要在配置文件中存储API密钥等敏感信息
- **环境变量**: 使用环境变量存储敏感信息
- **权限控制**: 确保配置文件的权限设置正确

### 4. 配置监控

- **配置变更**: 监控配置文件的变更
- **配置验证**: 定期验证配置的正确性
- **配置备份**: 定期备份配置文件

## 🔧 故障排除

### 常见问题

#### 1. 配置不生效
```bash
# 检查环境变量是否正确设置
echo $AKU_PROVIDER_PRIORITY

# 检查配置文件是否正确加载
cat .env | grep AKU_PROVIDER_PRIORITY
```

#### 2. 优先级配置错误
```bash
# 检查优先级配置格式
export AKU_PROVIDER_PRIORITY="akshare,efinance,yfinance"

# 检查数据集级别配置
export AKU_PROVIDER_PRIORITY__securities.equity.cn.ohlcv_daily="efinance,akshare"
```

#### 3. Vendor配置错误
```bash
# 检查vendor配置格式
export AKU_VENDOR_PRIORITY__akshare="eastmoney,sina"

# 检查数据集级别vendor配置
export AKU_VENDOR_PRIORITY__securities.equity.cn.ohlcv_daily__akshare="eastmoney"
```

### 调试技巧

#### 1. 启用详细日志
```bash
export AKU_LOG_LEVEL=DEBUG
export AKU_LOG_FORMAT=json
```

#### 2. 检查配置加载
```python
from ak_unified.config import Config

# 打印所有配置
print(Config.get_all())

# 检查特定配置
print(Config.get("AKU_PROVIDER_PRIORITY"))
```

#### 3. 测试配置
```python
# 测试特定配置组合
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
    adapter=["efinance"]
)
```

## 📚 相关文档

- [v2架构设计](V2_ARCHITECTURE.md)
- [最佳实践](../README.md#最佳实践)
- [API参考](../README.md#使用示例)
- [适配器开发指南](ADAPTER_DEVELOPMENT.md)