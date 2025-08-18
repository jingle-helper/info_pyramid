"""
exchange_calendars Adapter

Provides trading calendar data via the exchange_calendars library.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd

from .base import BaseAdapterError
from ..rate_limiter import acquire_rate_limit
from ..logging import logger


class ExchangeCalendarsAdapterError(BaseAdapterError):
    pass


def _import_exchange_calendars():
    try:
        import exchange_calendars as xcals  # type: ignore
        return xcals
    except Exception as exc:
        raise ExchangeCalendarsAdapterError("Failed to import exchange_calendars. Install with pip install exchange_calendars") from exc


_EXCHANGE_MAP = {
    # Generic -> exchange_calendars codes
    'SSE': 'XSHG',
    'SZSE': 'XSHE',
    'HKEX': 'XHKG',
    'NYSE': 'XNYS',
    'NASDAQ': 'XNAS',
    'TSE': 'XTKS',
    'LSE': 'XLON',
}


def _resolve_exchange(code: str) -> str:
    if not code:
        return code
    return _EXCHANGE_MAP.get(code.upper(), code)


async def call_exchange_calendars(function_name: str, params: Dict[str, Any]) -> Tuple[str, pd.DataFrame]:
    await acquire_rate_limit('exchange_calendars', 'default')
    xcals = _import_exchange_calendars()

    if function_name == 'supported_exchanges':
        try:
            names = list(xcals.get_calendar_names())
            df = pd.DataFrame({'exchange': names})
            df['library'] = 'exchange_calendars'
            return function_name, df
        except Exception as e:
            logger.warning(f"exchange_calendars supported_exchanges failed: {e}")
            return function_name, pd.DataFrame([])

    exchange = _resolve_exchange(params.get('exchange', ''))

    try:
        cal = xcals.get_calendar(exchange)
    except Exception as e:
        logger.warning(f"exchange_calendars get_calendar failed for {exchange}: {e}")
        return function_name, pd.DataFrame([])

    try:
        if function_name == 'trading_days':
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            sessions = cal.sessions_in_range(start_date, end_date)
            df = pd.DataFrame({'date': [d.strftime('%Y-%m-%d') for d in sessions]})
            df.insert(0, 'exchange', exchange)
            return function_name, df
        if function_name == 'is_trading_day':
            date = params.get('date')
            ok = bool(cal.is_session(date))
            df = pd.DataFrame([{'exchange': exchange, 'date': date, 'is_trading_day': ok}])
            return function_name, df
        if function_name == 'trading_hours':
            date = params.get('date')
            open_t = cal.session_open(date)
            close_t = cal.session_close(date)
            # Breaks optional
            try:
                bs = cal.session_break_start(date)
                be = cal.session_break_end(date)
                has_break = True
            except Exception:
                bs = None
                be = None
                has_break = False
            df = pd.DataFrame([{
                'exchange': exchange,
                'date': date,
                'open_time': open_t.strftime('%H:%M:%S') if open_t else None,
                'close_time': close_t.strftime('%H:%M:%S') if close_t else None,
                'has_break': has_break,
                'break_start': bs.strftime('%H:%M:%S') if bs else None,
                'break_end': be.strftime('%H:%M:%S') if be else None,
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
                    'open_time': row['open'].strftime('%H:%M:%S') if pd.notna(row['open']) else None,
                    'close_time': row['close'].strftime('%H:%M:%S') if pd.notna(row['close']) else None,
                })
            return function_name, pd.DataFrame(rows)
        if function_name == 'holidays':
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            hol = cal.holidays.loc[start_date:end_date]
            df = pd.DataFrame({'date': [d.strftime('%Y-%m-%d') for d in hol]})
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
        logger.warning(f"exchange_calendars {function_name} failed for {exchange}: {e}")
        return function_name, pd.DataFrame([])

    return function_name, pd.DataFrame([])