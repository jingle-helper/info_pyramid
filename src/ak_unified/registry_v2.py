from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Any

ParamTransform = Callable[[Dict[str, any]], Dict[str, any]]
PostProcess = Callable[["pd.DataFrame", Dict[str, any]], "pd.DataFrame"]

from .registry import _ohlcv_stock_daily_params, FIELD_OHLCV_CN, _strip_suffix, _yyyymmdd  # reuse v1 transform and field mapping


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


def _baostock_ohlcv_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for baostock adapter.
    
    baostock expects:
    - symbol: sh.600000 or sz.000001 format
    - start: YYYY-MM-DD format
    - end: YYYY-MM-DD format
    """
    raw_symbol = p.get("symbol") or p.get("symbols") or ""
    if not raw_symbol:
        return {"symbol": "", "start": "1970-01-01", "end": "2222-01-01"}
    
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
    
    # Keep dates in YYYY-MM-DD format for baostock
    start = p.get("start") or "1970-01-01"
    end = p.get("end") or "2222-01-01"
    return {
        "symbol": symbol,
        "start": start,
        "end": end,
    }


def _mootdx_ohlcv_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for mootdx adapter.
    
    mootdx expects:
    - symbol: with .SH/.SZ suffix (it handles suffix internally)
    - start: mootdx uses offset-based approach, so we keep original
    - end: mootdx uses offset-based approach, so we keep original
    """
    # mootdx handles .SH/.SZ suffix internally, so we don't strip it
    symbol = p.get("symbol") or p.get("symbols") or ""
    return {
        "symbol": symbol,
        "start": p.get("start"),
        "end": p.get("end"),
    }


def _yfinance_us_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for yfinance US market.
    
    yfinance expects:
    - symbol: uppercase without suffix
    - start: YYYY-MM-DD format
    - end: YYYY-MM-DD format
    """
    symbol = (p.get("symbol") or "").strip().upper()
    return {
        "symbol": symbol,
        "start": p.get("start"),
        "end": p.get("end"),
    }


def _yfinance_hk_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for yfinance HK market.
    
    yfinance expects:
    - symbol: with .HK suffix, 4-digit code
    - start: YYYY-MM-DD format
    - end: YYYY-MM-DD format
    """
    raw = p.get("symbol") or ""
    s = raw.upper().replace('.HK', '').strip()
    s = s.zfill(4)
    symbol = f"{s}.HK"
    return {
        "symbol": symbol,
        "start": p.get("start"),
        "end": p.get("end"),
    }


def _alphavantage_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for Alpha Vantage adapter.
    
    Alpha Vantage expects:
    - symbol: as provided
    - start: YYYY-MM-DD format
    - end: YYYY-MM-DD format
    """
    return {
        "symbol": p.get("symbol"),
        "start": p.get("start"),
        "end": p.get("end"),
    }


def _qstock_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for qstock adapter.
    
    qstock expects:
    - symbol: without .SH/.SZ/.BJ suffix
    """
    symbol = _strip_suffix(p.get("symbol") or p.get("symbols"))
    return {
        "symbol": symbol,
    }


def _index_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for index datasets.
    
    Handles index codes with .SH/.SZ suffix conversion.
    """
    raw = p.get("symbol") or p.get("index_code")
    if isinstance(raw, str):
        s = raw.upper()
        if s.endswith('.SH') and len(s) >= 9:
            symbol = f"sh{s[:6]}"
        elif s.endswith('.SZ') and len(s) >= 9:
            symbol = f"sz{s[:6]}"
        else:
            symbol = _strip_suffix(raw)
    else:
        symbol = _strip_suffix(raw)
    
    return {
        "symbol": symbol,
        "start": _yyyymmdd(p.get("start")),
        "end": _yyyymmdd(p.get("end")),
    }


def _fund_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for fund datasets.
    
    Handles fund codes and date formatting.
    """
    code = p.get("fund_code") or p.get("symbol")
    start = _yyyymmdd(p.get("start")) or "19700101"
    end = _yyyymmdd(p.get("end")) or "20500101"
    return {
        "symbol": code,
        "start": start,
        "end": end,
    }


