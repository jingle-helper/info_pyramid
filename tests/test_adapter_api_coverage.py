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
}

@pytest.mark.unit
def test_unified_adapter_api_coverage_enforced():
    missing = []

    # akshare APIs from adapters
    ak_apis_from_adapters = set()
    for path in (SRC / 'adapters').glob('**/*.py'):
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

    # yfinance presence (symbolic check)
    yf_hits = 0
    for path in (SRC / 'adapters').glob('**/yfinance_adapter.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        yf_hits += len(PATTERNS['yfinance'].findall(txt))

    # efinance API calls discovered
    ef_calls = set()
    for path in (SRC / 'adapters').glob('**/efinance_adapter.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['efinance'].finditer(txt):
            ef_calls.add('stock.' + m.group(1))

    # ibkr method usage discovered
    ib_hits = set()
    for path in (SRC / 'adapters').glob('**/ibkr_adapter.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in PATTERNS['ibkr'].finditer(txt):
            ib_hits.add(m.group(1))

    # Assertions: not empty where we expect usage
    assert ak_all, "No AkShare APIs found in adapters/registry; scan likely broken"
    assert yf_hits >= 1, "No yfinance API usage detected"
    assert ib_hits, "No IBKR API usage detected"

    # For AkShare, ensure every adapter-used API is present in registry, and vice versa
    only_in_adapters = sorted(ak_apis_from_adapters - ak_apis_from_registry)
    only_in_registry = sorted(ak_apis_from_registry - ak_apis_from_adapters)

    if only_in_adapters:
        missing.append("akshare in registry: " + ", ".join(only_in_adapters))
    if only_in_registry:
        missing.append("akshare in adapters: " + ", ".join(only_in_registry))

    if missing:
        pytest.fail("Adapter API coverage mismatch: " + " | ".join(missing))