# AK Unified v2 架构设计

## 🎯 设计理念

AK Unified v2 是一个全新的多提供商路由系统，旨在解决v1架构的以下问题：

1. **单一数据源限制**: v1只能选择一个数据源，缺乏灵活性
2. **参数转换不一致**: 不同适配器的参数处理逻辑分散在各处
3. **优先级配置困难**: 无法灵活配置不同数据集的adapter优先级
4. **vendor选择缺失**: 同一适配器无法选择不同的数据源提供商
5. **扩展性不足**: 添加新的数据集和适配器需要修改多处代码

## 🏗️ 核心组件

### 1. ProviderSpec

`ProviderSpec` 是v2系统的核心配置类，定义了每个数据提供商的详细配置：

```python
@dataclass
class ProviderSpec:
    adapter: str                    # 适配器名称 (如: akshare, efinance)
    api_id: str                    # API函数ID (如: stock_zh_a_hist)
    vendor: Optional[str] = None   # 数据源提供商 (如: eastmoney, sina)
    priority: Optional[int] = None # 优先级 (数字越小优先级越高)
    param_transform: Optional[ParamTransform] = None  # 参数转换函数
    field_mapping: Optional[Dict[str, str]] = None    # 字段映射
    notes: Optional[str] = None    # 备注信息
```

**关键特性**:
- **adapter**: 指定使用哪个适配器
- **api_id**: 指定适配器内的具体API函数
- **vendor**: 支持同一适配器的不同数据源选择
- **priority**: 支持手动优先级配置
- **param_transform**: 统一的参数转换逻辑
- **field_mapping**: 标准化的字段映射

### 2. DatasetV2

`DatasetV2` 定义了数据集的结构和配置：

```python
@dataclass
class DatasetV2:
    dataset_id: str                    # 数据集ID
    category: str                      # 数据类别 (如: securities, market)
    domain: str                        # 数据域 (如: securities.equity.cn)
    providers: List[ProviderSpec]      # 提供商列表
    postprocess: Optional[PostProcess] = None  # 后处理函数
```

**关键特性**:
- **多提供商支持**: 一个数据集可以配置多个ProviderSpec
- **分类组织**: 按category和domain组织数据集
- **后处理支持**: 支持数据获取后的统一处理

### 3. 参数转换系统

v2系统引入了统一的参数转换机制，解决不同适配器的参数格式差异：

```python
# 参数转换函数类型
ParamTransform = Callable[[Dict[str, Any]], Dict[str, Any]]

# 示例：efinance参数转换
def _efinance_ohlcv_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for efinance adapter.
    efinance expects:
    - symbol: without .SH/.SZ/.BJ suffix
    - start: YYYYMMDD format
    - end: YYYYMMDD format
    """
    symbol = _strip_suffix(p.get("symbol") or p.get("symbols"))
    start = _yyyymmdd(p.get("start")) or "19900101"
    end = _yyyymmdd(p.get("end")) or "20990101"
    return {
        "symbol": symbol,
        "start": start,
        "end": end,
    }
```

**支持的转换类型**:
- **股票代码**: 自动处理`.SH/.SZ/.BJ`后缀
- **日期格式**: 自动转换`YYYY-MM-DD`到`YYYYMMDD`
- **参数映射**: 支持不同参数名的自动映射
- **默认值**: 智能的默认值处理

## 🔄 路由流程

### 1. 请求处理流程

```
用户请求 → API端点 → 数据集识别 → ProviderSpec选择 → 参数转换 → 适配器调用 → 数据返回
```

### 2. 详细步骤

1. **数据集识别**: 根据RPC端点确定对应的dataset_id
2. **ProviderSpec选择**: 从DatasetV2.providers中选择合适的ProviderSpec
3. **优先级排序**: 根据环境变量和配置确定adapter优先级
4. **参数转换**: 使用param_transform函数转换参数
5. **适配器调用**: 调用对应的适配器API
6. **数据返回**: 返回标准化的数据格式

### 3. 优先级机制

优先级按以下顺序确定：

