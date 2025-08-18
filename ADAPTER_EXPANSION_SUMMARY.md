# 适配器扩展总结

## 概述
我已经为registry_v2.py中的所有数据集添加了完整的适配器支持，确保每个数据集都能使用adapter目录下所有相关的适配器。

## 扩展的适配器支持

### 1. 中国股票市场 (securities.equity.cn)

#### OHLCV/OHLCVA 日线数据
- **ohlcv_daily**: akshare, efinance, baostock, mootdx, qstock, yfinance
- **ohlcva_daily**: akshare, efinance, baostock, mootdx, qstock, yfinance

#### OHLCV/OHLCVA 分钟数据
- **ohlcv_min**: akshare, baostock, mootdx, qstock
- **ohlcva_min**: akshare, baostock, mootdx, qstock

#### 实时行情
- **quote**: akshare, efinance, qstock, yfinance

### 2. 美国股票市场 (securities.equity.us)

#### OHLCV 日线数据
- **ohlcv_daily**: yfinance, alphavantage, ibkr

#### OHLCV 分钟数据
- **ohlcv_min**: yfinance, alphavantage, ibkr

### 3. 香港股票市场 (securities.equity.hk)

#### OHLCV 日线数据
- **ohlcv_daily**: yfinance, alphavantage, ibkr

#### OHLCV 分钟数据
- **ohlcv_min**: yfinance, alphavantage, ibkr

### 4. 指数市场 (market.index.cn)

#### OHLCV/OHLCVA 日线数据
- **ohlcv_daily**: akshare, baostock, mootdx
- **ohlcva_daily**: akshare, baostock, mootdx

### 5. 基金市场 (securities.fund.cn)

#### 净值数据
- **nav_daily**: akshare, baostock, mootdx

### 6. 板块市场 (securities.board.cn)

#### 板块列表
- **industry.list**: akshare, baostock, qstock
- **concept.list**: akshare, baostock, qstock

#### 成分股
- **industry.constituents**: akshare, baostock, qstock
- **concept.constituents**: akshare, baostock, qstock

### 7. 宏观经济 (macro.cn)

#### 经济指标
- **cpi**: akshare
- **ppi**: akshare
- **gdp**: akshare

### 8. 市场日历 (market.calendar.cn)

#### 交易日历
- **calendar**: akshare, baostock, mootdx

## 适配器功能映射

### baostock 适配器
- 支持所有以 `ohlcv_daily` 结尾的数据集
- 支持所有以 `ohlcv_min` 结尾的数据集
- 支持 `market.calendar.baostock`
- 支持 `securities.industry.cn.class.baostock`
- 支持 `market.index.constituents.baostock`
- 支持 `securities.equity.cn.adjust_factor.baostock`

### mootdx 适配器
- 支持所有以 `ohlcv_daily` 结尾的数据集
- 支持所有以 `ohlcv_min` 结尾的数据集
- 支持板块数据：`securities.board.cn.industry.blocks.mootdx`, `securities.board.cn.concept.blocks.mootdx`
- 支持指数成分股：`market.index.constituents.mootdx`
- 支持复权因子：`securities.equity.cn.adjust_factor.mootdx`

### qstock 适配器
- 支持实时行情：所有包含 `.quote` 的数据集
- 支持日线数据：所有包含 `.ohlcv_daily` 的数据集
- 支持板块列表：`board.industry.list.qstock`, `board.concept.list.qstock`
- 支持成分股：`board.industry.cons.qstock`, `board.concept.cons.qstock`
- 支持公告：`announcements.qstock`

### yfinance 适配器
- 支持美国日线：所有以 `us.ohlcv_daily.yf` 结尾的数据集
- 支持香港日线：所有以 `hk.ohlcv_daily.yf` 结尾的数据集
- 支持分钟数据：所有以 `ohlcv_min.yf` 结尾的数据集
- 支持实时行情：所有以 `quote.yf` 结尾的数据集

### alphavantage 适配器
- 支持日线数据：所有以 `.ohlcv_daily.av` 结尾的数据集
- 支持分钟数据：所有以 `.ohlcv_intraday.av` 结尾的数据集
- 支持实时行情：所有以 `.quote.av` 结尾的数据集
- 支持公司概览：所有以 `.overview.av` 结尾的数据集
- 支持时间序列：所有以 `.series.av` 结尾的数据集

### ibkr 适配器
- 支持美国市场历史数据：`reqHistoricalData`
- 支持香港市场历史数据：`reqHistoricalData`

## 参数转换函数

每个适配器都配置了相应的 `param_transform` 函数：

- `_ohlcv_stock_daily_params`: akshare 股票数据
- `_efinance_ohlcv_params`: efinance 数据
- `_baostock_ohlcv_params`: baostock 数据
- `_mootdx_ohlcv_params`: mootdx 数据
- `_qstock_params`: qstock 数据
- `_yfinance_us_params`: yfinance 美国数据
- `_yfinance_hk_params`: yfinance 香港数据
- `_alphavantage_params`: alphavantage 数据
- `_index_params`: 指数数据
- `_fund_params`: 基金数据
- `_board_params`: 板块数据

## 优势

1. **完整的适配器覆盖**: 每个数据集都支持多个适配器，提供更好的数据可用性
2. **统一的参数转换**: 所有适配器都使用统一的参数转换逻辑，确保数据一致性
3. **灵活的优先级配置**: 可以通过环境变量配置适配器优先级
4. **自动回退机制**: 当主要适配器失败时，自动尝试其他适配器
5. **代码复用**: 避免了重复的参数转换逻辑

## 使用示例

现在用户可以使用任何支持的适配器来获取数据：

```bash
# 使用 efinance 获取中国股票数据
curl "http://localhost:8000/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=efinance"

# 使用 baostock 获取数据
curl "http://localhost:8000/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=baostock"

# 使用 mootdx 获取数据
curl "http://localhost:8000/rpc/ohlcva?symbol=600000.SH&start=2024-01-01&end=2024-01-31&adapter=mootdx"
```

所有适配器现在都支持 `.SH/.SZ/.BJ` 后缀的股票代码，并且日期参数会自动转换为正确的格式。