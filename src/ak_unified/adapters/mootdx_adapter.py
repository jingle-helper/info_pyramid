from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd


class MooAdapterError(RuntimeError):
    pass


def _import_mootdx_quotes():
    try:
        from mootdx.quotes import Quotes  # type: ignore
        # Try different server configurations
        servers_to_try = [
            ('119.147.212.81', 7709),  # 腾讯服务器
            ('47.103.48.45', 7709),    # 阿里云服务器
            ('47.103.86.229', 7709),   # 阿里云服务器
            ('47.103.88.146', 7709),   # 阿里云服务器
            ('47.103.86.254', 7709),   # 阿里云服务器
            ('47.103.86.243', 7709),   # 阿里云服务器
            ('47.103.86.244', 7709),   # 阿里云服务器
            ('47.103.86.245', 7709),   # 阿里云服务器
            ('47.103.86.246', 7709),   # 阿里云服务器
            ('47.103.86.247', 7709),   # 阿里云服务器
            ('47.103.86.248', 7709),   # 阿里云服务器
            ('47.103.86.249', 7709),   # 阿里云服务器
            ('47.103.86.250', 7709),   # 阿里云服务器
            ('47.103.86.251', 7709),   # 阿里云服务器
            ('47.103.86.252', 7709),   # 阿里云服务器
            ('47.103.86.253', 7709),   # 阿里云服务器
        ]
        
        for ip, port in servers_to_try:
            try:
                quotes = Quotes.factory(market='std', server=(ip, port))
                # Test if the connection works
                quotes.bars(symbol='000001', frequency=9, start=0, offset=1, market=0)
                return quotes
            except Exception:
                continue
        
        # If all servers fail, try the default factory
        try:
            return Quotes.factory(market='std')
        except Exception:
            # Last resort: create with explicit server
            return Quotes.factory(market='std', server=('119.147.212.81', 7709))
            
    except ImportError as exc:
        raise MooAdapterError("Failed to import mootdx.quotes. Install with pip install mootdx") from exc
    except Exception as exc:
        raise MooAdapterError(f"Failed to initialize mootdx quotes: {exc}") from exc


def _import_mootdx_reader():
    try:
        from mootdx.reader import Reader  # type: ignore
        return Reader.factory(market='std')
    except Exception:
        return None


