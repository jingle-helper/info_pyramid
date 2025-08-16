from __future__ import annotations

from typing import Any, Dict, Tuple, Optional, List

import pandas as pd


class QStockAdapterError(RuntimeError):
    pass


def _import_qstock():
    try:
        import qstock as qs  # type: ignore
        return qs
    except Exception as exc:
        raise QStockAdapterError("Failed to import qstock. Install with pip install qstock") from exc


def _to_df(obj: Any) -> pd.DataFrame:
    if isinstance(obj, pd.DataFrame):
        return obj
    if isinstance(obj, list):
        return pd.DataFrame(obj)
    if isinstance(obj, dict):
        return pd.DataFrame([obj])
    return pd.DataFrame([])


def call_qstock(dataset_id: str, params: Dict[str, Any]) -> Tuple[str, pd.DataFrame]:
    qs = _import_qstock()
    # Realtime quotes
    if '.quote' in dataset_id:
        symbols: Optional[List[str]] = params.get('symbols')
        try:
            df = qs.realtime(symbols) if symbols else qs.realtime()
        except Exception as exc:
            raise QStockAdapterError(str(exc)) from exc
        df = _to_df(df)
        if not df.empty:
            df = df.rename(columns={'代码': 'symbol', '名称': 'symbol_name', '最新': 'last', '涨幅': 'pct_change', '成交': 'amount'})
        return ('qstock.realtime', df)
    # Daily history (OHLCV/OHLCVA)
    if '.ohlcv_daily' in dataset_id or '.ohlcva_daily' in dataset_id:
        symbol = params.get('symbol')
        try:
            df = qs.history(symbol)
        except Exception as exc:
            raise QStockAdapterError(str(exc)) from exc
        df = _to_df(df)
        if not df.empty:
            df = df.rename(columns={'日期': 'date', '开盘': 'open', '最高': 'high', '最低': 'low', '收盘': 'close', '成交额': 'amount'})
            df.insert(0, 'symbol', symbol)
        return ('qstock.history', df)

    # Industry/Concept lists
    if dataset_id.endswith('board.industry.list.qstock'):
        try:
            df = _to_df(qs.industries()) if hasattr(qs, 'industries') else _to_df(qs.block_list('industry'))
        except Exception as exc:
            raise QStockAdapterError(str(exc)) from exc
        return ('qstock.industries', df)

    if dataset_id.endswith('board.concept.list.qstock'):
        try:
            df = _to_df(qs.concepts()) if hasattr(qs, 'concepts') else _to_df(qs.block_list('concept'))
        except Exception as exc:
            raise QStockAdapterError(str(exc)) from exc
        return ('qstock.concepts', df)

    # Constituents
    if dataset_id.endswith('board.industry.cons.qstock') or dataset_id.endswith('board.concept.cons.qstock'):
        code = params.get('board_code') or params.get('symbol')
        try:
            if hasattr(qs, 'block_stocks'):
                df = _to_df(qs.block_stocks(code))
            else:
                df = _to_df(qs.members(code))
        except Exception as exc:
            raise QStockAdapterError(str(exc)) from exc
        if not df.empty:
            df = df.rename(columns={'代码': 'symbol', '名称': 'symbol_name', '权重': 'weight'})
        return ('qstock.block_members', df)

    # Announcements
    if dataset_id.endswith('announcements.qstock'):
        symbol = params.get('symbol')
        try:
            fn = getattr(qs, 'announcements', None)
            df = _to_df(fn(symbol)) if fn else _to_df([])
        except Exception as exc:
            raise QStockAdapterError(str(exc)) from exc
        return ('qstock.announcements', df)

    # ========== 基本面数据 (Fundamentals) ==========
    
    # 财务报表 - 利润表
    if dataset_id.endswith('fundamentals.income_statement.qstock'):
        symbol = params.get('symbol')
        try:
            # 获取利润表数据
            df = qs.financial_data(symbol, '利润表')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '报告期': 'period', '日期': 'period', '公告日期': 'period',
                    '营业总收入': 'revenue_total', '营业收入': 'revenue', '主营业务收入': 'revenue_main',
                    '营业总成本': 'operating_cost_total', '营业成本': 'cost_of_revenue',
                    '销售费用': 'selling_expense', '管理费用': 'admin_expense',
                    '财务费用': 'financial_expense', '研发费用': 'rd_expense',
                    '营业利润': 'operating_profit', '利润总额': 'total_profit',
                    '净利润': 'net_profit', '归母净利润': 'net_profit_parent',
                    '基本每股收益': 'eps_basic', '稀释每股收益': 'eps_diluted'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
                df.insert(0, 'symbol', symbol)
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch income statement: {exc}") from exc
        return ('qstock.income_statement', df)

    # 财务报表 - 资产负债表
    if dataset_id.endswith('fundamentals.balance_sheet.qstock'):
        symbol = params.get('symbol')
        try:
            # 获取资产负债表数据
            df = qs.financial_data(symbol, '资产负债表')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '报告期': 'period', '日期': 'period', '公告日期': 'period',
                    '货币资金': 'cash_and_equivalents', '应收账款': 'accounts_receivable',
                    '存货': 'inventory', '流动资产合计': 'current_assets_total',
                    '非流动资产合计': 'noncurrent_assets_total', '资产总计': 'assets_total',
                    '流动负债合计': 'current_liabilities_total', '非流动负债合计': 'noncurrent_liabilities_total',
                    '负债合计': 'liabilities_total', '所有者权益(或股东权益)合计': 'equity_total'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
                df.insert(0, 'symbol', symbol)
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch balance sheet: {exc}") from exc
        return ('qstock.balance_sheet', df)

    # 财务报表 - 现金流量表
    if dataset_id.endswith('fundamentals.cash_flow.qstock'):
        symbol = params.get('symbol')
        try:
            # 获取现金流量表数据
            df = qs.financial_data(symbol, '现金流量表')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '报告期': 'period', '日期': 'period', '公告日期': 'period',
                    '经营活动现金流量净额': 'cfo_net', '投资活动产生的现金流量净额': 'cfi_net',
                    '筹资活动产生的现金流量净额': 'cff_net', '现金及现金等价物净增加额': 'cash_net_change'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
                df.insert(0, 'symbol', symbol)
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch cash flow: {exc}") from exc
        return ('qstock.cash_flow', df)

    # 财务指标
    if dataset_id.endswith('fundamentals.indicators.qstock'):
        symbol = params.get('symbol')
        try:
            # 获取财务指标数据
            df = qs.financial_data(symbol, '财务指标')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '报告期': 'period', '日期': 'period', '公告日期': 'period',
                    '净资产收益率': 'roe', '总资产收益率': 'roa', '销售净利率': 'net_profit_margin',
                    '资产负债率': 'debt_to_equity', '流动比率': 'current_ratio', '速动比率': 'quick_ratio',
                    '存货周转率': 'inventory_turnover', '应收账款周转率': 'receivables_turnover',
                    '总资产周转率': 'asset_turnover', '每股净资产': 'book_value_per_share'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
                df.insert(0, 'symbol', symbol)
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch financial indicators: {exc}") from exc
        return ('qstock.financial_indicators', df)

    # 业绩预告
    if dataset_id.endswith('fundamentals.earnings_forecast.qstock'):
        symbol = params.get('symbol')
        try:
            # 获取业绩预告数据
            df = qs.earnings_forecast(symbol)
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '报告期': 'period', '日期': 'period', '公告日期': 'period',
                    '预告类型': 'forecast_type', '预告净利润': 'forecast_net_profit',
                    '预告净利润变动幅度': 'forecast_profit_change_pct', '上年同期净利润': 'prior_year_profit'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
                df.insert(0, 'symbol', symbol)
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch earnings forecast: {exc}") from exc
        return ('qstock.earnings_forecast', df)

    # ========== 宏观数据 (Macro) ==========
    
    # 宏观经济指标
    if dataset_id.endswith('macro.indicators.qstock'):
        try:
            # 获取宏观经济指标数据
            df = qs.macro_data()
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '指标名称': 'indicator_name', '指标值': 'indicator_value',
                    '单位': 'unit', '发布时间': 'release_time', '数据来源': 'data_source'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch macro indicators: {exc}") from exc
        return ('qstock.macro_indicators', df)

    # CPI数据
    if dataset_id.endswith('macro.cpi.qstock'):
        try:
            # 获取CPI数据
            df = qs.macro_data('CPI')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '月份': 'month', 'CPI同比': 'cpi_yoy', 'CPI环比': 'cpi_mom',
                    'CPI累计': 'cpi_ytd', '核心CPI同比': 'core_cpi_yoy'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch CPI data: {exc}") from exc
        return ('qstock.macro_cpi', df)

    # PPI数据
    if dataset_id.endswith('macro.ppi.qstock'):
        try:
            # 获取PPI数据
            df = qs.macro_data('PPI')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '月份': 'month', 'PPI同比': 'ppi_yoy', 'PPI环比': 'ppi_mom',
                    'PPI累计': 'ppi_ytd', '生产资料PPI': 'ppi_production_materials',
                    '生活资料PPI': 'ppi_consumer_goods'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch PPI data: {exc}") from exc
        return ('qstock.macro_ppi', df)

    # GDP数据
    if dataset_id.endswith('macro.gdp.qstock'):
        try:
            # 获取GDP数据
            df = qs.macro_data('GDP')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '年份': 'year', '季度': 'quarter', 'GDP绝对值': 'gdp_absolute',
                    'GDP同比': 'gdp_yoy', 'GDP环比': 'gdp_qoq', '第一产业': 'gdp_primary',
                    '第二产业': 'gdp_secondary', '第三产业': 'gdp_tertiary'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch GDP data: {exc}") from exc
        return ('qstock.macro_gdp', df)

    # PMI数据
    if dataset_id.endswith('macro.pmi.qstock'):
        try:
            # 获取PMI数据
            df = qs.macro_data('PMI')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '月份': 'month', '制造业PMI': 'manufacturing_pmi', '非制造业PMI': 'non_manufacturing_pmi',
                    '综合PMI': 'composite_pmi', '新订单指数': 'new_orders_index',
                    '生产指数': 'production_index', '从业人员指数': 'employment_index'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch PMI data: {exc}") from exc
        return ('qstock.macro_pmi', df)

    # 货币供应量
    if dataset_id.endswith('macro.money_supply.qstock'):
        try:
            # 获取货币供应量数据
            df = qs.macro_data('货币供应量')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '月份': 'month', 'M0': 'm0', 'M1': 'm1', 'M2': 'm2',
                    'M1同比': 'm1_yoy', 'M2同比': 'm2_yoy', 'M1-M2剪刀差': 'm1_m2_scissors'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch money supply data: {exc}") from exc
        return ('qstock.macro_money_supply', df)

    # 利率数据
    if dataset_id.endswith('macro.interest_rates.qstock'):
        try:
            # 获取利率数据
            df = qs.macro_data('利率')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '日期': 'date', '1年期LPR': 'lpr_1y', '5年期LPR': 'lpr_5y',
                    '1年期存款基准利率': 'deposit_rate_1y', '1年期贷款基准利率': 'loan_rate_1y',
                    '7天逆回购利率': 'repo_rate_7d', 'MLF利率': 'mlf_rate'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch interest rates data: {exc}") from exc
        return ('qstock.macro_interest_rates', df)

    # 汇率数据
    if dataset_id.endswith('macro.exchange_rates.qstock'):
        try:
            # 获取汇率数据
            df = qs.macro_data('汇率')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '日期': 'date', '美元兑人民币': 'usd_cny', '欧元兑人民币': 'eur_cny',
                    '日元兑人民币': 'jpy_cny', '英镑兑人民币': 'gbp_cny',
                    '美元指数': 'dollar_index', '人民币汇率指数': 'cny_index'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch exchange rates data: {exc}") from exc
        return ('qstock.macro_exchange_rates', df)

    # 房地产数据
    if dataset_id.endswith('macro.real_estate.qstock'):
        try:
            # 获取房地产数据
            df = qs.macro_data('房地产')
            df = _to_df(df)
            if not df.empty:
                # 标准化列名
                column_mapping = {
                    '月份': 'month', '房地产开发投资': 'real_estate_investment',
                    '商品房销售面积': 'commercial_housing_sales_area', '商品房销售额': 'commercial_housing_sales_amount',
                    '70城房价指数': 'house_price_index_70cities', '土地购置面积': 'land_acquisition_area'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
        except Exception as exc:
            raise QStockAdapterError(f"Failed to fetch real estate data: {exc}") from exc
        return ('qstock.macro_real_estate', df)

    return ('qstock.unsupported', pd.DataFrame([]))