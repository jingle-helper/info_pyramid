from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Any

ParamTransform = Callable[[Dict[str, any]], Dict[str, any]]
PostProcess = Callable[["pd.DataFrame", Dict[str, any]], "pd.DataFrame"]

from .registry import _ohlcv_stock_daily_params, FIELD_OHLCV_CN  # reuse v1 transform and field mapping


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


def _strip_suffix(code: Optional[str]) -> str:
    """Remove .SH/.SZ/.BJ suffix from stock code."""
    if not code:
        return ""
    return code.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")


def _yyyymmdd(date_str: Optional[str]) -> str:
    """Convert date string to YYYYMMDD format."""
    if not date_str:
        return "19900101"
    return date_str.replace("-", "")


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
        # Temporarily disable qstock due to py_mini_racer issues
        # ProviderSpec(adapter="qstock", api_id="history"),
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
        # Temporarily disable qstock
        # ProviderSpec(adapter="qstock", api_id="history"),
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
        # Temporarily disable qstock
        # ProviderSpec(adapter="qstock", api_id="realtime"),
        ProviderSpec(adapter="yfinance", api_id="Ticker.fast_info", param_transform=lambda p: {"symbol": (p.get("symbols") or [None])[0]}),
    ],
)