def call_mootdx(dataset_id: str, params: Dict[str, Any]) -> Tuple[str, pd.DataFrame]:
    # Daily OHLCV/OHLCVA
    if dataset_id.endswith('ohlcv_daily') or dataset_id.endswith('ohlcva_daily'):
        q = _import_mootdx_quotes()
        symbol = params.get('symbol')
        # Extract 6-digit code from symbol (remove .SH/.SZ/.BJ suffix if present)
        if symbol and symbol.endswith(('.SH', '.SZ', '.BJ')):
            code = symbol[:-3]
        else:
            code = symbol or ''
        
        # Determine market based on symbol suffix or code prefix
        if symbol and symbol.endswith('.SH'):
            market = 1  # Shanghai
        elif symbol and symbol.endswith('.SZ'):
            market = 0  # Shenzhen
        elif symbol and symbol.endswith('.BJ'):
            market = 2  # Beijing
        else:
            # Guess market from code prefix
            if code.startswith('6'):
                market = 1  # Shanghai
            elif code.startswith(('0', '3')):
                market = 0  # Shenzhen
            else:
                market = 1  # Default to Shanghai
        
        # Use bars() method with date filtering for better reliability
        try:
            # Get data using bars() method (more reliable)
            df = q.bars(symbol=code, frequency=9, start=0, offset=2000, market=market)
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Rename columns to standard format
                column_mapping = {
                    'open': 'open', 'high': 'high', 'low': 'low', 
                    'close': 'close', 'vol': 'volume', 'volume': 'volume'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
                
                # Add symbol column if not present
                if 'symbol' not in df.columns:
                    df.insert(0, 'symbol', symbol)
                
                # Apply date filtering if start/end dates are provided
                start_date = params.get('start')
                end_date = params.get('end')
                
                if start_date or end_date:
                    # Convert date columns to datetime for filtering
                    date_col = None
                    for col in ['date', 'datetime', 'time']:
                        if col in df.columns:
                            date_col = col
                            break
                    
                    if date_col:
                        try:
                            df[date_col] = pd.to_datetime(df[date_col])
                            
                            if start_date:
                                start_dt = pd.to_datetime(start_date)
                                df = df[df[date_col] >= start_dt]
                            
                            if end_date:
                                end_dt = pd.to_datetime(end_date)
                                df = df[df[date_col] <= end_dt]
                                
                        except Exception as date_exc:
                            print(f"Warning: Date filtering failed: {date_exc}")
                
                return ('mootdx.bars_daily_filtered', df)
            else:
                return ('mootdx.bars_daily', pd.DataFrame([]))
                
        except Exception as exc:
            raise MooAdapterError(f"Failed to fetch daily data: {exc}") from exc

    # Minute OHLCV (5/15/30/60)
    if dataset_id.endswith('ohlcv_min'):
        q = _import_mootdx_quotes()
        symbol = params.get('symbol')
        # Extract 6-digit code from symbol (remove .SH/.SZ/.BJ suffix if present)
        if symbol and symbol.endswith(('.SH', '.SZ', '.BJ')):
            code = symbol[:-3]
        else:
            code = symbol or ''
        
        # Determine market based on symbol suffix or code prefix
        if symbol and symbol.endswith('.SH'):
            market = 1  # Shanghai
        elif symbol and symbol.endswith('.SZ'):
            market = 0  # Shenzhen
        elif symbol and symbol.endswith('.BJ'):
            market = 2  # Beijing
        else:
            # Guess market from code prefix
            if code.startswith('6'):
                market = 1  # Shanghai
            elif code.startswith(('0', '3')):
                market = 0  # Shenzhen
            else:
                market = 1  # Default to Shanghai
        
        freq = str(params.get('freq') or '5').lower()
        # Map to TDX frequency code
        freq_map = {'min5': 0, '5': 0, 'min15': 1, '15': 1, 'min30': 2, '30': 2, 'min60': 3, '60': 3}
        fcode = freq_map.get(freq, 0)
        
        try:
            # Get data using bars() method (more reliable)
            df = q.bars(symbol=code, frequency=fcode, start=0, offset=2000, market=market)
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Rename columns to standard format
                column_mapping = {
                    'open': 'open', 'high': 'high', 'low': 'low', 
                    'close': 'close', 'vol': 'volume', 'volume': 'volume'
                }
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df = df.rename(columns={old_col: new_col})
                
                # Add symbol column if not present
                if 'symbol' not in df.columns:
                    df.insert(0, 'symbol', symbol)
                
                # Apply date filtering if start/end dates are provided
                start_date = params.get('start')
                end_date = params.get('end')
                
                if start_date or end_date:
                    # Convert date columns to datetime for filtering
                    date_col = None
                    for col in ['date', 'datetime', 'time']:
                        if col in df.columns:
                            date_col = col
                            break
                    
                    if date_col:
                        try:
                            df[date_col] = pd.to_datetime(df[date_col])
                            
                            if start_date:
                                start_dt = pd.to_datetime(start_date)
                                df = df[df[date_col] >= start_dt]
                            
                            if end_date:
                                end_dt = pd.to_datetime(end_date)
                                df = df[df[date_col] <= end_dt]
                                
                        except Exception as date_exc:
                            print(f"Warning: Date filtering failed: {date_exc}")
                
                return (f'mootdx.bars_min_{freq}_filtered', df)
            else:
                return (f'mootdx.bars_min_{freq}', pd.DataFrame([]))
                
        except Exception as exc:
            raise MooAdapterError(f"Failed to fetch minute data: {exc}") from exc

    # Blocks (industry/concept)
    if dataset_id in ('securities.board.cn.industry.blocks.mootdx', 'securities.board.cn.concept.blocks.mootdx'):
        reader = _import_mootdx_reader()
        if reader is None:
            return ('mootdx.reader_unavailable', pd.DataFrame([]))
        try:
            cat = 'hy' if 'industry' in dataset_id else 'gn'
            df = reader.block(symbol=cat)
            # Expected columns: code, name, blockname
            if isinstance(df, pd.DataFrame) and not df.empty:
                cols = {c: c for c in df.columns}
                cols.update({"code": "symbol", "blockname": "board_name"})
                df = df.rename(columns=cols)
                return (f'mootdx.block_{cat}', df)
        except Exception:
            return ('mootdx.block_error', pd.DataFrame([]))
        return ('mootdx.block_empty', pd.DataFrame([]))

    # Index constituents via blocks (zs)
    if dataset_id == 'market.index.constituents.mootdx':
        reader = _import_mootdx_reader()
        if reader is None:
            return ('mootdx.reader_unavailable', pd.DataFrame([]))
        try:
            df = reader.block(symbol='zs')
            # Filter by index code/name if provided
            idx = params.get('index_code') or params.get('symbol')
            if isinstance(df, pd.DataFrame) and not df.empty and idx:
                f = df[df['blockname'].astype(str).str.contains(str(idx)) | df['code'].astype(str).str.contains(str(idx))]
                if not f.empty:
                    f = f.rename(columns={"code": "symbol"})
                    f.insert(0, 'index_symbol', idx)
                    return ('mootdx.block_zs', f)
            return ('mootdx.block_zs', pd.DataFrame([]))
        except Exception:
            return ('mootdx.block_error', pd.DataFrame([]))

    # Adjust factor (xdxr)
    if dataset_id == 'securities.equity.cn.adjust_factor.mootdx':
        q = _import_mootdx_quotes()
        symbol = params.get('symbol')
        # Extract 6-digit code from symbol (remove .SH/.SZ/.BJ suffix if present)
        if symbol and symbol.endswith(('.SH', '.SZ', '.BJ')):
            code = symbol[:-3]
        else:
            code = symbol or ''
        try:
            df = q.xdxr(symbol=code)
            if isinstance(df, pd.DataFrame):
                df = df.rename(columns={"category": "category", "date": "date"})
                df.insert(0, 'symbol', symbol)
                return ('mootdx.xdxr', df)
        except Exception:
            return ('mootdx.xdxr_error', pd.DataFrame([]))
        return ('mootdx.xdxr', pd.DataFrame([]))

    # Fundamentals via reader finance (if available)
    if dataset_id == 'securities.equity.cn.fundamentals.mootdx':
        reader = _import_mootdx_reader()
        if reader is None:
            return ('mootdx.reader_unavailable', pd.DataFrame([]))
        symbol = params.get('symbol')
        # Extract 6-digit code from symbol (remove .SH/.SZ/.BJ suffix if present)
        if symbol and symbol.endswith(('.SH', '.SZ', '.BJ')):
            code = symbol[:-3]
        else:
            code = symbol or ''
        try:
            if hasattr(reader, 'finance'):
                df = reader.finance(symbol=code)
            else:
                df = pd.DataFrame([])
            if isinstance(df, pd.DataFrame):
                df.insert(0, 'symbol', symbol)
                return ('mootdx.finance', df)
        except Exception:
            return ('mootdx.finance_error', pd.DataFrame([]))
        return ('mootdx.finance', pd.DataFrame([]))

    return ('mootdx.unsupported', pd.DataFrame([]))