def _board_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for board/industry/concept datasets.
    
    Handles board codes and symbols.
    """
    board_code = p.get("board_code") or p.get("symbol")
    return {
        "board_code": board_code,
        "symbol": board_code,
    }


def _adata_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for adata adapter.
    
    adata expects:
    - symbol: without .SH/.SZ/.BJ suffix
    - start: YYYY-MM-DD format
    - end: YYYY-MM-DD format
    """
    symbol = _strip_suffix(p.get("symbol") or p.get("symbols"))
    return {
        "symbol": symbol,
        "start": p.get("start"),
        "end": p.get("end"),
    }





def _qmt_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for qmt adapter.
    
    qmt expects:
    - symbol: without .SH/.SZ/.BJ suffix
    - start: YYYY-MM-DD format
    - end: YYYY-MM-DD format
    """
    symbol = _strip_suffix(p.get("symbol") or p.get("symbols"))
    return {
        "symbol": symbol,
        "start": p.get("start"),
        "end": p.get("end"),
    }


def _snowball_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for snowball adapter.
    
    snowball expects:
    - symbol: as provided
    - market: cn/hk/us
    - period: annual/quarterly for financial data
    - limit: for reports and discussions
    - days: for sentiment analysis
    - token: xq_a_token for authentication
    """
    return {
        "symbol": p.get("symbol"),
        "market": p.get("market", "cn"),
        "period": p.get("period", "annual"),
        "limit": p.get("limit", 20),
        "days": p.get("days", 7),
        "token": p.get("token") or p.get("xq_a_token"),
    }


@dataclass
class ProviderSpec:
    adapter: str
    api_id: str
    vendor: Optional[str] = None
    priority: Optional[int] = None
    param_transform: Optional[ParamTransform] = None
    field_mapping: Optional[Dict[str, str]] = None
    notes: Optional[str] = None


@dataclass
class DatasetV2:
    dataset_id: str
    category: str
    domain: str
    providers: List[ProviderSpec]
    postprocess: Optional[PostProcess] = None


REGISTRY_V2: Dict[str, DatasetV2] = {}

# Pre-register core CN daily datasets with multiple providers (order governed by env)
REGISTRY_V2["securities.equity.cn.ohlcv_daily"] = DatasetV2(
    dataset_id="securities.equity.cn.ohlcv_daily",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist", vendor="eastmoney", param_transform=_ohlcv_stock_daily_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist_pre", vendor="eastmoney", param_transform=_ohlcv_stock_daily_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="efinance", api_id="stock.get_quote_history", param_transform=_efinance_ohlcv_params),
        ProviderSpec(adapter="baostock", api_id="query_history_k_data_plus", param_transform=_baostock_ohlcv_params),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=_mootdx_ohlcv_params),
        ProviderSpec(adapter="qstock", api_id="history", param_transform=_qstock_params),
        ProviderSpec(adapter="adata", api_id="get_history", param_transform=_adata_params),
        ProviderSpec(adapter="qmt", api_id="ohlcv_daily", param_transform=_qmt_params),
        ProviderSpec(adapter="snowball", api_id="stock_quote", param_transform=_snowball_params),
        ProviderSpec(adapter="yfinance", api_id="download"),
    ],
)

REGISTRY_V2["securities.equity.cn.ohlcva_daily"] = DatasetV2(
    dataset_id="securities.equity.cn.ohlcva_daily",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist", vendor="eastmoney", param_transform=_ohlcv_stock_daily_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist_pre", vendor="eastmoney", param_transform=_ohlcv_stock_daily_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="efinance", api_id="stock.get_quote_history", param_transform=_efinance_ohlcv_params),
        ProviderSpec(adapter="baostock", api_id="query_history_k_data_plus", param_transform=_baostock_ohlcv_params),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=_mootdx_ohlcv_params),
        ProviderSpec(adapter="qstock", api_id="history", param_transform=_qstock_params),
        ProviderSpec(adapter="adata", api_id="get_history", param_transform=_adata_params),
        ProviderSpec(adapter="qmt", api_id="ohlcv_daily", param_transform=_qmt_params),
        ProviderSpec(adapter="snowball", api_id="stock_quote", param_transform=_snowball_params),
        ProviderSpec(adapter="yfinance", api_id="download"),
    ],
)

