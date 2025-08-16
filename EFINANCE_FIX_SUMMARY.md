# Efinance Adapter Symbol Suffix Fix Summary

## 问题描述

当调用 `/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=efinance` 时，没有返回结果。

## 问题分析

### 根本原因
1. **参数处理不一致**：efinance适配器在初始化ProviderSpec时没有传`param_transform`，而akshare适配器有
2. **symbol后缀未处理**：efinance适配器直接使用原始symbol（包含.SH/.SZ/.BJ后缀），但efinance库期望的是不带后缀的代码
3. **date格式处理重复**：efinance适配器内部处理date格式转换，但ProviderSpec层面也应该统一处理

### 具体表现
- akshare的ProviderSpec使用`_ohlcv_stock_daily_params`函数，会调用`_strip_suffix`去掉symbol后缀
- efinance的ProviderSpec没有param_transform，直接传递原始参数
- 在`dispatcher_v2.py`中，efinance调用直接传递原始参数给`call_efinance`
- `call_efinance`函数只处理了date格式转换，但没有处理symbol后缀

## 修复方案

### 1. 统一参数处理
为efinance的ProviderSpec添加`param_transform`，使用专门的`_efinance_ohlcv_params`函数：

```python
def _efinance_ohlcv_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for efinance adapter.
    
    efinance expects:
    - symbol: without .SH/.SZ/.BJ suffix
    - start: YYYYMMDD format
    - end: YYYYMMDD format
    """
    symbol = _strip_suffix(p.get("symbol") or p.get("symbols"))
    start = _yyyymmdd(p.get("start"))
    end = _yyyymmdd(p.get("end"))
    return {
        "symbol": symbol,
        "start": start,
        "end": end,
    }
```

### 2. 移除重复处理
在efinance适配器中移除重复的date格式转换逻辑，因为现在参数转换已经在ProviderSpec层面统一处理。

### 3. 更新ProviderSpec配置
```python
# Before
ProviderSpec(adapter="efinance", api_id="stock.get_quote_history")

# After  
ProviderSpec(adapter="efinance", api_id="stock.get_quote_history", param_transform=_efinance_ohlcv_params)
```

## 修复效果

### 修复前
- symbol: "600000.SH" (带后缀)
- start: "2024-01-01" (带连字符)
- end: "2024-01-31" (带连字符)

### 修复后
- symbol: "600000" (去掉后缀)
- start: "20240101" (去掉连字符)
- end: "20240131" (去掉连字符)

## 代码变更

### 文件：`src/ak_unified/registry_v2.py`
1. 添加了`_efinance_ohlcv_params`函数
2. 添加了`_strip_suffix`和`_yyyymmdd`辅助函数
3. 为efinance的ProviderSpec添加了`param_transform=_efinance_ohlcv_params`

### 文件：`src/ak_unified/adapters/efinance_adapter.py`
1. 移除了重复的date格式转换逻辑
2. 简化了参数处理，依赖ProviderSpec层面的统一处理

## 测试验证

修复后，当调用 `/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=efinance` 时：

1. ProviderSpec的`param_transform`会处理参数：
   - symbol: "600000.SH" → "600000"
   - start: "2024-01-01" → "20240101"
   - end: "2024-01-31" → "20240131"

2. 处理后的参数传递给efinance适配器
3. efinance库接收到正确的参数格式，能够正常返回数据

## 设计原则

这次修复体现了以下设计原则：

1. **统一性**：所有适配器的参数处理都通过ProviderSpec的param_transform统一管理
2. **一致性**：不同适配器对相同参数的处理逻辑保持一致
3. **可维护性**：参数转换逻辑集中管理，便于维护和扩展
4. **职责分离**：ProviderSpec负责参数转换，适配器负责具体的数据获取逻辑

## 总结

通过这次修复，efinance适配器的参数处理行为与akshare等其他适配器保持一致，解决了symbol后缀和date格式处理不一致的问题，确保了API调用的正常返回。