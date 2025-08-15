import re
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "ak_unified"

# Registry of expected upstream API identifiers per adapter
# Add concrete invocation tests elsewhere; this file enforces that any introduced API is declared here.
REGISTRY = {
    'akshare': {
        'stock_financial_abstract',
        'stock_financial_abstract_ths',
        'stock_notice_report',
        'stock_financial_us_report_em',
        'stock_financial_hk_report_em',
        'stock_profit_forecast_em',
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
        'stock_financial_debt_ths',
        'stock_financial_benefit_ths',
        'stock_financial_cash_ths',
    },
    'yfinance': {
        'download',  # yf.download
        'Ticker.fast_info',
    },
    'efinance': {
        'stock.get_quote_history',
        'stock.get_realtime_quotes',
        'stock.get_index_stocks',
        'stock.get_money_flow',
        'stock.get_fund_flow',
        'stock.get_industries',
        'stock.get_industry_plate',
        'stock.get_plate_list',
        'stock.get_concepts',
        'stock.get_concept_plate',
        'stock.get_plate_stocks',
        'stock.get_industry_stocks',
        'stock.get_concept_stocks',
        'stock.get_announcement',
        'stock.get_announce',
        'stock.get_company_announcement',
    },
    'ibkr': {
        'connectAsync', 'connect',
        'qualifyContractsAsync', 'qualifyContracts',
        'reqHistoricalDataAsync', 'reqHistoricalData',
        'reqMktDataAsync', 'reqMktData',
        'reqFundamentalDataAsync', 'reqFundamentalData',
    },
    # Stubs for other adapters to ensure they appear in unified policy; expand as needed
    'alphavantage': set(),
    'mootdx': set(),
    'qstock': set(),
    'baostock': set(),
    'snowball': set(),
    'easytrader': set(),
    'adata': set(),
    'qmt': set(),
}

PATTERNS = {
    'akshare': re.compile(r"\bcall_akshare\(\s*\[\s*'(?P<api>[a-zA-Z0-9_]+)'"),
    'yfinance': re.compile(r"yf\.download\(|yf\.Ticker\("),
    'efinance': re.compile(r"ef\.stock\.([a-zA-Z0-9_]+)\("),
    'ibkr': re.compile(r"\b(req(?:MktData|HistoricalData|FundamentalData)Async|req(?:MktData|HistoricalData|FundamentalData)|connectAsync|connect|qualifyContractsAsync|qualifyContracts)\b"),
}

@pytest.mark.unit
def test_unified_adapter_api_coverage_enforced():
    missing = []

    # akshare
    ak_apis = set()
    for path in (SRC / 'adapters').glob('**/*.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['akshare'].finditer(txt):
            ak_apis.add(m.group('api'))
    for api in sorted(ak_apis):
        if api not in REGISTRY['akshare']:
            missing.append(f"akshare:{api}")

    # yfinance
    yf_hits = 0
    for path in (SRC / 'adapters').glob('**/yfinance_adapter.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        yf_hits += len(PATTERNS['yfinance'].findall(txt))
    if yf_hits and not REGISTRY['yfinance']:
        missing.append("yfinance:registry-empty")

    # efinance
    ef_calls = set()
    for path in (SRC / 'adapters').glob('**/efinance_adapter.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['efinance'].finditer(txt):
            ef_calls.add('stock.' + m.group(1))
    for api in sorted(ef_calls):
        if api not in REGISTRY['efinance']:
            missing.append(f"efinance:{api}")

    # ibkr
    ib_hits = set()
    for path in (SRC / 'adapters').glob('**/ibkr_adapter.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['ibkr'].finditer(txt):
            ib_hits.add(m.group(1))
    for api in sorted(ib_hits):
        if api not in REGISTRY['ibkr']:
            missing.append(f"ibkr:{api}")

    if missing:
        pytest.fail("Missing adapter API coverage entries: " + ", ".join(missing))