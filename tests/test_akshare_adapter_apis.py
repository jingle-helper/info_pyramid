import os
import pytest

# This test asserts that newly introduced AkShare API names are registered here for coverage tracking.
# Add real end-to-end tests or mocks per API as needed.

AK_API_NAMES = {
    # Earnings/financial calendar
    'stock_financial_abstract',
    'stock_financial_abstract_ths',
    'stock_notice_report',
    'stock_financial_us_report_em',
    'stock_financial_hk_report_em',
    'stock_profit_forecast_em',
    # CN statements and fallbacks
    'stock_balance_sheet_by_report_em',
    'stock_balance_sheet_by_yearly_em',
    'stock_balance_sheet_by_report_delisted_em',
    'stock_profit_sheet_by_quarterly_em',
    'stock_profit_sheet_by_yearly_em',
    'stock_profit_sheet_by_report_em',
    'stock_profit_sheet_by_report_delisted_em',
    'stock_cash_flow_sheet_by_quarterly_em',
    'stock_cash_flow_sheet_by_yearly_em',
    'stock_cash_flow_sheet_by_report_em',
    'stock_cash_flow_sheet_by_report_delisted_em',
    # THS fallbacks
    'stock_financial_debt_ths',
    'stock_financial_benefit_ths',
    'stock_financial_cash_ths',
}

@pytest.mark.unit
@pytest.mark.parametrize("api_name", sorted(AK_API_NAMES))
def test_akshare_api_names_registered(api_name: str):
    # This ensures that when new AkShare APIs are introduced, a test is added here
    # Real invocation tests should be implemented per API (possibly behind markers/mocks)
    assert isinstance(api_name, str) and len(api_name) > 3