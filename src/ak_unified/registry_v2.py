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
    - symbol: without .SH/.SZ/.BJ suffix
    - start: YYYYMMDD format
    - end: YYYYMMDD format
    """
    symbol = _strip_suffix(p.get("symbol") or p.get("symbols"))
    start = _yyyymmdd(p.get("start")) or "19700101"
    end = _yyyymmdd(p.get("end")) or "22220101"
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


def _easytrader_params(p: Dict[str, Any]) -> Dict[str, Any]:
    """Transform parameters for easytrader adapter.
    
    easytrader expects:
    - username, password, exe_path, comm_password for login
    - start_date, end_date for trading history
    - symbols list for market data
    """
    return {
        "username": p.get("username"),
        "password": p.get("password"),
        "exe_path": p.get("exe_path"),
        "comm_password": p.get("comm_password"),
        "start_date": p.get("start_date") or p.get("start"),
        "end_date": p.get("end_date") or p.get("end"),
        "symbols": p.get("symbols"),
        "broker": p.get("broker", "universal"),
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
    """
    return {
        "symbol": p.get("symbol"),
        "market": p.get("market", "cn"),
        "period": p.get("period", "annual"),
        "limit": p.get("limit", 20),
        "days": p.get("days", 7),
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
        ProviderSpec(adapter="easytrader", api_id="market_data", param_transform=_easytrader_params),
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

# US market datasets
REGISTRY_V2["securities.equity.us.ohlcv_daily"] = DatasetV2(
    dataset_id="securities.equity.us.ohlcv_daily",
    category="securities",
    domain="securities.equity.us",
    providers=[
        ProviderSpec(adapter="yfinance", api_id="download", param_transform=_yfinance_us_params),
        ProviderSpec(adapter="alphavantage", api_id="TIME_SERIES_DAILY", param_transform=_alphavantage_params),
        ProviderSpec(adapter="ibkr", api_id="reqHistoricalData", param_transform=_alphavantage_params),
        ProviderSpec(adapter="easytrader", api_id="market_data", param_transform=_easytrader_params),
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
        ProviderSpec(adapter="easytrader", api_id="market_data", param_transform=_easytrader_params),
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
        ProviderSpec(adapter="easytrader", api_id="market_data", param_transform=_easytrader_params),
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
        ProviderSpec(adapter="easytrader", api_id="market_data", param_transform=_easytrader_params),
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
    ],
)

REGISTRY_V2["macro.cn.ppi"] = DatasetV2(
    dataset_id="macro.cn.ppi",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="macro_china_ppi_yearly", vendor="stats", param_transform=lambda p: {}),
        ProviderSpec(adapter="akshare", api_id="macro_china_ppi_monthly", vendor="stats", param_transform=lambda p: {}),
    ],
)

REGISTRY_V2["macro.cn.gdp"] = DatasetV2(
    dataset_id="macro.cn.gdp",
    category="macro",
    domain="macro.cn",
    providers=[
        ProviderSpec(adapter="akshare", api_id="macro_china_gdp", vendor="stats", param_transform=lambda p: {}),
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
    ],
)

# EasyTrader datasets
REGISTRY_V2["trading.account.info"] = DatasetV2(
    dataset_id="trading.account.info",
    category="trading",
    domain="trading.account",
    providers=[
        ProviderSpec(adapter="easytrader", api_id="account_info", param_transform=_easytrader_params),
    ],
)

REGISTRY_V2["trading.portfolio"] = DatasetV2(
    dataset_id="trading.portfolio",
    category="trading",
    domain="trading.portfolio",
    providers=[
        ProviderSpec(adapter="easytrader", api_id="portfolio", param_transform=_easytrader_params),
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

REGISTRY_V2["research.sentiment"] = DatasetV2(
    dataset_id="research.sentiment",
    category="research",
    domain="research.sentiment",
    providers=[
        ProviderSpec(adapter="snowball", api_id="sentiment", param_transform=_snowball_params),
    ],
)