REGISTRY_V2["securities.equity.cn.quote"] = DatasetV2(
    dataset_id="securities.equity.cn.quote",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_spot_em", vendor="eastmoney", param_transform=lambda p: {}),
        ProviderSpec(adapter="efinance", api_id="stock.get_realtime_quotes", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="qstock", api_id="realtime", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="adata", api_id="get_quotes", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="qmt", api_id="quote", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="snowball", api_id="stock_quote", param_transform=_snowball_params),
        ProviderSpec(adapter="easyquotation", api_id="stock_quotes", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="yfinance", api_id="Ticker.fast_info", param_transform=lambda p: {"symbol": (p.get("symbols") or [None])[0]}),
    ],
)

# Minute-level OHLCV/OHLCVA datasets
REGISTRY_V2["securities.equity.cn.ohlcv_min"] = DatasetV2(
    dataset_id="securities.equity.cn.ohlcv_min",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist_min_em", vendor="eastmoney", param_transform=_ohlcv_stock_daily_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="baostock", api_id="query_history_k_data_plus", param_transform=_baostock_ohlcv_params),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=_mootdx_ohlcv_params),
        ProviderSpec(adapter="qstock", api_id="history", param_transform=_qstock_params),
        ProviderSpec(adapter="adata", api_id="get_history", param_transform=_adata_params),
        ProviderSpec(adapter="qmt", api_id="ohlcv_min", param_transform=_qmt_params),
    ],
)

REGISTRY_V2["securities.equity.cn.ohlcva_min"] = DatasetV2(
    dataset_id="securities.equity.cn.ohlcva_min",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist_min_em", vendor="eastmoney", param_transform=_ohlcv_stock_daily_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="baostock", api_id="query_history_k_data_plus", param_transform=_baostock_ohlcv_params),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=_mootdx_ohlcv_params),
        ProviderSpec(adapter="qstock", api_id="history", param_transform=_qstock_params),
        ProviderSpec(adapter="adata", api_id="get_history", param_transform=_adata_params),
        ProviderSpec(adapter="qmt", api_id="ohlcv_min", param_transform=_qmt_params),
    ],
)

# Index datasets
REGISTRY_V2["market.index.cn.ohlcv_daily"] = DatasetV2(
    dataset_id="market.index.cn.ohlcv_daily",
    category="market",
    domain="market.index.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_zh_index_daily", vendor="eastmoney", param_transform=_index_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="baostock", api_id="query_history_k_data_plus", param_transform=_index_params),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=_index_params),
    ],
)

REGISTRY_V2["market.index.cn.ohlcva_daily"] = DatasetV2(
    dataset_id="market.index.cn.ohlcva_daily",
    category="market",
    domain="market.index.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_zh_index_daily", vendor="eastmoney", param_transform=_index_params, field_mapping=FIELD_OHLCV_CN),
        ProviderSpec(adapter="baostock", api_id="query_history_k_data_plus", param_transform=_index_params),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=_index_params),
    ],
)

# Fund datasets
REGISTRY_V2["securities.fund.cn.nav_daily"] = DatasetV2(
    dataset_id="securities.fund.cn.nav_daily",
    category="securities",
    domain="securities.fund.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="fund_open_fund_info_em", vendor="eastmoney", param_transform=_fund_params),
        ProviderSpec(adapter="baostock", api_id="query_history_k_data_plus", param_transform=_fund_params),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=_fund_params),
    ],
)

# Board/Industry/Concept datasets
REGISTRY_V2["securities.board.cn.industry.list"] = DatasetV2(
    dataset_id="securities.board.cn.industry.list",
    category="securities",
    domain="securities.board.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_board_industry_name_em", vendor="eastmoney", param_transform=_board_params),
        ProviderSpec(adapter="baostock", api_id="query_stock_industry", param_transform=_board_params),
        ProviderSpec(adapter="qstock", api_id="industry_list", param_transform=_qstock_params),
    ],
)

