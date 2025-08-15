import re
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "ak_unified"

# The coverage registry is dynamically derived from code, not manually duplicated.
# This test enforces that any upstream API referenced in adapters or registry is accounted for.

PATTERNS = {
    'akshare_call': re.compile(r"\bcall_akshare\(\s*\[\s*'(?P<api>[a-zA-Z0-9_]+)'"),
    'akshare_registry': re.compile(r"ak_functions=\[(?P<inside>[^\]]+)\]"),
    'akshare_fn': re.compile(r"'([a-zA-Z0-9_]+)'"),
    'yfinance': re.compile(r"yf\.download\(|yf\.Ticker\("),
    'efinance': re.compile(r"ef\.stock\.([a-zA-Z0-9_]+)\("),
    'ibkr': re.compile(r"\b(req(?:MktData|HistoricalData|FundamentalData)Async|req(?:MktData|HistoricalData|FundamentalData)|connectAsync|connect|qualifyContractsAsync|qualifyContracts)\b"),
    'baostock': re.compile(r"\bbaostock\.(query_|unsupported)"),  # via returned tag string
    'mootdx': re.compile(r"\bmootdx\.(bars|block_|xdxr|finance|unsupported)"),
    'qstock': re.compile(r"\bqstock\.(realtime|history|industries|concepts|block_members|announcements|unsupported)"),
    'adata': re.compile(r"\badata\.(get_history|get_quotes|industries|concepts|block_members|announcements|unsupported)"),
    'snowball': re.compile(r"\bsnowball\.(quote_detail|financial_report|research_report|sentiment|market_overview|discussion)\b"),
    'qmt': re.compile(r"\bqmt\b"),
}

ADAPTER_FILES = {
    'akshare': list((SRC / 'adapters').glob('**/akshare_adapter.py')),
    'yfinance': list((SRC / 'adapters').glob('**/yfinance_adapter.py')),
    'efinance': list((SRC / 'adapters').glob('**/efinance_adapter.py')),
    'ibkr': list((SRC / 'adapters').glob('**/ibkr_adapter.py')),
    'baostock': list((SRC / 'adapters').glob('**/baostock_adapter.py')),
    'mootdx': list((SRC / 'adapters').glob('**/mootdx_adapter.py')),
    'qstock': list((SRC / 'adapters').glob('**/qstock_adapter.py')),
    'adata': list((SRC / 'adapters').glob('**/adata_adapter.py')),
    'snowball': list((SRC / 'adapters').glob('**/snowball_adapter.py')),
    'qmt': list((SRC / 'adapters').glob('**/qmt_adapter.py')),
    'alphavantage': list((SRC / 'adapters').glob('**/alphavantage_adapter.py')),
    'earnings_calendar': list((SRC / 'adapters').glob('**/earnings_calendar_adapter.py')),
    'financial_data': list((SRC / 'adapters').glob('**/financial_data_adapter.py')),
}

@pytest.mark.unit
def test_unified_adapter_api_coverage_enforced():
    missing = []

    # akshare APIs from adapters
    ak_apis_from_adapters = set()
    for path in ADAPTER_FILES['akshare'] + ADAPTER_FILES['earnings_calendar'] + ADAPTER_FILES['financial_data']:
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['akshare_call'].finditer(txt):
            ak_apis_from_adapters.add(m.group('api'))

    # akshare APIs from registry
    reg_txt = (SRC / 'registry.py').read_text(encoding='utf-8', errors='ignore')
    ak_apis_from_registry = set()
    for m in PATTERNS['akshare_registry'].finditer(reg_txt):
        inside = m.group('inside')
        for fn in PATTERNS['akshare_fn'].finditer(inside):
            ak_apis_from_registry.add(fn.group(1))

    ak_all = ak_apis_from_adapters | ak_apis_from_registry
    assert ak_all, "No AkShare APIs found in adapters/registry; scan likely broken"

    # yfinance presence
    yf_hits = 0
    for path in ADAPTER_FILES['yfinance'] + ADAPTER_FILES['earnings_calendar'] + ADAPTER_FILES['financial_data']:
        txt = path.read_text(encoding='utf-8', errors='ignore')
        yf_hits += len(PATTERNS['yfinance'].findall(txt))
    assert yf_hits >= 1, "No yfinance API usage detected"

    # efinance presence and function names
    ef_calls = set()
    for path in ADAPTER_FILES['efinance']:
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['efinance'].finditer(txt):
            ef_calls.add('stock.' + m.group(1))
    assert ef_calls, "No efinance API usage detected"

    # ibkr presence
    ib_hits = set()
    for path in ADAPTER_FILES['ibkr']:
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['ibkr'].finditer(txt):
            ib_hits.add(m.group(1))
    assert ib_hits, "No IBKR API usage detected"

    # Other adapters presence markers
    for key in ['baostock', 'mootdx', 'qstock', 'adata', 'snowball', 'qmt', 'alphavantage']:
        paths = ADAPTER_FILES[key]
        assert paths, f"Missing adapter file for {key}"
        txt = ''.join(p.read_text(encoding='utf-8', errors='ignore') for p in paths)
        # For alphavantage we rely on presence of call_alphavantage
        if key == 'alphavantage':
            assert 'async def call_alphavantage' in txt
            continue
        # For others, ensure pattern matches or function names appear in returned tags
        pat = PATTERNS.get(key)
        if pat is not None:
            assert pat.search(txt), f"No usage pattern detected for {key}"

    # AkShare registry/adapters mismatch report
    only_in_adapters = sorted(ak_apis_from_adapters - ak_apis_from_registry)
    only_in_registry = sorted(ak_apis_from_registry - ak_apis_from_adapters)
    problems = []
    if only_in_adapters:
        problems.append("akshare in registry: " + ", ".join(only_in_adapters))
    if only_in_registry:
        problems.append("akshare in adapters: " + ", ".join(only_in_registry))
    if problems:
        pytest.fail("Adapter API coverage mismatch: " + " | ".join(problems))