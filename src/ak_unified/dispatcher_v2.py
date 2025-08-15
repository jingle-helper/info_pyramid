from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from .registry_v2 import ProviderSpec
from .resolver import resolve_providers
from .logging import logger


def _dispatch_call(provider: ProviderSpec, dataset_id: str, params: Dict[str, Any]) -> Tuple[str, pd.DataFrame]:
    adapter = provider.adapter.lower()
    api_id = provider.api_id
    # Apply per-provider param transform if present
    p: Dict[str, Any] = dict(params)
    if provider.param_transform is not None:
        try:
            p = provider.param_transform(p)
        except Exception:
            # fall back to original params if transform fails
            p = dict(params)

    if adapter == 'akshare':
        # Reuse call_akshare with api_id as forced function
        from .adapters.akshare_adapter import call_akshare
        fn_used, df = _sync_await(call_akshare([api_id], p, field_mapping=provider.field_mapping, allow_fallback=False, function_name=api_id))
        return fn_used, df

    if adapter == 'efinance':
        # Leverage efinance_adapter dispatch by dataset_id patterns; when called via v2, return tag with api_id
        from .adapters.efinance_adapter import call_efinance
        fn_used, df = call_efinance(dataset_id, p)
        if isinstance(df, pd.DataFrame):
            return api_id, df
        return api_id, pd.DataFrame([])

    if adapter == 'yfinance':
        from .adapters.yfinance_adapter import call_yfinance
        fn_used, df = call_yfinance(dataset_id, p)
        return api_id, df if isinstance(df, pd.DataFrame) else pd.DataFrame([])

    if adapter == 'ibkr':
        from .adapters.ibkr_adapter import call_ibkr
        fn_used, df = _sync_await(call_ibkr(dataset_id, p))
        return api_id, df if isinstance(df, pd.DataFrame) else pd.DataFrame([])

    if adapter == 'baostock':
        from .adapters.baostock_adapter import call_baostock
        fn_used, df = call_baostock(dataset_id, p)
        return api_id, df if isinstance(df, pd.DataFrame) else pd.DataFrame([])

    if adapter == 'mootdx':
        from .adapters.mootdx_adapter import call_mootdx
        fn_used, df = call_mootdx(dataset_id, p)
        return api_id, df if isinstance(df, pd.DataFrame) else pd.DataFrame([])

    if adapter == 'qstock':
        from .adapters.qstock_adapter import call_qstock
        fn_used, df = call_qstock(dataset_id, p)
        return api_id, df if isinstance(df, pd.DataFrame) else pd.DataFrame([])

    if adapter == 'adata':
        from .adapters.adata_adapter import call_adata
        fn_used, df = call_adata(dataset_id, p)
        return api_id, df if isinstance(df, pd.DataFrame) else pd.DataFrame([])

    if adapter == 'alphavantage':
        from .adapters.alphavantage_adapter import call_alphavantage
        fn_used, df = _sync_await(call_alphavantage(dataset_id, p))
        return api_id, df if isinstance(df, pd.DataFrame) else pd.DataFrame([])

    if adapter == 'snowball':
        # Not yet wired to dataset ids; return empty for now
        return api_id, pd.DataFrame([])

    if adapter == 'qmt':
        # Not yet wired; return empty for now
        return api_id, pd.DataFrame([])

    raise RuntimeError(f"Unknown adapter: {adapter}")


def _sync_await(coro):
    # Helper to run async calls from sync context; tests patch _dispatch_call, so minimal impl is OK
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # In real app, dispatcher_v2 will be async; for now run in thread
        from concurrent.futures import ThreadPoolExecutor
        import threading
        result: Tuple[str, pd.DataFrame] = ('', pd.DataFrame([]))
        def runner():
            nonlocal result
            result = asyncio.run(coro)
        t = threading.Thread(target=runner)
        t.start(); t.join()
        return result
    else:
        return asyncio.run(coro)


def fetch_data_v2(
    dataset_id: str,
    params: Dict[str, Any],
    *,
    adapter: Optional[List[str]] = None,
    allow_fallback: bool = True,
) -> Tuple[str, pd.DataFrame]:
    providers = resolve_providers(dataset_id, adapter=adapter)
    last_err: Optional[Exception] = None
    for p in providers:
        try:
            fn_used, df = _dispatch_call(p, dataset_id, params)
            if isinstance(df, pd.DataFrame) and not df.empty:
                logger.bind(dataset=dataset_id, adapter=p.adapter, api=p.api_id).info('v2 fetched')
                return fn_used, df
        except Exception as e:
            last_err = e
            if not allow_fallback:
                raise
            continue
    if last_err:
        raise last_err
    return 'empty', pd.DataFrame([])