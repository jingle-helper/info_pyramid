"""
Snowball Adapter

Provides access to Snowball data including:
- Stock information and quotes
- Financial data and reports
- Research reports and analysis
- User discussions and sentiment
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .base import BaseAdapterError
from ..rate_limiter import acquire_rate_limit
from ..logging import logger


class SnowballAdapterError(BaseAdapterError):
    """Snowball adapter specific error."""
    pass


class SnowballAdapter:
    """Adapter for Snowball data from pysnowball library."""
    
    def __init__(self, token: Optional[str] = None):
        self.supported_markets = ['cn', 'hk', 'us']
        self._snowball = None
        self._token = token
        
        # Set token if provided
        if token:
            self._set_token(token)
    
    def _set_token(self, token: str):
        """Set Snowball token for authentication."""
        try:
            import pysnowball as snowball
            snowball.set_token(token)
        except Exception as e:
            logger.warning(f"Failed to set Snowball token: {e}")
    
    def set_token(self, token: str):
        """Set Snowball token for authentication."""
        self._token = token
        self._set_token(token)
    
    def _import_snowball(self):
        """Import pysnowball library."""
        try:
            import pysnowball as snowball
            return snowball
        except ImportError:
            raise SnowballAdapterError("Failed to import pysnowball. Please install: pip install pysnowball")
    
    async def get_stock_quote(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get stock quote from Snowball.
        
        Args:
            symbol: Stock symbol
            market: Market code ('cn' for China, 'hk' for Hong Kong, 'us' for US)
            
        Returns:
            DataFrame with stock quote data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get stock quote
            quote_data = snowball.quote_detail(symbol)
            
            if not quote_data or 'data' not in quote_data:
                return pd.DataFrame()
            
            data = quote_data['data']
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'symbol': symbol,
                'market': market,
                'name': data.get('name', ''),
                'current': data.get('current', 0),
                'change': data.get('change', 0),
                'change_percent': data.get('change_percent', 0),
                'open': data.get('open', 0),
                'high': data.get('high', 0),
                'low': data.get('low', 0),
                'volume': data.get('volume', 0),
                'market_cap': data.get('market_cap', 0),
                'pe_ratio': data.get('pe_ratio', 0),
                'pb_ratio': data.get('pb_ratio', 0),
                'dividend_yield': data.get('dividend_yield', 0),
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball stock quote for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_stock_financial_data(
        self, 
        symbol: str, 
        market: str = 'cn',
        period: str = 'annual'
    ) -> pd.DataFrame:
        """
        Get stock financial data from Snowball.
        
        Args:
            symbol: Stock symbol
            market: Market code
            period: Period type ('annual' or 'quarterly')
            
        Returns:
            DataFrame with financial data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get financial data
            if period == 'quarterly':
                financial_data = snowball.financial_report(symbol, 'Q')
            else:
                financial_data = snowball.financial_report(symbol, 'Y')
            
            if not financial_data or 'data' not in financial_data:
                return pd.DataFrame()
            
            data = financial_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'symbol': symbol,
                    'market': market,
                    'period': item.get('period', ''),
                    'report_date': item.get('report_date', ''),
                    'revenue': item.get('revenue', 0),
                    'net_profit': item.get('net_profit', 0),
                    'eps': item.get('eps', 0),
                    'roe': item.get('roe', 0),
                    'roa': item.get('roa', 0),
                    'gross_margin': item.get('gross_margin', 0),
                    'net_margin': item.get('net_margin', 0),
                    'debt_ratio': item.get('debt_ratio', 0),
                    'current_ratio': item.get('current_ratio', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball financial data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_stock_research_reports(
        self, 
        symbol: str, 
        market: str = 'cn',
        limit: int = 20
    ) -> pd.DataFrame:
        """
        Get stock research reports from Snowball.
        
        Args:
            symbol: Stock symbol
            market: Market code
            limit: Number of reports to return
            
        Returns:
            DataFrame with research report data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get research reports
            reports_data = snowball.research_report(symbol, limit)
            
            if not reports_data or 'data' not in reports_data:
                return pd.DataFrame()
            
            data = reports_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'symbol': symbol,
                    'market': market,
                    'title': item.get('title', ''),
                    'author': item.get('author', ''),
                    'institution': item.get('institution', ''),
                    'publish_date': item.get('publish_date', ''),
                    'rating': item.get('rating', ''),
                    'target_price': item.get('target_price', 0),
                    'summary': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball research reports for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_stock_sentiment(
        self, 
        symbol: str, 
        market: str = 'cn',
        days: int = 7
    ) -> pd.DataFrame:
        """
        Get stock sentiment data from Snowball.
        
        Args:
            symbol: Stock symbol
            market: Market code
            days: Number of days to analyze
            
        Returns:
            DataFrame with sentiment data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get sentiment data
            sentiment_data = snowball.sentiment(symbol, days)
            
            if not sentiment_data or 'data' not in sentiment_data:
                return pd.DataFrame()
            
            data = sentiment_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'symbol': symbol,
                    'market': market,
                    'date': item.get('date', ''),
                    'positive_count': item.get('positive_count', 0),
                    'negative_count': item.get('negative_count', 0),
                    'neutral_count': item.get('neutral_count', 0),
                    'sentiment_score': item.get('sentiment_score', 0),
                    'discussion_count': item.get('discussion_count', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball sentiment data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_stock_discussions(
        self, 
        symbol: str, 
        market: str = 'cn',
        limit: int = 50
    ) -> pd.DataFrame:
        """
        Get stock discussions from Snowball.
        
        Args:
            symbol: Stock symbol
            market: Market code
            limit: Number of discussions to return
            
        Returns:
            DataFrame with discussion data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get discussions
            discussions_data = snowball.discussion(symbol, limit)
            
            if not discussions_data or 'data' not in discussions_data:
                return pd.DataFrame()
            
            data = discussions_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'symbol': symbol,
                    'market': market,
                    'title': item.get('title', ''),
                    'content': item.get('content', ''),
                    'author': item.get('author', ''),
                    'publish_time': item.get('publish_time', ''),
                    'like_count': item.get('like_count', 0),
                    'comment_count': item.get('comment_count', 0),
                    'share_count': item.get('share_count', 0),
                    'sentiment': item.get('sentiment', ''),
                    'url': item.get('url', ''),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball discussions for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_market_overview(
        self, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get market overview from Snowball.
        
        Args:
            market: Market code
            
        Returns:
            DataFrame with market overview data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get market overview
            if market == 'cn':
                overview_data = snowball.market_overview('CN')
            elif market == 'hk':
                overview_data = snowball.market_overview('HK')
            elif market == 'us':
                overview_data = snowball.market_overview('US')
            else:
                return pd.DataFrame()
            
            if not overview_data or 'data' not in overview_data:
                return pd.DataFrame()
            
            data = overview_data['data']
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'market': market,
                'index_name': data.get('index_name', ''),
                'current_value': data.get('current_value', 0),
                'change': data.get('change', 0),
                'change_percent': data.get('change_percent', 0),
                'volume': data.get('volume', 0),
                'turnover': data.get('turnover', 0),
                'advance_count': data.get('advance_count', 0),
                'decline_count': data.get('decline_count', 0),
                'flat_count': data.get('flat_count', 0),
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball market overview for {market}: {e}")
            return pd.DataFrame()

    # ========== 新增功能：个股基础信息 ==========
    
    async def get_stock_basic_info(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get stock basic information including company profile, industry, etc.
        
        Args:
            symbol: Stock symbol
            market: Market code
            
        Returns:
            DataFrame with basic stock information
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get stock basic info
            basic_info = snowball.stock_info(symbol)
            
            if not basic_info or 'data' not in basic_info:
                return pd.DataFrame()
            
            data = basic_info['data']
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'symbol': symbol,
                'market': market,
                'name': data.get('name', ''),
                'english_name': data.get('english_name', ''),
                'industry': data.get('industry', ''),
                'sector': data.get('sector', ''),
                'market_cap': data.get('market_cap', 0),
                'pe_ratio': data.get('pe_ratio', 0),
                'pb_ratio': data.get('pb_ratio', 0),
                'ps_ratio': data.get('ps_ratio', 0),
                'dividend_yield': data.get('dividend_yield', 0),
                'beta': data.get('beta', 0),
                'shares_outstanding': data.get('shares_outstanding', 0),
                'float_shares': data.get('float_shares', 0),
                'insider_ownership': data.get('insider_ownership', 0),
                'institutional_ownership': data.get('institutional_ownership', 0),
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball stock basic info for {symbol}: {e}")
            return pd.DataFrame()

    async def get_stock_volume_price_analysis(
        self, 
        symbol: str, 
        market: str = 'cn',
        period: str = '1d'
    ) -> pd.DataFrame:
        """
        Get stock volume and price analysis data.
        
        Args:
            symbol: Stock symbol
            market: Market code
            period: Period ('1d', '5d', '1m', '3m', '6m', '1y')
            
        Returns:
            DataFrame with volume and price analysis
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get volume and price analysis
            vp_data = snowball.volume_price_analysis(symbol, period)
            
            if not vp_data or 'data' not in vp_data:
                return pd.DataFrame()
            
            data = vp_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'symbol': symbol,
                    'market': market,
                    'date': item.get('date', ''),
                    'open': item.get('open', 0),
                    'high': item.get('high', 0),
                    'low': item.get('low', 0),
                    'close': item.get('close', 0),
                    'volume': item.get('volume', 0),
                    'turnover': item.get('turnover', 0),
                    'amplitude': item.get('amplitude', 0),
                    'change_percent': item.get('change_percent', 0),
                    'ma5': item.get('ma5', 0),
                    'ma10': item.get('ma10', 0),
                    'ma20': item.get('ma20', 0),
                    'ma60': item.get('ma60', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball volume price analysis for {symbol}: {e}")
            return pd.DataFrame()

    async def get_stock_shareholder_structure(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get stock shareholder structure information.
        
        Args:
            symbol: Stock symbol
            market: Market code
            
        Returns:
            DataFrame with shareholder structure data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get shareholder structure
            shareholder_data = snowball.shareholder_structure(symbol)
            
            if not shareholder_data or 'data' not in shareholder_data:
                return pd.DataFrame()
            
            data = shareholder_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'symbol': symbol,
                    'market': market,
                    'report_date': item.get('report_date', ''),
                    'shareholder_name': item.get('shareholder_name', ''),
                    'shareholder_type': item.get('shareholder_type', ''),
                    'shares_held': item.get('shares_held', 0),
                    'shares_percent': item.get('shares_percent', 0),
                    'change_shares': item.get('change_shares', 0),
                    'change_percent': item.get('change_percent', 0),
                    'rank': item.get('rank', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball shareholder structure for {symbol}: {e}")
            return pd.DataFrame()

    async def get_stock_fund_flow(
        self, 
        symbol: str, 
        market: str = 'cn',
        period: str = '1d'
    ) -> pd.DataFrame:
        """
        Get stock fund flow data.
        
        Args:
            symbol: Stock symbol
            market: Market code
            period: Period ('1d', '5d', '10d', '1m', '3m')
            
        Returns:
            DataFrame with fund flow data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get fund flow data
            flow_data = snowball.fund_flow(symbol, period)
            
            if not flow_data or 'data' not in flow_data:
                return pd.DataFrame()
            
            data = flow_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'symbol': symbol,
                    'market': market,
                    'date': item.get('date', ''),
                    'main_net_inflow': item.get('main_net_inflow', 0),
                    'retail_net_inflow': item.get('retail_net_inflow', 0),
                    'super_large_net_inflow': item.get('super_large_net_inflow', 0),
                    'large_net_inflow': item.get('large_net_inflow', 0),
                    'medium_net_inflow': item.get('medium_net_inflow', 0),
                    'small_net_inflow': item.get('small_net_inflow', 0),
                    'total_net_inflow': item.get('total_net_inflow', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball fund flow for {symbol}: {e}")
            return pd.DataFrame()

    # ========== 新增功能：债券数据 ==========
    
    async def get_bond_info(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get bond basic information.
        
        Args:
            symbol: Bond symbol
            market: Market code
            
        Returns:
            DataFrame with bond information
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get bond info
            bond_data = snowball.bond_info(symbol)
            
            if not bond_data or 'data' not in bond_data:
                return pd.DataFrame()
            
            data = bond_data['data']
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'symbol': symbol,
                'market': market,
                'name': data.get('name', ''),
                'bond_type': data.get('bond_type', ''),
                'issue_date': data.get('issue_date', ''),
                'maturity_date': data.get('maturity_date', ''),
                'face_value': data.get('face_value', 0),
                'coupon_rate': data.get('coupon_rate', 0),
                'payment_frequency': data.get('payment_frequency', ''),
                'credit_rating': data.get('credit_rating', ''),
                'current_price': data.get('current_price', 0),
                'yield_to_maturity': data.get('yield_to_maturity', 0),
                'duration': data.get('duration', 0),
                'convexity': data.get('convexity', 0),
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball bond info for {symbol}: {e}")
            return pd.DataFrame()

    async def get_convertible_bond_info(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get convertible bond specific information.
        
        Args:
            symbol: Convertible bond symbol
            market: Market code
            
        Returns:
            DataFrame with convertible bond data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get convertible bond info
            cb_data = snowball.convertible_bond_info(symbol)
            
            if not cb_data or 'data' not in cb_data:
                return pd.DataFrame()
            
            data = cb_data['data']
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'symbol': symbol,
                'market': market,
                'name': data.get('name', ''),
                'underlying_stock': data.get('underlying_stock', ''),
                'conversion_price': data.get('conversion_price', 0),
                'conversion_ratio': data.get('conversion_ratio', 0),
                'conversion_value': data.get('conversion_value', 0),
                'premium_rate': data.get('premium_rate', 0),
                'issue_date': data.get('issue_date', ''),
                'maturity_date': data.get('maturity_date', ''),
                'face_value': data.get('face_value', 0),
                'coupon_rate': data.get('coupon_rate', 0),
                'current_price': data.get('current_price', 0),
                'yield_to_maturity': data.get('yield_to_maturity', 0),
                'delta': data.get('delta', 0),
                'gamma': data.get('gamma', 0),
                'theta': data.get('theta', 0),
                'vega': data.get('vega', 0),
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball convertible bond info for {symbol}: {e}")
            return pd.DataFrame()

    async def get_bond_yield_curve(
        self, 
        market: str = 'cn',
        bond_type: str = 'government'
    ) -> pd.DataFrame:
        """
        Get bond yield curve data.
        
        Args:
            market: Market code
            bond_type: Bond type ('government', 'corporate', 'municipal')
            
        Returns:
            DataFrame with yield curve data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get yield curve
            curve_data = snowball.yield_curve(market, bond_type)
            
            if not curve_data or 'data' not in curve_data:
                return pd.DataFrame()
            
            data = curve_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'market': market,
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
            logger.warning(f"Failed to get Snowball yield curve for {market}: {e}")
            return pd.DataFrame()

    # ========== 新增功能：指数构成与权重 ==========
    
    async def get_index_info(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get index basic information.
        
        Args:
            symbol: Index symbol
            market: Market code
            
        Returns:
            DataFrame with index information
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get index info
            index_data = snowball.index_info(symbol)
            
            if not index_data or 'data' not in index_data:
                return pd.DataFrame()
            
            data = index_data['data']
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'symbol': symbol,
                'market': market,
                'name': data.get('name', ''),
                'english_name': data.get('english_name', ''),
                'index_type': data.get('index_type', ''),
                'base_date': data.get('base_date', ''),
                'base_value': data.get('base_value', 0),
                'current_value': data.get('current_value', 0),
                'total_return': data.get('total_return', 0),
                'price_return': data.get('price_return', 0),
                'dividend_yield': data.get('dividend_yield', 0),
                'pe_ratio': data.get('pe_ratio', 0),
                'pb_ratio': data.get('pb_ratio', 0),
                'constituent_count': data.get('constituent_count', 0),
                'timestamp': datetime.now()
            }])
            
            return df
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball index info for {symbol}: {e}")
            return pd.DataFrame()

    async def get_index_constituents(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get index constituents with weights.
        
        Args:
            symbol: Index symbol
            market: Market code
            
        Returns:
            DataFrame with index constituents data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get index constituents
            constituents_data = snowball.index_constituents(symbol)
            
            if not constituents_data or 'data' not in constituents_data:
                return pd.DataFrame()
            
            data = constituents_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'index_symbol': symbol,
                    'market': market,
                    'constituent_symbol': item.get('symbol', ''),
                    'constituent_name': item.get('name', ''),
                    'weight': item.get('weight', 0),
                    'shares': item.get('shares', 0),
                    'market_cap': item.get('market_cap', 0),
                    'sector': item.get('sector', ''),
                    'industry': item.get('industry', ''),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball index constituents for {symbol}: {e}")
            return pd.DataFrame()

    async def get_index_sector_weight(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get index sector weight distribution.
        
        Args:
            symbol: Index symbol
            market: Market code
            
        Returns:
            DataFrame with sector weight data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get sector weights
            sector_data = snowball.index_sector_weight(symbol)
            
            if not sector_data or 'data' not in sector_data:
                return pd.DataFrame()
            
            data = sector_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'index_symbol': symbol,
                    'market': market,
                    'sector': item.get('sector', ''),
                    'weight': item.get('weight', 0),
                    'constituent_count': item.get('constituent_count', 0),
                    'market_cap': item.get('market_cap', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball sector weight for {symbol}: {e}")
            return pd.DataFrame()

    async def get_index_industry_weight(
        self, 
        symbol: str, 
        market: str = 'cn'
    ) -> pd.DataFrame:
        """
        Get index industry weight distribution.
        
        Args:
            symbol: Index symbol
            market: Market code
            
        Returns:
            DataFrame with industry weight data
        """
        try:
            await acquire_rate_limit('snowball', 'default')
            
            snowball = self._import_snowball()
            
            # Get industry weights
            industry_data = snowball.index_industry_weight(symbol)
            
            if not industry_data or 'data' not in industry_data:
                return pd.DataFrame()
            
            data = industry_data['data']
            
            # Convert to DataFrame
            rows = []
            for item in data:
                rows.append({
                    'index_symbol': symbol,
                    'market': market,
                    'industry': item.get('industry', ''),
                    'weight': item.get('weight', 0),
                    'constituent_count': item.get('constituent_count', 0),
                    'market_cap': item.get('market_cap', 0),
                    'timestamp': datetime.now()
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.warning(f"Failed to get Snowball industry weight for {symbol}: {e}")
            return pd.DataFrame()


# Convenience function for backward compatibility
async def call_snowball(
    function_name: str,
    params: Dict[str, Any],
    market: str = 'cn'
) -> Tuple[str, pd.DataFrame]:
    """
    Convenience function to call Snowball functions.
    
    Args:
        function_name: Function name to call
        params: Parameters for the function
        market: Market code
        
    Returns:
        Tuple of (function_name, DataFrame)
    """
    # Get token from params or environment
    token = params.get('token') or params.get('xq_a_token')
    adapter = SnowballAdapter(token=token)
    
    if function_name == 'stock_quote':
        df = await adapter.get_stock_quote(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'financial_data':
        df = await adapter.get_stock_financial_data(
            symbol=params.get('symbol'),
            market=params.get('market', market),
            period=params.get('period', 'annual')
        )
    elif function_name == 'research_reports':
        df = await adapter.get_stock_research_reports(
            symbol=params.get('symbol'),
            market=params.get('market', market),
            limit=params.get('limit', 20)
        )
    elif function_name == 'sentiment':
        df = await adapter.get_stock_sentiment(
            symbol=params.get('symbol'),
            market=params.get('market', market),
            days=params.get('days', 7)
        )
    elif function_name == 'discussions':
        df = await adapter.get_stock_discussions(
            symbol=params.get('symbol'),
            market=params.get('market', market),
            limit=params.get('limit', 50)
        )
    elif function_name == 'market_overview':
        df = await adapter.get_market_overview(
            market=params.get('market', market)
        )
    
    # ========== 新增功能调用 ==========
    
    # 个股基础信息
    elif function_name == 'stock_basic_info':
        df = await adapter.get_stock_basic_info(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'volume_price_analysis':
        df = await adapter.get_stock_volume_price_analysis(
            symbol=params.get('symbol'),
            market=params.get('market', market),
            period=params.get('period', '1d')
        )
    elif function_name == 'shareholder_structure':
        df = await adapter.get_stock_shareholder_structure(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'fund_flow':
        df = await adapter.get_stock_fund_flow(
            symbol=params.get('symbol'),
            market=params.get('market', market),
            period=params.get('period', '1d')
        )
    
    # 债券数据
    elif function_name == 'bond_info':
        df = await adapter.get_bond_info(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'convertible_bond_info':
        df = await adapter.get_convertible_bond_info(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'bond_yield_curve':
        df = await adapter.get_bond_yield_curve(
            market=params.get('market', market),
            bond_type=params.get('bond_type', 'government')
        )
    
    # 指数数据
    elif function_name == 'index_info':
        df = await adapter.get_index_info(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'index_constituents':
        df = await adapter.get_index_constituents(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'index_sector_weight':
        df = await adapter.get_index_sector_weight(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    elif function_name == 'index_industry_weight':
        df = await adapter.get_index_industry_weight(
            symbol=params.get('symbol'),
            market=params.get('market', market)
        )
    
    else:
        raise SnowballAdapterError(f"Unknown function: {function_name}")
    
    return function_name, df