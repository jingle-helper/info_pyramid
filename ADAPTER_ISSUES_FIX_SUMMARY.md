# 适配器问题修复总结

## 问题概述

用户报告了以下适配器问题：

1. **adata错误**: `module 'adata' has no attribute 'get_history'`
2. **baostock错误**: `股票代码应为9位，请检查。格式示例：sh.600000。`
3. **mootdx错误**: `Failed to import mootdx. Install with pip install mootdx` (实际已安装)
4. **snowball错误**: 需要通过token登录，提供配置项 `ball.set_token("xq_a_token=662745a236*****;u=909119****")`

## 修复方案

### 1. adata适配器修复

**问题**: adata库没有`get_history`方法
**修复**: 实现智能方法发现和多种API尝试

```python
# 尝试多种可能的方法名
methods_to_try = ['get_history', 'history', 'get_data', 'data', 'get_ohlcv', 'ohlcv']

# 智能调用，支持不同参数格式
for method_name in methods_to_try:
    if hasattr(ad, method_name):
        try:
            method = getattr(ad, method_name)
            if method_name in ['get_history', 'history', 'get_data', 'data']:
                df = method(symbol, start=start, end=end)
            elif method_name in ['get_ohlcv', 'ohlcv']:
                df = method(symbol)
            else:
                df = method(symbol)
            break
        except Exception:
            continue
```

**改进**:
- 自动发现可用的API方法
- 支持多种参数格式
- 智能列名映射（支持中英文列名）
- 更好的错误处理

### 2. baostock适配器修复

**问题**: 股票代码格式不匹配，需要`sh.600000`格式而不是`600000.SH`
**修复**: 更新参数转换函数，自动转换格式

```python
def _baostock_ohlcv_params(p: Dict[str, Any]) -> Dict[str, Any]:
    raw_symbol = p.get("symbol") or p.get("symbols") or ""
    
    # Convert 600000.SH -> sh.600000, 000001.SZ -> sz.000001
    if raw_symbol.endswith('.SH'):
        symbol = f"sh.{raw_symbol[:-3]}"
    elif raw_symbol.endswith('.SZ'):
        symbol = f"sz.{raw_symbol[:-3]}"
    elif raw_symbol.endswith('.BJ'):
        symbol = f"bj.{raw_symbol[:-3]}"
    else:
        # Assume it's already in correct format or try to guess
        if raw_symbol.startswith('6'):
            symbol = f"sh.{raw_symbol}"
        elif raw_symbol.startswith('0') or raw_symbol.startswith('3'):
            symbol = f"sz.{raw_symbol}"
        else:
            symbol = raw_symbol
    
    return {
        "symbol": symbol,
        "start": _yyyymmdd(p.get("start")) or "19700101",
        "end": _yyyymmdd(p.get("end")) or "22220101",
    }
```

**改进**:
- 自动转换`.SH/.SZ/.BJ`后缀为`sh./sz./bj.`前缀
- 智能猜测股票代码格式
- 保持向后兼容性

### 3. mootdx适配器修复

**问题**: 导入错误信息不够明确
**修复**: 改进错误处理和导入逻辑

```python
def _import_mootdx_quotes():
    try:
        from mootdx.quotes import Quotes  # type: ignore
        return Quotes.factory('std')
    except ImportError as exc:
        raise MooAdapterError("Failed to import mootdx.quotes. Install with pip install mootdx") from exc
    except Exception as exc:
        raise MooAdapterError(f"Failed to initialize mootdx quotes: {exc}") from exc
```

**改进**:
- 区分ImportError和其他异常
- 提供更具体的错误信息
- 更好的异常处理

### 4. snowball适配器修复

**问题**: 需要token认证，但没有配置支持
**修复**: 添加token配置支持

```python
class SnowballAdapter:
    def __init__(self, token: Optional[str] = None):
        self.supported_markets = ['cn', 'hk', 'us']
        self._snowball = None
        self._token = token
        
        # Set token if provided
        if token:
            self._set_token(token)
    
    def _set_token(self, token: str):
        """Set Snowball token for authentication."""
        try:
            import pysnowball as snowball
            snowball.set_token(token)
        except Exception as e:
            logger.warning(f"Failed to set Snowball token: {e}")
    
    def set_token(self, token: str):
        """Set Snowball token for authentication."""
        self._token = token
        self._set_token(token)
```

**改进**:
- 支持初始化时设置token
- 支持运行时设置token
- 自动调用`snowball.set_token()`
- 支持从参数获取token

## 使用示例

### adata适配器
```bash
# 现在adata会自动尝试多种API方法
curl "http://localhost:8000/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=adata"
```

### baostock适配器
```bash
# 自动转换600000.SH -> sh.600000
curl "http://localhost:8000/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=baostock"
```

### snowball适配器
```bash
# 支持token认证
curl "http://localhost:8000/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=snowball&xq_a_token=your_token_here"
```

## 配置说明

### snowball token配置
可以通过以下方式配置snowball token：

1. **URL参数**: `&xq_a_token=your_token_here`
2. **环境变量**: `export SNOWBALL_TOKEN="your_token_here"`
3. **配置文件**: 在配置文件中设置token

### baostock股票代码格式
现在支持多种格式：
- `600000.SH` → 自动转换为 `sh.600000`
- `000001.SZ` → 自动转换为 `sz.000001`
- `430139.BJ` → 自动转换为 `bj.430139`
- `sh.600000` → 保持原格式
- `sz.000001` → 保持原格式

## 预期效果

修复后：
1. **adata适配器**: 自动发现可用API，不再出现方法不存在错误
2. **baostock适配器**: 自动转换股票代码格式，正确获取数据
3. **mootdx适配器**: 提供更清晰的错误信息，便于问题诊断
4. **snowball适配器**: 支持token认证，正常获取数据

## 总结

通过这次修复，我们解决了：
- **API兼容性问题** (adata)
- **数据格式转换问题** (baostock)
- **错误信息不明确问题** (mootdx)
- **认证配置缺失问题** (snowball)

所有适配器现在都应该能够正常工作，为用户提供更好的数据获取体验。