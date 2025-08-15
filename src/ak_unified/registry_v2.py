from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

ParamTransform = Callable[[Dict[str, any]], Dict[str, any]]
PostProcess = Callable[["pd.DataFrame", Dict[str, any]], "pd.DataFrame"]


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
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist", vendor="eastmoney"),
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist_pre", vendor="eastmoney"),
        ProviderSpec(adapter="efinance", api_id="stock.get_quote_history"),
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
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist", vendor="eastmoney"),
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_hist_pre", vendor="eastmoney"),
        ProviderSpec(adapter="efinance", api_id="stock.get_quote_history"),
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
        ProviderSpec(adapter="akshare", api_id="stock_zh_a_spot_em", vendor="eastmoney"),
        ProviderSpec(adapter="efinance", api_id="stock.get_realtime_quotes"),
        # Temporarily disable qstock
        # ProviderSpec(adapter="qstock", api_id="realtime"),
        ProviderSpec(adapter="yfinance", api_id="Ticker.fast_info"),
    ],
)