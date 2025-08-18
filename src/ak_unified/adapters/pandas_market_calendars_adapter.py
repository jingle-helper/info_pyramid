"""
pandas_market_calendars Adapter

Provides trading calendar data via the pandas_market_calendars library.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd

from .base import BaseAdapterError
from ..rate_limiter import acquire_rate_limit
from ..logging import logger


class PandasMarketCalendarsAdapterError(BaseAdapterError):
    pass


def _import_mcal():
    try:
        import pandas_market_calendars as mcal  # type: ignore
        return mcal
    except Exception as exc:
        raise PandasMarketCalendarsAdapterError("Failed to import pandas_market_calendars. Install with pip install pandas_market_calendars") from exc


_EXCHANGE_MAP = {
    # Generic -> pandas_market_calendars codes are often human-readable; default passthrough
    'SSE': 'SSE',
    'SZSE': 'SZSE',
    'HKEX': 'HKEX',
    'NYSE': 'NYSE',
    'NASDAQ': 'NASDAQ',
    'TSE': 'TSE',
    'LSE': 'LSE',
}


def _resolve_exchange(code: str) -> str:
    if not code:
        return code
    return _EXCHANGE_MAP.get(code.upper(), code)


async def call_pandas_market_calendars(function_name: str, params: Dict[str, Any]) -> Tuple[str, pd.DataFrame]:
    await acquire_rate_limit('pandas_market_calendars', 'default')
    mcal = _import_mcal()

    if function_name == 'supported_exchanges':
        try:
            names = mcal.get_calendar_names()
            df = pd.DataFrame({'exchange': names})
            df['library'] = 'pandas_market_calendars'
            return function_name, df
        except Exception as e:
            logger.warning(f"pandas_market_calendars supported_exchanges failed: {e}")
            return function_name, pd.DataFrame([])

    exchange = _resolve_exchange(params.get('exchange', ''))

    try:
        cal = mcal.get_calendar(exchange)
    except Exception as e:
        logger.warning(f"pandas_market_calendars get_calendar failed for {exchange}: {e}")
        return function_name, pd.DataFrame([])

    try:
        if function_name == 'trading_days':
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            days = cal.valid_days(start_date, end_date)
            df = pd.DataFrame({'date': [d.strftime('%Y-%m-%d') for d in days]})
            df.insert(0, 'exchange', exchange)
            return function_name, df
        if function_name == 'is_trading_day':
            date = params.get('date')
            ok = bool(cal.is_session(date))
            df = pd.DataFrame([{'exchange': exchange, 'date': date, 'is_trading_day': ok}])
            return function_name, df
        if function_name == 'trading_hours':
            date = params.get('date')
            sched = cal.schedule.loc[date]
            open_t = sched['market_open']
            close_t = sched['market_close']
            bs = sched['break_start'] if 'break_start' in sched else None
            be = sched['break_end'] if 'break_end' in sched else None
            has_break = bool(bs is not None and be is not None)
            df = pd.DataFrame([{
                'exchange': exchange,
                'date': date,
                'open_time': open_t.strftime('%H:%M:%S') if open_t is not None else None,
                'close_time': close_t.strftime('%H:%M:%S') if close_t is not None else None,
                'has_break': has_break,
                'break_start': bs.strftime('%H:%M:%S') if bs is not None else None,
                'break_end': be.strftime('%H:%M:%S') if be is not None else None,
            }])
            return function_name, df
        if function_name == 'trading_schedule':
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            sched = cal.schedule.loc[start_date:end_date]
            rows = []
            for dt, row in sched.iterrows():
                rows.append({
                    'exchange': exchange,
                    'date': dt.strftime('%Y-%m-%d'),
                    'open_time': row['market_open'].strftime('%H:%M:%S') if pd.notna(row['market_open']) else None,
                    'close_time': row['market_close'].strftime('%H:%M:%S') if pd.notna(row['market_close']) else None,
                })
            return function_name, pd.DataFrame(rows)
        if function_name == 'holidays':
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            # pandas_market_calendars exposes holidays via calendar.holidays()
            hols = cal.holidays()
            selected = [d for d in hols if start_date <= d.strftime('%Y-%m-%d') <= end_date]
            df = pd.DataFrame({'date': [d.strftime('%Y-%m-%d') for d in selected]})
            df.insert(0, 'exchange', exchange)
            return function_name, df
        if function_name == 'next_trading_day':
            date = params.get('date')
            nxt = cal.next_session(date)
            df = pd.DataFrame([{'exchange': exchange, 'current_date': date, 'next_trading_day': nxt.strftime('%Y-%m-%d')}])
            return function_name, df
        if function_name == 'previous_trading_day':
            date = params.get('date')
            prev = cal.previous_session(date)
            df = pd.DataFrame([{'exchange': exchange, 'current_date': date, 'previous_trading_day': prev.strftime('%Y-%m-%d')}])
            return function_name, df
    except Exception as e:
        logger.warning(f"pandas_market_calendars {function_name} failed for {exchange}: {e}")
        return function_name, pd.DataFrame([])

    return function_name, pd.DataFrame([])