REGISTRY_V2["securities.board.cn.concept.list"] = DatasetV2(
    dataset_id="securities.board.cn.concept.list",
    category="securities",
    domain="securities.board.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_board_concept_name_em", vendor="eastmoney", param_transform=_board_params),
        ProviderSpec(adapter="baostock", api_id="query_stock_industry", param_transform=_board_params),
        ProviderSpec(adapter="qstock", api_id="concept_list", param_transform=_qstock_params),
    ],
)

REGISTRY_V2["securities.board.cn.industry.constituents"] = DatasetV2(
    dataset_id="securities.board.cn.industry.constituents",
    category="securities",
    domain="securities.board.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_board_industry_cons_em", vendor="eastmoney", param_transform=_board_params),
        ProviderSpec(adapter="baostock", api_id="query_stock_industry", param_transform=_board_params),
        ProviderSpec(adapter="qstock", api_id="industry_stocks", param_transform=_qstock_params),
    ],
)

REGISTRY_V2["securities.board.cn.concept.constituents"] = DatasetV2(
    dataset_id="securities.board.cn.concept.constituents",
    category="securities",
    domain="securities.board.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_board_concept_cons_em", vendor="eastmoney", param_transform=_board_params),
        ProviderSpec(adapter="baostock", api_id="query_stock_industry", param_transform=_board_params),
        ProviderSpec(adapter="qstock", api_id="concept_stocks", param_transform=_qstock_params),
    ],
)

# QStock fundamentals datasets
REGISTRY_V2["securities.equity.cn.fundamentals.income_statement.qstock"] = DatasetV2(
    dataset_id="securities.equity.cn.fundamentals.income_statement.qstock",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="fundamentals.income_statement.qstock", param_transform=_qstock_params, priority=3),
    ],
)

REGISTRY_V2["securities.equity.cn.fundamentals.balance_sheet.qstock"] = DatasetV2(
    dataset_id="securities.equity.cn.fundamentals.balance_sheet.qstock",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="fundamentals.balance_sheet.qstock", param_transform=_qstock_params, priority=3),
    ],
)

REGISTRY_V2["securities.equity.cn.fundamentals.cash_flow.qstock"] = DatasetV2(
    dataset_id="securities.equity.cn.fundamentals.cash_flow.qstock",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="fundamentals.cash_flow.qstock", param_transform=_qstock_params, priority=3),
    ],
)

REGISTRY_V2["securities.equity.cn.fundamentals.indicators.qstock"] = DatasetV2(
    dataset_id="securities.equity.cn.fundamentals.indicators.qstock",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="fundamentals.indicators.qstock", param_transform=_qstock_params, priority=3),
    ],
)

REGISTRY_V2["securities.equity.cn.fundamentals.earnings_forecast.qstock"] = DatasetV2(
    dataset_id="securities.equity.cn.fundamentals.earnings_forecast.qstock",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="fundamentals.earnings_forecast.qstock", param_transform=_qstock_params, priority=3),
    ],
)