1. **环境变量配置**: `AKU_PROVIDER_PRIORITY__{dataset_id}`
2. **全局配置**: `AKU_PROVIDER_PRIORITY`
3. **ProviderSpec.priority**: 手动设置的优先级
4. **注册顺序**: 在DatasetV2.providers中的顺序

## ⚙️ 配置系统

### 1. 环境变量配置

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

### 2. 配置文件示例

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

## 🚀 使用示例

### 1. 基本数据获取

```python
from ak_unified import fetch_data_v2

# 获取股票日线数据
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"}
)
```

### 2. 指定adapter

```python
# 只使用efinance适配器
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
    adapter=["efinance"]
)
```

### 3. 禁用fallback

```python
# 禁用fallback，确保数据一致性
result = fetch_data_v2(
    "securities.equity.cn.ohlcv_daily",
    {"symbol": "600000.SH", "start": "2024-01-01", "end": "2024-01-31"},
    allow_fallback=False
)
```

## 🔧 扩展开发

### 1. 添加新的参数转换函数

```python
def _new_adapter_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for new adapter."""
    # 实现参数转换逻辑
    return transformed_params

# 在ProviderSpec中使用
ProviderSpec(
    adapter="new_adapter",
    api_id="new_api",
    param_transform=_new_adapter_params
)
```

### 2. 添加新的数据集

```python
REGISTRY_V2["new.dataset.id"] = DatasetV2(
    dataset_id="new.dataset.id",
    category="new_category",
    domain="new.domain",
    providers=[
        ProviderSpec(adapter="akshare", api_id="new_api"),
        ProviderSpec(adapter="efinance", api_id="new_api"),
    ],
)
```

### 3. 添加新的适配器

1. 在 `adapters/` 目录下创建新的适配器文件
2. 实现标准的适配器接口
3. 在 `registry_v2.py` 中注册新的ProviderSpec

## 📊 性能优化

### 1. 缓存策略

- **参数转换缓存**: 相同参数的转换结果会被缓存
- **ProviderSpec缓存**: 数据集配置会被缓存，避免重复解析
- **适配器实例缓存**: 适配器实例会被复用

### 2. 并发处理

- **异步支持**: 支持异步的数据获取
- **并发请求**: 支持多个数据源的并发请求
- **超时控制**: 内置请求超时和重试机制

### 3. 错误处理

- **智能fallback**: 自动切换到备用数据源
- **错误分类**: 区分网络错误、数据错误、配置错误
- **重试机制**: 支持可配置的重试策略

## 🔍 监控和调试

### 1. 日志系统

```python
import logging

# 启用详细日志
logging.getLogger("ak_unified").setLevel(logging.DEBUG)
```

### 2. 性能监控

```python
# 监控数据获取性能
import time

start_time = time.time()
result = fetch_data_v2(dataset_id, params)
end_time = time.time()

print(f"Data fetch took {end_time - start_time:.2f} seconds")
```

### 3. 调试工具

```python
# 查看数据集配置
from ak_unified.registry_v2 import REGISTRY_V2

dataset = REGISTRY_V2["securities.equity.cn.ohlcv_daily"]
print(f"Dataset: {dataset.dataset_id}")
print(f"Providers: {[p.adapter for p in dataset.providers]}")
```

## 🔮 未来规划

### 1. 短期目标

- [ ] 完善更多数据集的v2配置
- [ ] 优化参数转换性能
- [ ] 增强错误处理和重试机制
- [ ] 完善文档和示例

### 2. 中期目标

- [ ] 支持动态配置更新
- [ ] 引入机器学习优化adapter选择
- [ ] 支持数据质量评估
- [ ] 引入数据验证和清洗

### 3. 长期目标

- [ ] 支持分布式部署
- [ ] 引入数据流处理
- [ ] 支持实时数据订阅
- [ ] 构建数据湖架构

## 📚 相关文档

- [API参考](../README.md#使用示例)
- [配置指南](../README.md#配置)
- [最佳实践](../README.md#最佳实践)
- [适配器开发指南](ADAPTER_DEVELOPMENT.md)