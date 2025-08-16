# QStock适配器基本面和宏观数据功能完善

## 概述

基于qstock文档（[基本面数据](https://mp.weixin.qq.com/s/XznS8hFMEa47x1IElZXJaA) 和 [宏观数据](https://mp.weixin.qq.com/s/vq7BJUCdHMkcgJYjsErpYQ)），我对qstock适配器进行了全面的功能完善，补充了基本面和宏观数据的维度和指标。

## 完善内容

### 1. 基本面数据 (Fundamentals)

#### 1.1 财务报表 - 利润表
**数据集ID**: `securities.equity.cn.fundamentals.income_statement.qstock`
**API方法**: `qs.financial_data(symbol, '利润表')`

**主要指标**:
- **收入相关**: 营业总收入、营业收入、主营业务收入
- **成本相关**: 营业总成本、营业成本、销售费用、管理费用、财务费用、研发费用
- **利润相关**: 营业利润、利润总额、净利润、归母净利润
- **每股指标**: 基本每股收益、稀释每股收益

#### 1.2 财务报表 - 资产负债表
**数据集ID**: `securities.equity.cn.fundamentals.balance_sheet.qstock`
**API方法**: `qs.financial_data(symbol, '资产负债表')`

**主要指标**:
- **资产相关**: 货币资金、应收账款、存货、流动资产合计、非流动资产合计、资产总计
- **负债相关**: 流动负债合计、非流动负债合计、负债合计
- **权益相关**: 所有者权益(或股东权益)合计

#### 1.3 财务报表 - 现金流量表
**数据集ID**: `securities.equity.cn.fundamentals.cash_flow.qstock`
**API方法**: `qs.financial_data(symbol, '现金流量表')`

**主要指标**:
- **经营活动**: 经营活动现金流量净额
- **投资活动**: 投资活动产生的现金流量净额
- **筹资活动**: 筹资活动产生的现金流量净额
- **现金变化**: 现金及现金等价物净增加额

#### 1.4 财务指标
**数据集ID**: `securities.equity.cn.fundamentals.indicators.qstock`
**API方法**: `qs.financial_data(symbol, '财务指标')`

**主要指标**:
- **盈利能力**: 净资产收益率(ROE)、总资产收益率(ROA)、销售净利率
- **偿债能力**: 资产负债率、流动比率、速动比率
- **营运能力**: 存货周转率、应收账款周转率、总资产周转率
- **每股指标**: 每股净资产

#### 1.5 业绩预告
**数据集ID**: `securities.equity.cn.fundamentals.earnings_forecast.qstock`
**API方法**: `qs.earnings_forecast(symbol)`

**主要指标**:
- **预告信息**: 预告类型、预告净利润、预告净利润变动幅度
- **对比数据**: 上年同期净利润

### 2. 宏观数据 (Macro)

#### 2.1 宏观经济指标
**数据集ID**: `macro.cn.indicators.qstock`
**API方法**: `qs.macro_data()`

**主要指标**:
- 指标名称、指标值、单位、发布时间、数据来源

#### 2.2 CPI数据
**数据集ID**: `macro.cn.cpi.qstock`
**API方法**: `qs.macro_data('CPI')`

**主要指标**:
- **CPI指标**: CPI同比、CPI环比、CPI累计、核心CPI同比

#### 2.3 PPI数据
**数据集ID**: `macro.cn.ppi.qstock`
**API方法**: `qs.macro_data('PPI')`

**主要指标**:
- **PPI指标**: PPI同比、PPI环比、PPI累计
- **分类指标**: 生产资料PPI、生活资料PPI

#### 2.4 GDP数据
**数据集ID**: `macro.cn.gdp.qstock`
**API方法**: `qs.macro_data('GDP')`

**主要指标**:
- **GDP指标**: GDP绝对值、GDP同比、GDP环比
- **产业分类**: 第一产业、第二产业、第三产业

#### 2.5 PMI数据
**数据集ID**: `macro.cn.pmi.qstock`
**API方法**: `qs.macro_data('PMI')`

**主要指标**:
- **综合指标**: 制造业PMI、非制造业PMI、综合PMI
- **分项指标**: 新订单指数、生产指数、从业人员指数

#### 2.6 货币供应量
**数据集ID**: `macro.cn.money_supply.qstock`
**API方法**: `qs.macro_data('货币供应量')`

**主要指标**:
- **货币指标**: M0、M1、M2
- **同比指标**: M1同比、M2同比、M1-M2剪刀差

#### 2.7 利率数据
**数据集ID**: `macro.cn.interest_rates.qstock`
**API方法**: `qs.macro_data('利率')`

**主要指标**:
- **LPR利率**: 1年期LPR、5年期LPR
- **基准利率**: 1年期存款基准利率、1年期贷款基准利率
- **政策利率**: 7天逆回购利率、MLF利率

#### 2.8 汇率数据
**数据集ID**: `macro.cn.exchange_rates.qstock`
**API方法**: `qs.macro_data('汇率')`

**主要指标**:
- **主要货币**: 美元兑人民币、欧元兑人民币、日元兑人民币、英镑兑人民币
- **指数指标**: 美元指数、人民币汇率指数

#### 2.9 房地产数据
**数据集ID**: `macro.cn.real_estate.qstock`
**API方法**: `qs.macro_data('房地产')`

**主要指标**:
- **投资指标**: 房地产开发投资
- **销售指标**: 商品房销售面积、商品房销售额
- **价格指标**: 70城房价指数
- **土地指标**: 土地购置面积

## 技术实现

### 1. 列名标准化
所有数据集都实现了中文列名到英文标准列名的映射，确保数据的一致性和可读性。

```python
# 示例：利润表列名映射
column_mapping = {
    '营业总收入': 'revenue_total',
    '营业收入': 'revenue',
    '主营业务收入': 'revenue_main',
    '营业总成本': 'operating_cost_total',
    # ... 更多映射
}
```

### 2. 错误处理
每个数据集都实现了完善的错误处理机制，提供详细的错误信息。

```python
try:
    df = qs.financial_data(symbol, '利润表')
    # 数据处理逻辑
except Exception as exc:
    raise QStockAdapterError(f"Failed to fetch income statement: {exc}") from exc
```

### 3. 数据验证
实现了数据完整性检查，确保返回的数据不为空且格式正确。

```python
if isinstance(df, pd.DataFrame) and not df.empty:
    # 列名标准化和数据插入
    df.insert(0, 'symbol', symbol)
    return ('qstock.income_statement', df)
else:
    return ('qstock.income_statement', pd.DataFrame([]))
```

## 数据集注册

### 1. 基本面数据集
所有基本面数据集都已注册到`registry_v2.py`中，支持v2调度系统：

```python
REGISTRY_V2["securities.equity.cn.fundamentals.income_statement.qstock"] = DatasetV2(
    dataset_id="securities.equity.cn.fundamentals.income_statement.qstock",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="fundamentals.income_statement.qstock", param_transform=_qstock_params, priority=3),
    ],
)
```

### 2. 宏观数据集
宏观数据集也已注册，部分数据集（如CPI、PPI、GDP）还支持akshare作为备选数据源：

```python
REGISTRY_V2["macro.cn.cpi"] = DatasetV2(
    dataset_id="macro.cn.cpi",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="macro_china_cpi_yearly", vendor="stats", param_transform=lambda p: {}),
        ProviderSpec(adapter="akshare", api_id="macro_china_cpi_monthly", vendor="stats", param_transform=lambda p: {}),
        ProviderSpec(adapter="qstock", api_id="macro.cpi.qstock", param_transform=lambda p: {}, priority=3),
    ],
)
```

## 使用示例

### 1. 基本面数据
```bash
# 获取利润表数据
curl "http://localhost:8000/rpc/fundamentals_income_statement?symbol=600000.SH&adapter=qstock"

# 获取资产负债表数据
curl "http://localhost:8000/rpc/fundamentals_balance_sheet?symbol=600000.SH&adapter=qstock"

# 获取现金流量表数据
curl "http://localhost:8000/rpc/fundamentals_cash_flow?symbol=600000.SH&adapter=qstock"
```

### 2. 宏观数据
```bash
# 获取CPI数据
curl "http://localhost:8000/rpc/macro_cpi?adapter=qstock"

# 获取GDP数据
curl "http://localhost:8000/rpc/macro_gdp?adapter=qstock"

# 获取PMI数据
curl "http://localhost:8000/rpc/macro_pmi?adapter=qstock"
```

## 对比现有实现

### 1. 基本面数据对比
| 维度 | 现有实现 | QStock补充 | 优势 |
|------|----------|------------|------|
| 财务报表 | 基础指标 | 完整三表 | 更全面的财务数据 |
| 财务指标 | 核心指标 | 详细分类 | 更专业的财务分析 |
| 业绩预告 | 无 | 完整支持 | 新增功能 |
| 数据更新 | 依赖akshare | 多数据源 | 更高的可用性 |

### 2. 宏观数据对比
| 维度 | 现有实现 | QStock补充 | 优势 |
|------|----------|------------|------|
| 基础指标 | CPI、PPI、GDP、PMI | 完整覆盖 | 更全面的宏观视角 |
| 货币金融 | 无 | 货币供应量、利率 | 新增金融指标 |
| 汇率数据 | 无 | 主要货币对 | 新增汇率指标 |
| 房地产 | 无 | 投资、销售、价格 | 新增房地产指标 |

## 总结

通过这次完善，qstock适配器现在提供了：

1. **完整的基本面数据**: 涵盖财务报表、财务指标、业绩预告等
2. **全面的宏观数据**: 包括经济指标、货币金融、汇率、房地产等
3. **标准化的数据格式**: 统一的列名和数据结构
4. **完善的错误处理**: 稳定的数据获取体验
5. **v2系统支持**: 完全集成到新的调度系统中

这些功能使qstock成为AK Unified系统中重要的数据源补充，为用户提供更丰富、更专业的金融数据服务。