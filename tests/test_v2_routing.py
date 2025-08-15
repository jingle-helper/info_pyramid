import os
import types
import pandas as pd
import pytest

# Tests for v2 multi-provider routing using registry_v2 + resolver + dispatcher_v2.

@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    for k in list(os.environ.keys()):
        if k.startswith('AKU_PROVIDER_PRIORITY') or k.startswith('AKU_VENDOR_PRIORITY'):
            monkeypatch.delenv(k, raising=False)
    yield


def _make_df(tag: str) -> pd.DataFrame:
    return pd.DataFrame([{"_tag": tag}])


def test_fetch_v2_adapter_order(monkeypatch):
    # Lazy import module paths
    import importlib
    registry_v2 = importlib.import_module('ak_unified.registry_v2')
    resolver = importlib.import_module('ak_unified.resolver')
    dispatcher_v2 = importlib.import_module('ak_unified.dispatcher_v2')

    # Register a dataset with three providers
    dsid = 'securities.equity.cn.ohlcva_daily'
    providers = [
        registry_v2.ProviderSpec(adapter='akshare', api_id='stock_zh_a_hist', vendor='eastmoney'),
        registry_v2.ProviderSpec(adapter='efinance', api_id='stock.get_quote_history'),
        registry_v2.ProviderSpec(adapter='yfinance', api_id='download'),
    ]
    registry_v2.REGISTRY_V2[dsid] = registry_v2.DatasetV2(
        dataset_id=dsid,
        category='securities',
        domain='securities.equity.cn',
        providers=providers,
    )

    # Monkeypatch dispatcher call to simulate failures/success by adapter
    calls = []

    def fake_dispatch(provider, dataset_id, params):
        calls.append((provider.adapter, provider.api_id))
        if provider.adapter == 'efinance':
            raise RuntimeError('efinance fail')
        return 'ok', _make_df(f"{provider.adapter}:{provider.api_id}")

    monkeypatch.setattr(dispatcher_v2, '_dispatch_call', fake_dispatch)

    # No explicit priority => use env global priority
    os.environ['AKU_PROVIDER_PRIORITY'] = 'efinance,akshare,yfinance'

    fn_used, df = dispatcher_v2.fetch_data_v2(dsid, params={'symbol': '600000.SH'})
    assert isinstance(df, pd.DataFrame)
    # efinance fails, fallback to akshare
    assert df['_tag'].iloc[0] == 'akshare:stock_zh_a_hist'
    # Call order: efinance -> akshare
    assert calls[:2] == [('efinance', 'stock.get_quote_history'), ('akshare', 'stock_zh_a_hist')]


def test_fetch_v2_adapter_query_overrides_priority(monkeypatch):
    import importlib
    registry_v2 = importlib.import_module('ak_unified.registry_v2')
    dispatcher_v2 = importlib.import_module('ak_unified.dispatcher_v2')

    dsid = 'securities.equity.cn.ohlcv_daily'
    registry_v2.REGISTRY_V2[dsid] = registry_v2.DatasetV2(
        dataset_id=dsid,
        category='securities',
        domain='securities.equity.cn',
        providers=[
            registry_v2.ProviderSpec(adapter='akshare', api_id='stock_zh_a_hist'),
            registry_v2.ProviderSpec(adapter='yfinance', api_id='download'),
        ],
    )

    calls = []

    def fake_dispatch(provider, dataset_id, params):
        calls.append(provider.adapter)
        return 'ok', _make_df(provider.adapter)

    monkeypatch.setattr(dispatcher_v2, '_dispatch_call', fake_dispatch)

    # Even if global priority is akshare first, query-adapter should override
    os.environ['AKU_PROVIDER_PRIORITY'] = 'akshare,yfinance'

    # adapter override: yfinance first
    fn_used, df = dispatcher_v2.fetch_data_v2(dsid, params={'symbol': 'AAPL'}, adapter=['yfinance', 'akshare'])
    assert df['_tag'].iloc[0] == 'yfinance'
    assert calls[0] == 'yfinance'


def test_fetch_v2_vendor_priority(monkeypatch):
    import importlib
    registry_v2 = importlib.import_module('ak_unified.registry_v2')
    dispatcher_v2 = importlib.import_module('ak_unified.dispatcher_v2')

    dsid = 'securities.equity.cn.quote'
    registry_v2.REGISTRY_V2[dsid] = registry_v2.DatasetV2(
        dataset_id=dsid,
        category='securities',
        domain='securities.equity.cn',
        providers=[
            registry_v2.ProviderSpec(adapter='akshare', api_id='stock_zh_a_spot_em', vendor='eastmoney'),
            registry_v2.ProviderSpec(adapter='akshare', api_id='stock_zh_a_spot_sina', vendor='sina'),
        ],
    )

    calls = []

    def fake_dispatch(provider, dataset_id, params):
        calls.append(provider.vendor)
        return 'ok', _make_df(provider.vendor or 'none')

    monkeypatch.setattr(dispatcher_v2, '_dispatch_call', fake_dispatch)

    # Vendor priority: prefer sina over eastmoney for this dataset
    os.environ['AKU_VENDOR_PRIORITY__securities.equity.cn.quote__akshare'] = 'sina,eastmoney'

    fn_used, df = dispatcher_v2.fetch_data_v2(dsid, params={})
    assert df['_tag'].iloc[0] == 'sina'
    assert calls[0] == 'sina'