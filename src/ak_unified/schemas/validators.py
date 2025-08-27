"""
Data validation and transformation utilities for AK Unified.
This module ensures that all adapter outputs conform to the core schema definitions.
"""

from __future__ import annotations

import pandas as pd
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re

from .core import (
    MacroIndicator, MarketQuote, OHLCVBar, IndexConstituent, CapitalFlow,
    TradingCalendar, CorporateAction, FundNAV, BondQuote, BondCurve,
    FuturesContract, FuturesQuote, OptionContract, OptionQuote
)


class DataValidator:
    """Validates and transforms data to conform to core schemas."""
    
    @staticmethod
    def validate_macro_indicator(data: Dict[str, Any]) -> MacroIndicator:
        """Validate and transform macro indicator data."""
        # Standardize field names
        field_mapping = {
            'region': ['region', 'country', 'market'],
            'indicator_id': ['indicator_id', 'indicator_code', 'code'],
            'indicator_name': ['indicator_name', 'name', 'indicator'],
            'date': ['date', 'report_date', 'period'],
            'value': ['value', 'data', 'amount'],
            'unit': ['unit', 'currency'],
            'source': ['source', 'data_source'],
            'release_time': ['release_time', 'publish_time', 'update_time'],
            'period': ['period', 'freq', 'frequency'],
            'revised': ['revised', 'is_revised', 'revision']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            
            if target_field == 'period' and value:
                # Normalize period values
                if isinstance(value, str):
                    value = value.upper()
                    if value in ['M', 'MONTH', 'MONTHLY']:
                        value = 'M'
                    elif value in ['Q', 'QUARTER', 'QUARTERLY']:
                        value = 'Q'
                    elif value in ['Y', 'YEAR', 'YEARLY', 'ANNUAL']:
                        value = 'Y'
            
            transformed[target_field] = value
        
        # Ensure required fields have defaults if missing
        if 'region' not in transformed or not transformed['region']:
            transformed['region'] = 'CN'
        
        return MacroIndicator(**transformed)
    
    @staticmethod
    def validate_market_quote(data: Dict[str, Any]) -> MarketQuote:
        """Validate and transform market quote data."""
        field_mapping = {
            'symbol': ['symbol', 'code', 'ticker'],
            'symbol_name': ['symbol_name', 'name', 'stock_name'],
            'datetime': ['datetime', 'date', 'time', 'timestamp'],
            'last': ['last', 'close', 'price', 'current_price'],
            'open': ['open', 'open_price'],
            'high': ['high', 'high_price', 'highest'],
            'low': ['low', 'low_price', 'lowest'],
            'prev_close': ['prev_close', 'previous_close', 'yesterday_close'],
            'change': ['change', 'price_change', 'change_amount'],
            'pct_change': ['pct_change', 'change_pct', 'change_percent'],
            'volume': ['volume', 'vol', 'trading_volume'],
            'amount': ['amount', 'turnover', 'trading_amount'],
            'turnover_rate': ['turnover_rate', 'turnover_ratio'],
            'bid1': ['bid1', 'bid', 'buy1'],
            'ask1': ['ask1', 'ask', 'sell1']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return MarketQuote(**transformed)
    
    @staticmethod
    def validate_ohlcv_bar(data: Dict[str, Any]) -> OHLCVBar:
        """Validate and transform OHLCV bar data."""
        field_mapping = {
            'symbol': ['symbol', 'code', 'ticker'],
            'date': ['date', 'datetime', 'time', 'timestamp'],
            'open': ['open', 'open_price'],
            'high': ['high', 'high_price', 'highest'],
            'low': ['low', 'low_price', 'lowest'],
            'close': ['close', 'close_price', 'last'],
            'volume': ['volume', 'vol', 'trading_volume'],
            'amount': ['amount', 'turnover', 'trading_amount'],
            'adjust': ['adjust', 'adjustment', 'factor']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            
            if target_field == 'adjust' and value:
                # Normalize adjustment values
                if isinstance(value, str):
                    value = value.lower()
                    if value in ['none', 'no', '0']:
                        value = 'none'
                    elif value in ['qfq', 'forward', 'forward_adjust']:
                        value = 'qfq'
                    elif value in ['hfq', 'backward', 'backward_adjust']:
                        value = 'hfq'
            
            transformed[target_field] = value
        
        return OHLCVBar(**transformed)
    
    @staticmethod
    def validate_index_constituent(data: Dict[str, Any]) -> IndexConstituent:
        """Validate and transform index constituent data."""
        field_mapping = {
            'index_symbol': ['index_symbol', 'index_code', 'index'],
            'symbol': ['symbol', 'code', 'ticker', 'stock_code'],
            'symbol_name': ['symbol_name', 'name', 'stock_name'],
            'weight': ['weight', 'weighting', 'proportion'],
            'date': ['date', 'constituent_date', 'update_date']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return IndexConstituent(**transformed)
    
    @staticmethod
    def validate_capital_flow(data: Dict[str, Any]) -> CapitalFlow:
        """Validate and transform capital flow data."""
        field_mapping = {
            'symbol': ['symbol', 'code', 'ticker'],
            'date': ['date', 'datetime', 'time'],
            'main_inflow': ['main_inflow', 'main_net_inflow', 'main_force_inflow'],
            'main_outflow': ['main_outflow', 'main_net_outflow', 'main_force_outflow'],
            'net_inflow': ['net_inflow', 'net_flow', 'total_net_inflow'],
            'pct_main': ['pct_main', 'main_percentage', 'main_force_pct']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return CapitalFlow(**transformed)
    
    @staticmethod
    def validate_trading_calendar(data: Dict[str, Any]) -> TradingCalendar:
        """Validate and transform trading calendar data."""
        field_mapping = {
            'date': ['date', 'calendar_date', 'trading_date'],
            'is_trading_day': ['is_trading_day', 'trading_day', 'is_open'],
            'market': ['market', 'exchange', 'market_code'],
            'open_time': ['open_time', 'market_open', 'trading_start'],
            'close_time': ['close_time', 'market_close', 'trading_end']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            
            if target_field == 'is_trading_day' and value is not None:
                # Normalize boolean values
                if isinstance(value, str):
                    value = value.lower() in ['true', '1', 'yes', 'open', 'trading']
                elif isinstance(value, int):
                    value = bool(value)
            
            transformed[target_field] = value
        
        return TradingCalendar(**transformed)
    
    @staticmethod
    def validate_corporate_action(data: Dict[str, Any]) -> CorporateAction:
        """Validate and transform corporate action data."""
        field_mapping = {
            'symbol': ['symbol', 'code', 'ticker'],
            'action_type': ['action_type', 'type', 'event_type'],
            'ex_date': ['ex_date', 'ex_dividend_date', 'record_date'],
            'record_date': ['record_date', 'record_date_actual'],
            'payable_date': ['payable_date', 'payment_date', 'distribution_date'],
            'cash_dividend': ['cash_dividend', 'dividend', 'cash_payment'],
            'stock_dividend_ratio': ['stock_dividend_ratio', 'stock_dividend', 'bonus_ratio'],
            'split_ratio': ['split_ratio', 'split', 'stock_split']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return CorporateAction(**transformed)
    
    @staticmethod
    def validate_fund_nav(data: Dict[str, Any]) -> FundNAV:
        """Validate and transform fund NAV data."""
        field_mapping = {
            'fund_code': ['fund_code', 'code', 'ticker'],
            'fund_name': ['fund_name', 'name', 'fund_title'],
            'nav_date': ['nav_date', 'date', 'valuation_date'],
            'nav': ['nav', 'net_asset_value', 'unit_nav'],
            'acc_nav': ['acc_nav', 'accumulated_nav', 'cumulative_nav'],
            'daily_return': ['daily_return', 'return', 'daily_change'],
            'subscription_status': ['subscription_status', 'purchase_status'],
            'redemption_status': ['redemption_status', 'sell_status'],
            'fee': ['fee', 'management_fee', 'expense_ratio']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return FundNAV(**transformed)
    
    @staticmethod
    def validate_bond_quote(data: Dict[str, Any]) -> BondQuote:
        """Validate and transform bond quote data."""
        field_mapping = {
            'symbol': ['symbol', 'code', 'bond_code'],
            'date': ['date', 'datetime', 'quote_date'],
            'yield_': ['yield', 'yield_rate', 'current_yield'],
            'duration': ['duration', 'modified_duration'],
            'ytm': ['ytm', 'yield_to_maturity'],
            'clean_price': ['clean_price', 'price', 'current_price'],
            'dirty_price': ['dirty_price', 'full_price'],
            'coupon': ['coupon', 'coupon_rate', 'interest_rate'],
            'maturity_date': ['maturity_date', 'maturity', 'due_date']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return BondQuote(**transformed)
    
    @staticmethod
    def validate_futures_quote(data: Dict[str, Any]) -> FuturesQuote:
        """Validate and transform futures quote data."""
        field_mapping = {
            'contract': ['contract', 'symbol', 'code'],
            'date': ['date', 'datetime', 'trading_date'],
            'open': ['open', 'open_price'],
            'high': ['high', 'high_price', 'highest'],
            'low': ['low', 'low_price', 'lowest'],
            'close': ['close', 'close_price', 'last'],
            'settlement': ['settlement', 'settlement_price'],
            'volume': ['volume', 'vol', 'trading_volume'],
            'open_interest': ['open_interest', 'oi', 'open_interest_volume'],
            'basis': ['basis', 'basis_price', 'cash_basis']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return FuturesQuote(**transformed)
    
    @staticmethod
    def validate_option_quote(data: Dict[str, Any]) -> OptionQuote:
        """Validate and transform option quote data."""
        field_mapping = {
            'contract': ['contract', 'symbol', 'code'],
            'datetime': ['datetime', 'date', 'time', 'timestamp'],
            'last': ['last', 'last_price', 'current_price'],
            'bid': ['bid', 'bid_price', 'buy_price'],
            'ask': ['ask', 'ask_price', 'sell_price'],
            'volume': ['volume', 'vol', 'trading_volume'],
            'open_interest': ['open_interest', 'oi', 'open_interest_volume'],
            'iv': ['iv', 'implied_volatility', 'volatility'],
            'delta': ['delta', 'delta_value'],
            'gamma': ['gamma', 'gamma_value'],
            'vega': ['vega', 'vega_value'],
            'theta': ['theta', 'theta_value'],
            'rho': ['rho', 'rho_value']
        }
        
        transformed = {}
        for target_field, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                if field in data and data[field] is not None:
                    value = data[field]
                    break
            transformed[target_field] = value
        
        return OptionQuote(**transformed)


def validate_dataframe_to_schema(df: pd.DataFrame, schema_class: type, **kwargs) -> List[Any]:
    """
    Validate and transform a pandas DataFrame to a list of schema instances.
    
    Args:
        df: Input DataFrame
        schema_class: Target schema class from core.py
        **kwargs: Additional arguments for validation
    
    Returns:
        List of validated schema instances
    """
    if df.empty:
        return []
    
    validator = DataValidator()
    validated_data = []
    
    for _, row in df.iterrows():
        data_dict = row.to_dict()
        
        try:
            if schema_class == MacroIndicator:
                validated = validator.validate_macro_indicator(data_dict)
            elif schema_class == MarketQuote:
                validated = validator.validate_market_quote(data_dict)
            elif schema_class == OHLCVBar:
                validated = validator.validate_ohlcv_bar(data_dict)
            elif schema_class == IndexConstituent:
                validated = validator.validate_index_constituent(data_dict)
            elif schema_class == CapitalFlow:
                validated = validator.validate_capital_flow(data_dict)
            elif schema_class == TradingCalendar:
                validated = validator.validate_trading_calendar(data_dict)
            elif schema_class == CorporateAction:
                validated = validator.validate_corporate_action(data_dict)
            elif schema_class == FundNAV:
                validated = validator.validate_fund_nav(data_dict)
            elif schema_class == BondQuote:
                validated = validator.validate_bond_quote(data_dict)
            elif schema_class == FuturesQuote:
                validated = validator.validate_futures_quote(data_dict)
            elif schema_class == OptionQuote:
                validated = validator.validate_option_quote(data_dict)
            else:
                raise ValueError(f"Unsupported schema class: {schema_class}")
            
            validated_data.append(validated)
            
        except Exception as e:
            # Log validation errors but continue processing
            print(f"Validation error for row {row}: {e}")
            continue
    
    return validated_data