# US market datasets
REGISTRY_V2["securities.equity.us.ohlcv_daily"] = DatasetV2(
    dataset_id="securities.equity.us.ohlcv_daily",
    category="securities",
    domain="securities.equity.us",
    providers=[
        ProviderSpec(adapter="yfinance", api_id="download", param_transform=_yfinance_us_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_DAILY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="ibkr", api_id="reqHistoricalData", param_transform=_alphavantage_params),
        ProviderSpec(adapter="easyquotation", api_id="stock_quotes", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="snowball", api_id="stock_quote", param_transform=_snowball_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_DAILY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
    ],
)

REGISTRY_V2["securities.equity.us.ohlcv_min"] = DatasetV2(
    dataset_id="securities.equity.us.ohlcv_min",
    category="securities",
    domain="securities.equity.us",
    providers=[
        ProviderSpec(adapter="yfinance", api_id="download", param_transform=_yfinance_us_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="ibkr", api_id="reqHistoricalData", param_transform=_alphavantage_params),
        ProviderSpec(adapter="easyquotation", api_id="stock_quotes", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="snowball", api_id="stock_quote", param_transform=_snowball_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
    ],
)

# HK market datasets
REGISTRY_V2["securities.equity.hk.ohlcv_daily"] = DatasetV2(
    dataset_id="securities.equity.hk.ohlcv_daily",
    category="securities",
    domain="securities.equity.hk",
    providers=[
        ProviderSpec(adapter="yfinance", api_id="download", param_transform=_yfinance_hk_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_DAILY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="ibkr", api_id="reqHistoricalData", param_transform=_alphavantage_params),
        ProviderSpec(adapter="easyquotation", api_id="stock_quotes", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="snowball", api_id="stock_quote", param_transform=_snowball_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_DAILY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
    ],
)

REGISTRY_V2["securities.equity.hk.ohlcv_min"] = DatasetV2(
    dataset_id="securities.equity.hk.ohlcv_min",
    category="securities",
    domain="securities.equity.hk",
    providers=[
        ProviderSpec(adapter="yfinance", api_id="download", param_transform=_yfinance_hk_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="ibkr", api_id="reqHistoricalData", param_transform=_alphavantage_params),
        ProviderSpec(adapter="easyquotation", api_id="stock_quotes", param_transform=lambda p: {"symbols": p.get("symbols")}),
        ProviderSpec(adapter="snowball", api_id="stock_quote", param_transform=_snowball_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_INTRADAY", param_transform=_alphavantage_params),
    ],
)

# Macro datasets
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

REGISTRY_V2["macro.cn.ppi"] = DatasetV2(
    dataset_id="macro.cn.ppi",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="macro_china_ppi_yearly", vendor="stats", param_transform=lambda p: {}),
        ProviderSpec(adapter="akshare", api_id="macro_china_ppi_monthly", vendor="stats", param_transform=lambda p: {}),
        ProviderSpec(adapter="qstock", api_id="macro.ppi.qstock", param_transform=lambda p: {}, priority=3),
    ],
)

REGISTRY_V2["macro.cn.gdp"] = DatasetV2(
    dataset_id="macro.cn.gdp",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="macro_china_gdp", vendor="stats", param_transform=lambda p: {}),
        ProviderSpec(adapter="qstock", api_id="macro.gdp.qstock", param_transform=lambda p: {}, priority=3),
    ],
)

# Additional macro datasets via QStock
REGISTRY_V2["macro.cn.pmi"] = DatasetV2(
    dataset_id="macro.cn.pmi",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="macro.pmi.qstock", param_transform=lambda p: {}, priority=3),
    ],
)

REGISTRY_V2["macro.cn.money_supply"] = DatasetV2(
    dataset_id="macro.cn.money_supply",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="macro.money_supply.qstock", param_transform=lambda p: {}, priority=3),
    ],
)

REGISTRY_V2["macro.cn.interest_rates"] = DatasetV2(
    dataset_id="macro.cn.interest_rates",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="macro.interest_rates.qstock", param_transform=lambda p: {}, priority=3),
    ],
)

REGISTRY_V2["macro.cn.exchange_rates"] = DatasetV2(
    dataset_id="macro.cn.exchange_rates",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="macro.exchange_rates.qstock", param_transform=lambda p: {}, priority=3),
    ],
)

REGISTRY_V2["macro.cn.real_estate"] = DatasetV2(
    dataset_id="macro.cn.real_estate",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="qstock", api_id="macro.real_estate.qstock", param_transform=lambda p: {}, priority=3),
    ],
)

# Market calendar
REGISTRY_V2["market.calendar.cn"] = DatasetV2(
    dataset_id="market.calendar.cn",
    category="market",
    domain="market.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="tool_trade_date_hist_sina", vendor="sina", param_transform=lambda p: {}),
        ProviderSpec(adapter="baostock", api_id="query_trade_dates", param_transform=lambda p: {"start": p.get("start"), "end": p.get("end")}),
        ProviderSpec(adapter="mootdx", api_id="bars", param_transform=lambda p: {"start": p.get("start"), "end": p.get("end")}),
        ProviderSpec(adapter="exchange_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "SSE", "start_date": p.get("start"), "end_date": p.get("end")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "SSE", "start_date": p.get("start"), "end_date": p.get("end")}),
    ],
)

