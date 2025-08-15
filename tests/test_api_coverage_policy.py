import os
import re
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "ak_unified"

ADAPTER_PATTERNS = {
    'akshare': re.compile(r"\bcall_akshare\(\s*\[\s*'(?P<api>[a-zA-Z0-9_]+)'"),
    'yfinance': re.compile(r"yf\.download\(|yf\.Ticker\("),
    'efinance': re.compile(r"ef\.stock\.[a-zA-Z0-9_]+\("),
    'ibkr': re.compile(r"req(MktData|HistoricalData|FundamentalData)Async|req(MktData|HistoricalData|FundamentalData)\("),
}

COVERAGE_FILES = {
    'akshare': ROOT / 'tests' / 'test_akshare_adapter_apis.py',
}

@pytest.mark.unit
def test_adapters_api_coverage_enforced():
    missing = []
    # Collect declared AkShare APIs found in adapters
    ak_apis = set()
    for path in (SRC / 'adapters').glob('**/*.py'):
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for m in ADAPTER_PATTERNS['akshare'].finditer(txt):
            ak_apis.add(m.group('api'))
    # Read coverage list
    covered_apis = set()
    cov_path = COVERAGE_FILES['akshare']
    if cov_path.exists():
        covered_apis.update(re.findall(r"'([a-zA-Z0-9_]+)'", cov_path.read_text(encoding='utf-8', errors='ignore')))
    # Compute missing
    for api in sorted(ak_apis):
        if api not in covered_apis:
            missing.append(f"akshare:{api}")
    if missing:
        pytest.fail("Missing adapter API coverage entries: " + ", ".join(missing))