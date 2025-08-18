"""
Calendar Adapter

Provides access to trading calendar data including:
- Trading days and sessions
- Market hours and breaks
- Holiday calendars
- Multi-exchange support

Supports both exchange_calendars and pandas_market_calendars libraries.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from .base import BaseAdapterError
from ..rate_limiter import acquire_rate_limit
from ..logging import logger


class CalendarAdapterError(BaseAdapterError):
    """Calendar adapter specific error."""
    pass


class CalendarAdapter:
    """Unified adapter for trading calendar data from multiple libraries."""
    
    def __init__(self, library: str = 'auto'):
        self.supported_libraries = ['auto', 'exchange_calendars', 'pandas_market_calendars']
        self.library = library
        self._xcals = None
        self._mcal = None
        
        if library not in self.supported_libraries:
            raise CalendarAdapterError(f"Unsupported library: {library}")
    
    def _import_exchange_calendars(self):
        """Import exchange_calendars library."""
        try:
            import exchange_calendars as xcals
            return xcals
        except ImportError:
            raise CalendarAdapterError("Failed to import exchange_calendars. Please install: pip install exchange_calendars")
    
    def _import_pandas_market_calendars(self):
        """Import pandas_market_calendars library."""
        try:
            import pandas_market_calendars as mcal
            return mcal
        except ImportError:
            raise CalendarAdapterError("Failed to import pandas_market_calendars. Please install: pip install pandas_market_calendars")
    
    def _get_xcals(self):
        """Get exchange_calendars instance."""
        if self._xcals is None:
            self._xcals = self._import_exchange_calendars()
        return self._xcals
    
    def _get_mcal(self):
        """Get pandas_market_calendars instance."""
        if self._mcal is None:
            self._mcal = self._import_pandas_market_calendars()
        return self._mcal
    
    def _get_calendar(self, exchange: str, library: Optional[str] = None):
        """Get calendar instance for specified exchange and library."""
        lib = library or self.library
        
        if lib == 'auto':
            # Try exchange_calendars first, fallback to pandas_market_calendars
            try:
                xcals = self._get_xcals()
                return xcals.get_calendar(exchange), 'exchange_calendars'
            except Exception:
                try:
                    mcal = self._get_mcal()
                    return mcal.get_calendar(exchange), 'pandas_market_calendars'
                except Exception as e:
                    raise CalendarAdapterError(f"Failed to get calendar for {exchange}: {e}")
        
        elif lib == 'exchange_calendars':
            xcals = self._get_xcals()
            return xcals.get_calendar(exchange), 'exchange_calendars'
        
        elif lib == 'pandas_market_calendars':
            mcal = self._get_mcal()
            return mcal.get_calendar(exchange), 'pandas_market_calendars'
        
        else:
            raise CalendarAdapterError(f"Unsupported library: {lib}")
    
    # ========== 交易日历查询 ==========
    
    async def get_trading_days(
        self, 
        exchange: str,
        start_date: str,
        end_date: str,
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get trading days for specified exchange and date range.
        
        Args:
            exchange: Exchange code (e.g., 'NYSE', 'NASDAQ', 'SSE', 'SZSE')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            library: Library to use ('auto', 'exchange_calendars', 'pandas_market_calendars')
            
        Returns:
            DataFrame with trading days
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            calendar, lib_used = self._get_calendar(exchange, library)
            
            if lib_used == 'exchange_calendars':
                # Use exchange_calendars API
                sessions = calendar.sessions_in_range(start_date, end_date)
                rows = []
                for session in sessions:
                    rows.append({
                        'exchange': exchange,
                        'date': session.strftime('%Y-%m-%d'),
                        'is_trading_day': True,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    })
                return pd.DataFrame(rows)
            
            else:
                # Use pandas_market_calendars API
                valid_days = calendar.valid_days(start_date, end_date)
                rows = []
                for day in valid_days:
                    rows.append({
                        'exchange': exchange,
                        'date': day.strftime('%Y-%m-%d'),
                        'is_trading_day': True,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    })
                return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get trading days for {exchange}: {e}")
            return pd.DataFrame()
    
    async def is_trading_day(
        self, 
        exchange: str,
        date: str,
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Check if a specific date is a trading day.
        
        Args:
            exchange: Exchange code
            date: Date in YYYY-MM-DD format
            library: Library to use
            
        Returns:
            DataFrame with trading day status
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            calendar, lib_used = self._get_calendar(exchange, library)
            
            if lib_used == 'exchange_calendars':
                is_session = calendar.is_session(date)
            else:
                is_session = calendar.is_session(date)
            
            df = pd.DataFrame([{
                'exchange': exchange,
                'date': date,
                'is_trading_day': is_session,
                'library': lib_used,
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to check trading day for {exchange} on {date}: {e}")
            return pd.DataFrame()
    
    # ========== 交易时间查询 ==========
    
    async def get_trading_hours(
        self, 
        exchange: str,
        date: str,
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get trading hours for a specific date.
        
        Args:
            exchange: Exchange code
            date: Date in YYYY-MM-DD format
            library: Library to use
            
        Returns:
            DataFrame with trading hours
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            calendar, lib_used = self._get_calendar(exchange, library)
            
            if lib_used == 'exchange_calendars':
                # Use exchange_calendars API
                try:
                    session_open = calendar.session_open(date)
                    session_close = calendar.session_close(date)
                    
                    # Check for breaks
                    try:
                        break_start = calendar.session_break_start(date)
                        break_end = calendar.session_break_end(date)
                        has_break = True
                    except:
                        break_start = None
                        break_end = None
                        has_break = False
                    
                    df = pd.DataFrame([{
                        'exchange': exchange,
                        'date': date,
                        'open_time': session_open.strftime('%H:%M:%S') if session_open else None,
                        'close_time': session_close.strftime('%H:%M:%S') if session_close else None,
                        'has_break': has_break,
                        'break_start': break_start.strftime('%H:%M:%S') if break_start else None,
                        'break_end': break_end.strftime('%H:%M:%S') if break_end else None,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    }])
                    
                    return df
                    
                except Exception as e:
                    logger.warning(f"Failed to get trading hours for {exchange} on {date}: {e}")
                    return pd.DataFrame()
            
            else:
                # Use pandas_market_calendars API
                try:
                    schedule = calendar.schedule.loc[date]
                    open_time = schedule['market_open'].strftime('%H:%M:%S')
                    close_time = schedule['market_close'].strftime('%H:%M:%S')
                    
                    # Check for breaks
                    if 'break_start' in schedule and 'break_end' in schedule:
                        break_start = schedule['break_start'].strftime('%H:%M:%S')
                        break_end = schedule['break_end'].strftime('%H:%M:%S')
                        has_break = True
                    else:
                        break_start = None
                        break_end = None
                        has_break = False
                    
                    df = pd.DataFrame([{
                        'exchange': exchange,
                        'date': date,
                        'open_time': open_time,
                        'close_time': close_time,
                        'has_break': has_break,
                        'break_start': break_start,
                        'break_end': break_end,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    }])
                    
                    return df
                    
                except Exception as e:
                    logger.warning(f"Failed to get trading hours for {exchange} on {date}: {e}")
                    return pd.DataFrame()
            
        except Exception as e:
            logger.warning(f"Failed to get trading hours for {exchange} on {date}: {e}")
            return pd.DataFrame()
    
    async def get_trading_schedule(
        self, 
        exchange: str,
        start_date: str,
        end_date: str,
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get trading schedule for a date range.
        
        Args:
            exchange: Exchange code
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            library: Library to use
            
        Returns:
            DataFrame with trading schedule
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            calendar, lib_used = self._get_calendar(exchange, library)
            
            if lib_used == 'exchange_calendars':
                # Use exchange_calendars API
                schedule = calendar.schedule.loc[start_date:end_date]
                rows = []
                for date, row in schedule.iterrows():
                    rows.append({
                        'exchange': exchange,
                        'date': date.strftime('%Y-%m-%d'),
                        'open_time': row['open'].strftime('%H:%M:%S') if pd.notna(row['open']) else None,
                        'close_time': row['close'].strftime('%H:%M:%S') if pd.notna(row['close']) else None,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    })
                return pd.DataFrame(rows)
            
            else:
                # Use pandas_market_calendars API
                schedule = calendar.schedule.loc[start_date:end_date]
                rows = []
                for date, row in schedule.iterrows():
                    rows.append({
                        'exchange': exchange,
                        'date': date.strftime('%Y-%m-%d'),
                        'open_time': row['market_open'].strftime('%H:%M:%S') if pd.notna(row['market_open']) else None,
                        'close_time': row['market_close'].strftime('%H:%M:%S') if pd.notna(row['market_close']) else None,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    })
                return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get trading schedule for {exchange}: {e}")
            return pd.DataFrame()
    
    # ========== 节假日查询 ==========
    
    async def get_holidays(
        self, 
        exchange: str,
        start_date: str,
        end_date: str,
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get holidays for specified exchange and date range.
        
        Args:
            exchange: Exchange code
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            library: Library to use
            
        Returns:
            DataFrame with holidays
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            calendar, lib_used = self._get_calendar(exchange, library)
            
            if lib_used == 'exchange_calendars':
                # Use exchange_calendars API
                holidays = calendar.holidays.loc[start_date:end_date]
                rows = []
                for holiday in holidays:
                    rows.append({
                        'exchange': exchange,
                        'date': holiday.strftime('%Y-%m-%d'),
                        'is_holiday': True,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    })
                return pd.DataFrame(rows)
            
            else:
                # Use pandas_market_calendars API
                holidays = calendar.holidays()
                # Filter holidays in date range
                filtered_holidays = [h for h in holidays if start_date <= h.strftime('%Y-%m-%d') <= end_date]
                rows = []
                for holiday in filtered_holidays:
                    rows.append({
                        'exchange': exchange,
                        'date': holiday.strftime('%Y-%m-%d'),
                        'is_holiday': True,
                        'library': lib_used,
                        'timestamp': datetime.now()
                    })
                return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get holidays for {exchange}: {e}")
            return pd.DataFrame()
    
    # ========== 交易所信息查询 ==========
    
    async def get_supported_exchanges(
        self, 
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get list of supported exchanges.
        
        Args:
            library: Library to use
            
        Returns:
            DataFrame with supported exchanges
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            lib = library or self.library
            
            if lib == 'auto' or lib == 'exchange_calendars':
                try:
                    xcals = self._get_xcals()
                    exchanges = list(xcals.get_calendar_names())
                    rows = []
                    for exchange in exchanges:
                        rows.append({
                            'exchange': exchange,
                            'library': 'exchange_calendars',
                            'supported': True,
                            'timestamp': datetime.now()
                        })
                    return pd.DataFrame(rows)
                except Exception:
                    pass
            
            if lib == 'auto' or lib == 'pandas_market_calendars':
                try:
                    mcal = self._get_mcal()
                    exchanges = mcal.get_calendar_names()
                    rows = []
                    for exchange in exchanges:
                        rows.append({
                            'exchange': exchange,
                            'library': 'pandas_market_calendars',
                            'supported': True,
                            'timestamp': datetime.now()
                        })
                    return pd.DataFrame(rows)
                except Exception:
                    pass
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.warning(f"Failed to get supported exchanges: {e}")
            return pd.DataFrame()
    
    # ========== 高级功能 ==========
    
    async def get_next_trading_day(
        self, 
        exchange: str,
        date: str,
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get next trading day after specified date.
        
        Args:
            exchange: Exchange code
            date: Date in YYYY-MM-DD format
            library: Library to use
            
        Returns:
            DataFrame with next trading day
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            calendar, lib_used = self._get_calendar(exchange, library)
            
            if lib_used == 'exchange_calendars':
                # Use exchange_calendars API
                next_session = calendar.next_session(date)
                next_date = next_session.strftime('%Y-%m-%d')
            else:
                # Use pandas_market_calendars API
                next_session = calendar.next_session(date)
                next_date = next_session.strftime('%Y-%m-%d')
            
            df = pd.DataFrame([{
                'exchange': exchange,
                'current_date': date,
                'next_trading_day': next_date,
                'library': lib_used,
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get next trading day for {exchange} after {date}: {e}")
            return pd.DataFrame()
    
    async def get_previous_trading_day(
        self, 
        exchange: str,
        date: str,
        library: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get previous trading day before specified date.
        
        Args:
            exchange: Exchange code
            date: Date in YYYY-MM-DD format
            library: Library to use
            
        Returns:
            DataFrame with previous trading day
        """
        try:
            await acquire_rate_limit('calendar', 'default')
            
            calendar, lib_used = self._get_calendar(exchange, library)
            
            if lib_used == 'exchange_calendars':
                # Use exchange_calendars API
                prev_session = calendar.previous_session(date)
                prev_date = prev_session.strftime('%Y-%m-%d')
            else:
                # Use pandas_market_calendars API
                prev_session = calendar.previous_session(date)
                prev_date = prev_session.strftime('%Y-%m-%d')
            
            df = pd.DataFrame([{
                'exchange': exchange,
                'current_date': date,
                'previous_trading_day': prev_date,
                'library': lib_used,
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get previous trading day for {exchange} before {date}: {e}")
            return pd.DataFrame()


# Convenience function for backward compatibility
async def call_calendar(
    function_name: str,
    params: Dict[str, Any],
    library: str = 'auto'
) -> Tuple[str, pd.DataFrame]:
    """
    Convenience function to call Calendar functions.
    
    Args:
        function_name: Function name to call
        params: Parameters for the function
        library: Library to use
        
    Returns:
        Tuple of (function_name, DataFrame)
    """
    adapter = CalendarAdapter(library=library)
    
    if function_name == 'trading_days':
        df = await adapter.get_trading_days(
            exchange=params.get('exchange'),
            start_date=params.get('start_date'),
            end_date=params.get('end_date'),
            library=params.get('library')
        )
        return 'trading_days', df
    
    elif function_name == 'is_trading_day':
        df = await adapter.is_trading_day(
            exchange=params.get('exchange'),
            date=params.get('date'),
            library=params.get('library')
        )
        return 'is_trading_day', df
    
    elif function_name == 'trading_hours':
        df = await adapter.get_trading_hours(
            exchange=params.get('exchange'),
            date=params.get('date'),
            library=params.get('library')
        )
        return 'trading_hours', df
    
    elif function_name == 'trading_schedule':
        df = await adapter.get_trading_schedule(
            exchange=params.get('exchange'),
            start_date=params.get('start_date'),
            end_date=params.get('end_date'),
            library=params.get('library')
        )
        return 'trading_schedule', df
    
    elif function_name == 'holidays':
        df = await adapter.get_holidays(
            exchange=params.get('exchange'),
            start_date=params.get('start_date'),
            end_date=params.get('end_date'),
            library=params.get('library')
        )
        return 'holidays', df
    
    elif function_name == 'supported_exchanges':
        df = await adapter.get_supported_exchanges(
            library=params.get('library')
        )
        return 'supported_exchanges', df
    
    elif function_name == 'next_trading_day':
        df = await adapter.get_next_trading_day(
            exchange=params.get('exchange'),
            date=params.get('date'),
            library=params.get('library')
        )
        return 'next_trading_day', df
    
    elif function_name == 'previous_trading_day':
        df = await adapter.get_previous_trading_day(
            exchange=params.get('exchange'),
            date=params.get('date'),
            library=params.get('library')
        )
        return 'previous_trading_day', df
    
    else:
        raise CalendarAdapterError(f"Unknown function: {function_name}")