# Calendar datasets for different exchanges
REGISTRY_V2["market.calendar.us"] = DatasetV2(
    dataset_id="market.calendar.us",
    category="market",
    domain="market.us",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "NYSE", "start_date": p.get("start"), "end_date": p.get("end")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "NASDAQ", "start_date": p.get("start"), "end_date": p.get("end")}),
    ],
)

REGISTRY_V2["market.calendar.hk"] = DatasetV2(
    dataset_id="market.calendar.hk",
    category="market",
    domain="market.hk",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "HKEX", "start_date": p.get("start"), "end_date": p.get("end")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "HKEX", "start_date": p.get("start"), "end_date": p.get("end")}),
    ],
)

REGISTRY_V2["market.calendar.jp"] = DatasetV2(
    dataset_id="market.calendar.jp",
    category="market",
    domain="market.jp",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "TSE", "start_date": p.get("start"), "end_date": p.get("end")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "TSE", "start_date": p.get("start"), "end_date": p.get("end")}),
    ],
)

REGISTRY_V2["market.calendar.uk"] = DatasetV2(
    dataset_id="market.calendar.uk",
    category="market",
    domain="market.uk",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "LSE", "start_date": p.get("start"), "end_date": p.get("end")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="trading_days", param_transform=lambda p: {"exchange": "LSE", "start_date": p.get("start"), "end_date": p.get("end")}),
    ],
)

# Calendar utility datasets
REGISTRY_V2["market.calendar.trading_hours"] = DatasetV2(
    dataset_id="market.calendar.trading_hours",
    category="market",
    domain="market.calendar",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="trading_hours", param_transform=lambda p: {"exchange": p.get("exchange"), "date": p.get("date")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="trading_hours", param_transform=lambda p: {"exchange": p.get("exchange"), "date": p.get("date")}),
    ],
)

REGISTRY_V2["market.calendar.holidays"] = DatasetV2(
    dataset_id="market.calendar.holidays",
    category="market",
    domain="market.calendar",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="holidays", param_transform=lambda p: {"exchange": p.get("exchange"), "start_date": p.get("start_date"), "end_date": p.get("end_date")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="holidays", param_transform=lambda p: {"exchange": p.get("exchange"), "start_date": p.get("start_date"), "end_date": p.get("end_date")}),
    ],
)

REGISTRY_V2["market.calendar.supported_exchanges"] = DatasetV2(
    dataset_id="market.calendar.supported_exchanges",
    category="market",
    domain="market.calendar",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="supported_exchanges", param_transform=lambda p: {}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="supported_exchanges", param_transform=lambda p: {}),
    ],
)

REGISTRY_V2["market.calendar.next_trading_day"] = DatasetV2(
    dataset_id="market.calendar.next_trading_day",
    category="market",
    domain="market.calendar",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="next_trading_day", param_transform=lambda p: {"exchange": p.get("exchange"), "date": p.get("date")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="next_trading_day", param_transform=lambda p: {"exchange": p.get("exchange"), "date": p.get("date")}),
    ],
)

REGISTRY_V2["market.calendar.previous_trading_day"] = DatasetV2(
    dataset_id="market.calendar.previous_trading_day",
    category="market",
    domain="market.calendar",
    providers=[
        ProviderSpec(adapter="exchange_calendars", api_id="previous_trading_day", param_transform=lambda p: {"exchange": p.get("exchange"), "date": p.get("date")}),
        ProviderSpec(adapter="pandas_market_calendars", api_id="previous_trading_day", param_transform=lambda p: {"exchange": p.get("exchange"), "date": p.get("date")}),
    ],
)

