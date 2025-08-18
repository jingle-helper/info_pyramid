"""
EasyQuotation Adapter

Provides access to EasyQuotation data including:
- Sina finance data (real-time quotes, market data)
- Jisilu bond data (convertible bonds, bond information)
- Market overview and sector data
- Historical data and analysis
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .base import BaseAdapterError
from ..rate_limiter import acquire_rate_limit
from ..logging import logger


class EasyQuotationAdapterError(BaseAdapterError):
    """EasyQuotation adapter specific error."""
    pass


class EasyQuotationAdapter:
    """Adapter for EasyQuotation data from easyquotation library."""
    
    def __init__(self, data_source: str = 'sina'):
        self.supported_sources = ['sina', 'jisilu', 'tencent', 'eastmoney']
        self.data_source = data_source
        self._quoter = None
        
        if data_source not in self.supported_sources:
            raise EasyQuotationAdapterError(f"Unsupported data source: {data_source}")
    
    def _import_easyquotation(self):
        """Import easyquotation library."""
        try:
            import easyquotation
            return easyquotation
        except ImportError:
            raise EasyQuotationAdapterError("Failed to import easyquotation. Please install: pip install easyquotation")
    
    def _get_quoter(self):
        """Get quoter instance."""
        if self._quoter is None:
            easyquotation = self._import_easyquotation()
            
            if self.data_source == 'sina':
                self._quoter = easyquotation.use('sina')
            elif self.data_source == 'jisilu':
                self._quoter = easyquotation.use('jisilu')
            elif self.data_source == 'tencent':
                self._quoter = easyquotation.use('tencent')
            elif self.data_source == 'eastmoney':
                self._quoter = easyquotation.use('eastmoney')
        
        return self._quoter
    
    # ========== 新浪财经数据源 ==========
    
    async def get_stock_quotes(
        self, 
        symbols: List[str]
    ) -> pd.DataFrame:
        """
        Get real-time stock quotes from Sina.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            DataFrame with stock quotes
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get stock quotes
            quotes = quoter.real(symbols)
            
            if not quotes:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for symbol, data in quotes.items():
                rows.append({
                    'symbol': symbol,
                    'name': data.get('name', ''),
                    'current_price': data.get('now', 0),
                    'open': data.get('open', 0),
                    'high': data.get('high', 0),
                    'low': data.get('low', 0),
                    'volume': data.get('volume', 0),
                    'turnover': data.get('amount', 0),
                    'change': data.get('change', 0),
                    'change_percent': data.get('change_percent', 0),
                    'yesterday_close': data.get('close', 0),
                    'bid_price': data.get('bid1', 0),
                    'ask_price': data.get('ask1', 0),
                    'bid_volume': data.get('bid_volume1', 0),
                    'ask_volume': data.get('ask_volume1', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get stock quotes from {self.data_source}: {e}")
            return pd.DataFrame()
    
    async def get_market_overview(self) -> pd.DataFrame:
        """
        Get market overview from Sina.
        
        Returns:
            DataFrame with market overview
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get market overview
            if hasattr(quoter, 'market_snapshot'):
                market_data = quoter.market_snapshot()
            elif hasattr(quoter, 'market_overview'):
                market_data = quoter.market_overview()
            else:
                return pd.DataFrame()
            
            if not market_data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for index_code, data in market_data.items():
                rows.append({
                    'index_code': index_code,
                    'name': data.get('name', ''),
                    'current_value': data.get('now', 0),
                    'change': data.get('change', 0),
                    'change_percent': data.get('change_percent', 0),
                    'open': data.get('open', 0),
                    'high': data.get('high', 0),
                    'low': data.get('low', 0),
                    'volume': data.get('volume', 0),
                    'turnover': data.get('amount', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get market overview from {self.data_source}: {e}")
            return pd.DataFrame()
    
    async def get_sector_data(self) -> pd.DataFrame:
        """
        Get sector performance data from Sina.
        
        Returns:
            DataFrame with sector data
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get sector data
            if hasattr(quoter, 'sector_data'):
                sector_data = quoter.sector_data()
            else:
                return pd.DataFrame()
            
            if not sector_data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for sector_name, data in sector_data.items():
                rows.append({
                    'sector_name': sector_name,
                    'change_percent': data.get('change_percent', 0),
                    'advance_count': data.get('advance_count', 0),
                    'decline_count': data.get('decline_count', 0),
                    'flat_count': data.get('flat_count', 0),
                    'total_count': data.get('total_count', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get sector data from {self.data_source}: {e}")
            return pd.DataFrame()
    
    async def get_stock_rankings(
        self, 
        rank_type: str = 'change_percent',
        limit: int = 50
    ) -> pd.DataFrame:
        """
        Get stock rankings from Sina.
        
        Args:
            rank_type: Type of ranking ('change_percent', 'volume', 'turnover')
            limit: Number of stocks to return
            
        Returns:
            DataFrame with stock rankings
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get stock rankings
            if hasattr(quoter, 'stock_rankings'):
                rankings = quoter.stock_rankings(rank_type, limit)
            else:
                return pd.DataFrame()
            
            if not rankings:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for rank, data in enumerate(rankings, 1):
                rows.append({
                    'rank': rank,
                    'symbol': data.get('symbol', ''),
                    'name': data.get('name', ''),
                    'current_price': data.get('current_price', 0),
                    'change_percent': data.get('change_percent', 0),
                    'volume': data.get('volume', 0),
                    'turnover': data.get('turnover', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get stock rankings from {self.data_source}: {e}")
            return pd.DataFrame()
    
    # ========== 集思录债券数据源 ==========
    
    async def get_convertible_bonds(self) -> pd.DataFrame:
        """
        Get convertible bond data from Jisilu.
        
        Returns:
            DataFrame with convertible bond data
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get convertible bonds
            if hasattr(quoter, 'convertible_bonds'):
                cb_data = quoter.convertible_bonds()
            elif hasattr(quoter, 'jisilu_cb'):
                cb_data = quoter.jisilu_cb()
            else:
                return pd.DataFrame()
            
            if not cb_data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for item in cb_data:
                rows.append({
                    'bond_code': item.get('bond_code', ''),
                    'bond_name': item.get('bond_name', ''),
                    'stock_code': item.get('stock_code', ''),
                    'stock_name': item.get('stock_name', ''),
                    'current_price': item.get('current_price', 0),
                    'conversion_price': item.get('conversion_price', 0),
                    'conversion_value': item.get('conversion_value', 0),
                    'premium_rate': item.get('premium_rate', 0),
                    'yield_to_maturity': item.get('yield_to_maturity', 0),
                    'remaining_years': item.get('remaining_years', 0),
                    'issue_size': item.get('issue_size', 0),
                    'rating': item.get('rating', ''),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get convertible bonds from {self.data_source}: {e}")
            return pd.DataFrame()
    
    async def get_bond_info(
        self, 
        bond_code: str
    ) -> pd.DataFrame:
        """
        Get detailed bond information from Jisilu.
        
        Args:
            bond_code: Bond code
            
        Returns:
            DataFrame with bond information
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get bond info
            if hasattr(quoter, 'bond_info'):
                bond_data = quoter.bond_info(bond_code)
            else:
                return pd.DataFrame()
            
            if not bond_data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'bond_code': bond_code,
                'bond_name': bond_data.get('bond_name', ''),
                'bond_type': bond_data.get('bond_type', ''),
                'issue_date': bond_data.get('issue_date', ''),
                'maturity_date': bond_data.get('maturity_date', ''),
                'face_value': bond_data.get('face_value', 0),
                'coupon_rate': bond_data.get('coupon_rate', 0),
                'payment_frequency': bond_data.get('payment_frequency', ''),
                'current_price': bond_data.get('current_price', 0),
                'yield_to_maturity': bond_data.get('yield_to_maturity', 0),
                'duration': bond_data.get('duration', 0),
                'convexity': bond_data.get('convexity', 0),
                'credit_rating': bond_data.get('credit_rating', ''),
                'issuer': bond_data.get('issuer', ''),
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get bond info from {self.data_source}: {e}")
            return pd.DataFrame()
    
    async def get_bond_yield_curve(
        self, 
        bond_type: str = 'government'
    ) -> pd.DataFrame:
        """
        Get bond yield curve from Jisilu.
        
        Args:
            bond_type: Bond type ('government', 'corporate', 'municipal')
            
        Returns:
            DataFrame with yield curve data
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get yield curve
            if hasattr(quoter, 'yield_curve'):
                curve_data = quoter.yield_curve(bond_type)
            else:
                return pd.DataFrame()
            
            if not curve_data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for item in curve_data:
                rows.append({
                    'bond_type': bond_type,
                    'maturity': item.get('maturity', ''),
                    'yield_rate': item.get('yield_rate', 0),
                    'duration': item.get('duration', 0),
                    'convexity': item.get('convexity', 0),
                    'spread': item.get('spread', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get yield curve from {self.data_source}: {e}")
            return pd.DataFrame()
    
    # ========== 腾讯数据源 ==========
    
    async def get_tencent_quotes(
        self, 
        symbols: List[str]
    ) -> pd.DataFrame:
        """
        Get stock quotes from Tencent.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            DataFrame with stock quotes
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get Tencent quotes
            if hasattr(quoter, 'tencent_quotes'):
                quotes = quoter.tencent_quotes(symbols)
            else:
                return pd.DataFrame()
            
            if not quotes:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for symbol, data in quotes.items():
                rows.append({
                    'symbol': symbol,
                    'name': data.get('name', ''),
                    'current_price': data.get('current', 0),
                    'open': data.get('open', 0),
                    'high': data.get('high', 0),
                    'low': data.get('low', 0),
                    'volume': data.get('volume', 0),
                    'turnover': data.get('turnover', 0),
                    'change': data.get('change', 0),
                    'change_percent': data.get('change_percent', 0),
                    'yesterday_close': data.get('close', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Tencent quotes: {e}")
            return pd.DataFrame()
    
    # ========== 东方财富数据源 ==========
    
    async def get_eastmoney_data(
        self, 
        symbols: List[str]
    ) -> pd.DataFrame:
        """
        Get stock data from Eastmoney.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            DataFrame with stock data
        """
        try:
            await acquire_rate_limit('easyquotation', 'default')
            
            quoter = self._get_quoter()
            
            # Get Eastmoney data
            if hasattr(quoter, 'eastmoney_data'):
                data = quoter.eastmoney_data(symbols)
            else:
                return pd.DataFrame()
            
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            rows = []
            for symbol, item in data.items():
                rows.append({
                    'symbol': symbol,
                    'name': item.get('name', ''),
                    'current_price': item.get('current', 0),
                    'open': item.get('open', 0),
                    'high': item.get('high', 0),
                    'low': item.get('low', 0),
                    'volume': item.get('volume', 0),
                    'turnover': item.get('turnover', 0),
                    'change': item.get('change', 0),
                    'change_percent': item.get('change_percent', 0),
                    'pe_ratio': item.get('pe_ratio', 0),
                    'pb_ratio': item.get('pb_ratio', 0),
                    'market_cap': item.get('market_cap', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Eastmoney data: {e}")
            return pd.DataFrame()


# Convenience function for backward compatibility
async def call_easyquotation(
    function_name: str,
    params: Dict[str, Any],
    data_source: str = 'sina'
) -> Tuple[str, pd.DataFrame]:
    """
    Convenience function to call EasyQuotation functions.
    
    Args:
        function_name: Function name to call
        params: Parameters for the function
        data_source: Data source name
        
    Returns:
        Tuple of (function_name, DataFrame)
    """
    adapter = EasyQuotationAdapter(data_source=data_source)
    
    # Sina finance data
    if function_name == 'stock_quotes':
        df = await adapter.get_stock_quotes(
            symbols=params.get('symbols', [])
        )
        return 'stock_quotes', df
    
    elif function_name == 'market_overview':
        df = await adapter.get_market_overview()
        return 'market_overview', df
    
    elif function_name == 'sector_data':
        df = await adapter.get_sector_data()
        return 'sector_data', df
    
    elif function_name == 'stock_rankings':
        df = await adapter.get_stock_rankings(
            rank_type=params.get('rank_type', 'change_percent'),
            limit=params.get('limit', 50)
        )
        return 'stock_rankings', df
    
    # Jisilu bond data
    elif function_name == 'convertible_bonds':
        df = await adapter.get_convertible_bonds()
        return 'convertible_bonds', df
    
    elif function_name == 'bond_info':
        df = await adapter.get_bond_info(
            bond_code=params.get('bond_code')
        )
        return 'bond_info', df
    
    elif function_name == 'bond_yield_curve':
        df = await adapter.get_bond_yield_curve(
            bond_type=params.get('bond_type', 'government')
        )
        return 'bond_yield_curve', df
    
    # Tencent data
    elif function_name == 'tencent_quotes':
        df = await adapter.get_tencent_quotes(
            symbols=params.get('symbols', [])
        )
        return 'tencent_quotes', df
    
    # Eastmoney data
    elif function_name == 'eastmoney_data':
        df = await adapter.get_eastmoney_data(
            symbols=params.get('symbols', [])
        )
        return 'eastmoney_data', df
    
    else:
        raise EasyQuotationAdapterError(f"Unknown function: {function_name}")