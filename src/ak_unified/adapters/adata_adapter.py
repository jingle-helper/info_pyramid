from __future__ import annotations

from typing import Any, Dict, Tuple, Optional, List

import pandas as pd


class ADataAdapterError(RuntimeError):
    pass


def _import_adata():
    try:
        import adata  # type: ignore
        return adata
    except Exception as exc:
        raise ADataAdapterError("Failed to import adata. Install with pip install adata") from exc


def _to_df(obj: Any) -> pd.DataFrame:
    if isinstance(obj, pd.DataFrame):
        return obj
    if isinstance(obj, list):
        return pd.DataFrame(obj)
    if isinstance(obj, dict):
        return pd.DataFrame([obj])
    return pd.DataFrame([])


def call_adata(dataset_id: str, params: Dict[str, Any]) -> Tuple[str, pd.DataFrame]:
    ad = _import_adata()
    # Try to find available methods for historical data
    if '.ohlcv_daily' in dataset_id or '.ohlcva_daily' in dataset_id:
        symbol = params.get('symbol')
        start = params.get('start')
        end = params.get('end')
        
        # Try different possible method names
        methods_to_try = ['get_history', 'history', 'get_data', 'data', 'get_ohlcv', 'ohlcv']
        df = pd.DataFrame()
        
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
        
        if df is None or df.empty:
            # Try calling without parameters
            for method_name in methods_to_try:
                if hasattr(ad, method_name):
                    try:
                        method = getattr(ad, method_name)
                        df = method(symbol)
                        break
                    except Exception:
                        continue
        
        df = _to_df(df)
        if not df.empty:
            # Try to rename columns if they exist
            column_mapping = {
                'date': 'date', 'time': 'date', 'datetime': 'date',
                'open': 'open', '开盘': 'open',
                'high': 'high', '最高': 'high',
                'low': 'low', '最低': 'low',
                'close': 'close', '收盘': 'close',
                'volume': 'volume', '成交量': 'volume', 'vol': 'volume',
                'amount': 'amount', '成交额': 'amount'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns and new_col not in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            if 'symbol' not in df.columns:
                df.insert(0, 'symbol', symbol)
        
        return ('adata.historical_data', df)
    if '.quote' in dataset_id:
        symbols: Optional[List[str]] = params.get('symbols')
        try:
            df = ad.get_quotes(symbols) if symbols else ad.get_quotes()
        except Exception as exc:
            raise ADataAdapterError(str(exc)) from exc
        return ('adata.get_quotes', _to_df(df))

    # Industry/Concept lists
    if dataset_id.endswith('board.industry.list.adata'):
        fn = getattr(ad, 'industries', None)
        if fn:
            try:
                return ('adata.industries', _to_df(fn()))
            except Exception as exc:
                raise ADataAdapterError(str(exc)) from exc
        return ('adata.industries', _to_df([]))

    if dataset_id.endswith('board.concept.list.adata'):
        fn = getattr(ad, 'concepts', None)
        if fn:
            try:
                return ('adata.concepts', _to_df(fn()))
            except Exception as exc:
                raise ADataAdapterError(str(exc)) from exc
        return ('adata.concepts', _to_df([]))

    # Constituents
    if dataset_id.endswith('board.industry.cons.adata') or dataset_id.endswith('board.concept.cons.adata'):
        code = params.get('board_code') or params.get('symbol')
        fn = getattr(ad, 'block_stocks', None) or getattr(ad, 'members', None)
        if fn:
            try:
                df = _to_df(fn(code))
            except Exception as exc:
                raise ADataAdapterError(str(exc)) from exc
            if not df.empty:
                df = df.rename(columns={'代码': 'symbol', '名称': 'symbol_name', '权重': 'weight'})
            return ('adata.block_members', df)
        return ('adata.block_members', _to_df([]))

    # Announcements
    if dataset_id.endswith('announcements.adata'):
        symbol = params.get('symbol')
        fn = getattr(ad, 'announcements', None)
        if fn:
            try:
                return ('adata.announcements', _to_df(fn(symbol)))
            except Exception as exc:
                raise ADataAdapterError(str(exc)) from exc
        return ('adata.announcements', _to_df([]))
    return ('adata.unsupported', pd.DataFrame([]))