# EasyQuotation datasets (replacing EasyTrader)
REGISTRY_V2["securities.equity.cn.quotes.sina"] = DatasetV2(
    dataset_id="securities.equity.cn.quotes.sina",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="stock_quotes", param_transform=lambda p: {"symbols": p.get("symbols", [])}),
    ],
)

REGISTRY_V2["market.overview.sina"] = DatasetV2(
    dataset_id="market.overview.sina",
    category="market",
    domain="market.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="market_overview", param_transform=lambda p: {}),
    ],
)

REGISTRY_V2["market.sector.sina"] = DatasetV2(
    dataset_id="market.sector.sina",
    category="market",
    domain="market.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="sector_data", param_transform=lambda p: {}),
    ],
)

REGISTRY_V2["securities.equity.cn.rankings.sina"] = DatasetV2(
    dataset_id="securities.equity.cn.rankings.sina",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="stock_rankings", param_transform=lambda p: {"rank_type": p.get("rank_type", "change_percent"), "limit": p.get("limit", 50)}),
    ],
)

# Jisilu bond datasets
REGISTRY_V2["securities.bond.cn.convertible.jisilu"] = DatasetV2(
    dataset_id="securities.bond.cn.convertible.jisilu",
    category="securities",
    domain="securities.bond.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="convertible_bonds", param_transform=lambda p: {}),
    ],
)

REGISTRY_V2["securities.bond.cn.info.jisilu"] = DatasetV2(
    dataset_id="securities.bond.cn.info.jisilu",
    category="securities",
    domain="securities.bond.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="bond_info", param_transform=lambda p: {"bond_code": p.get("bond_code")}),
    ],
)

REGISTRY_V2["securities.bond.cn.yield_curve.jisilu"] = DatasetV2(
    dataset_id="securities.bond.cn.yield_curve.jisilu",
    category="securities",
    domain="securities.bond.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="bond_yield_curve", param_transform=lambda p: {"bond_type": p.get("bond_type", "government")}),
    ],
)

# Tencent and Eastmoney datasets
REGISTRY_V2["securities.equity.cn.quotes.tencent"] = DatasetV2(
    dataset_id="securities.equity.cn.quotes.tencent",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="tencent_quotes", param_transform=lambda p: {"symbols": p.get("symbols", [])}),
    ],
)

REGISTRY_V2["securities.equity.cn.quotes.eastmoney"] = DatasetV2(
    dataset_id="securities.equity.cn.quotes.eastmoney",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="easyquotation", api_id="eastmoney_data", param_transform=lambda p: {"symbols": p.get("symbols", [])}),
    ],
)

# Snowball datasets
REGISTRY_V2["research.financial_data"] = DatasetV2(
    dataset_id="research.financial_data",
    category="research",
    domain="research.financial",
    providers=[
        ProviderSpec(adapter="snowball", api_id="financial_data", param_transform=_snowball_params),
    ],
)

# Earnings datasets (split by concrete providers, no virtual aggregation)
REGISTRY_V2["research.earnings.calendar.cn"] = DatasetV2(
    dataset_id="research.earnings.calendar.cn",
    category="research",
    domain="research.earnings",
    providers=[
        # Baidu report time as broad CN calendar
        ProviderSpec(adapter="akshare", api_id="news_report_time_baidu", vendor="baidu", param_transform=lambda p: {"market": "cn"}),
    ],
)

REGISTRY_V2["research.earnings.calendar.hk"] = DatasetV2(
    dataset_id="research.earnings.calendar.hk",
    category="research",
    domain="research.earnings",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_financial_hk_report_em", vendor="eastmoney", param_transform=lambda p: {}),
    ],
)

REGISTRY_V2["research.earnings.calendar.us"] = DatasetV2(
    dataset_id="research.earnings.calendar.us",
    category="research",
    domain="research.earnings",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_financial_us_report_em", vendor="eastmoney", param_transform=lambda p: {}),
        ProviderSpec(adapter="alphavantage", api_id="EARNINGS_CALENDAR", param_transform=lambda p: {"symbol": (p.get("symbols") or [None])[0], "horizon": p.get("horizon", "3month")}, priority=3),
    ],
)

REGISTRY_V2["research.earnings.dates.cn"] = DatasetV2(
    dataset_id="research.earnings.dates.cn",
    category="research",
    domain="research.earnings",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_financial_abstract", vendor="eastmoney", param_transform=lambda p: {"symbol": p.get("symbol")}),
        ProviderSpec(adapter="akshare", api_id="stock_notice_report", vendor="eastmoney", param_transform=lambda p: {"symbol": p.get("symbol")}, priority=3),
    ],
)

REGISTRY_V2["research.earnings.forecast.cn"] = DatasetV2(
    dataset_id="research.earnings.forecast.cn",
    category="research",
    domain="research.earnings",
    providers=[
        ProviderSpec(adapter="akshare", api_id="stock_profit_forecast_em", vendor="eastmoney", param_transform=lambda p: {"symbol": p.get("symbol")}),
    ],
)

REGISTRY_V2["research.earnings.forecast.us"] = DatasetV2(
    dataset_id="research.earnings.forecast.us",
    category="research",
    domain="research.earnings",
    providers=[
        ProviderSpec(adapter="alphavantage", api_id="EARNINGS", param_transform=lambda p: {"symbol": p.get("symbol")}),
    ],
)

REGISTRY_V2["research.sentiment"] = DatasetV2(
    dataset_id="research.sentiment",
    category="research",
    domain="research.sentiment",
    providers=[
        ProviderSpec(adapter="snowball", api_id="sentiment", param_transform=_snowball_params),
    ],
)

# Additional Snowball datasets for enhanced functionality
REGISTRY_V2["securities.equity.cn.basic_info.snowball"] = DatasetV2(
    dataset_id="securities.equity.cn.basic_info.snowball",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="stock_basic_info", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["securities.equity.cn.volume_price_analysis.snowball"] = DatasetV2(
    dataset_id="securities.equity.cn.volume_price_analysis.snowball",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="volume_price_analysis", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["securities.equity.cn.shareholder_structure.snowball"] = DatasetV2(
    dataset_id="securities.equity.cn.shareholder_structure.snowball",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="shareholder_structure", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["securities.equity.cn.fund_flow.snowball"] = DatasetV2(
    dataset_id="securities.equity.cn.fund_flow.snowball",
    category="securities",
    domain="securities.equity.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="fund_flow", param_transform=_snowball_params),
    ],
)

# Snowball bond datasets
REGISTRY_V2["securities.bond.cn.info.snowball"] = DatasetV2(
    dataset_id="securities.bond.cn.info.snowball",
    category="securities",
    domain="securities.bond.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="bond_info", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["securities.bond.cn.convertible.snowball"] = DatasetV2(
    dataset_id="securities.bond.cn.convertible.snowball",
    category="securities",
    domain="securities.bond.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="convertible_bond_info", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["securities.bond.cn.yield_curve.snowball"] = DatasetV2(
    dataset_id="securities.bond.cn.yield_curve.snowball",
    category="securities",
    domain="securities.bond.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="bond_yield_curve", param_transform=_snowball_params),
    ],
)

# Snowball index datasets
REGISTRY_V2["market.index.cn.info.snowball"] = DatasetV2(
    dataset_id="market.index.cn.info.snowball",
    category="market",
    domain="market.index.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="index_info", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["market.index.cn.constituents.snowball"] = DatasetV2(
    dataset_id="market.index.cn.constituents.snowball",
    category="market",
    domain="market.index.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="index_constituents", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["market.index.cn.sector_weight.snowball"] = DatasetV2(
    dataset_id="market.index.cn.sector_weight.snowball",
    category="market",
    domain="market.index.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="index_sector_weight", param_transform=_snowball_params),
    ],
)

REGISTRY_V2["market.index.cn.industry_weight.snowball"] = DatasetV2(
    dataset_id="market.index.cn.industry_weight.snowball",
    category="market",
    domain="market.index.cn",
    providers=[
        ProviderSpec(adapter="snowball", api_id="index_industry_weight", param_transform=_snowball_params),
    ],
)