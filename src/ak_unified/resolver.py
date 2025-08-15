from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from .registry_v2 import REGISTRY_V2, DatasetV2, ProviderSpec


def _parse_csv(val: Optional[str]) -> List[str]:
    if not val:
        return []
    return [x.strip() for x in str(val).split(',') if x.strip()]


def _provider_priority_for_dataset(dataset_id: str) -> List[str]:
    # per-dataset override
    key = f"AKU_PROVIDER_PRIORITY__{dataset_id}"
    v = os.getenv(key)
    if v:
        return _parse_csv(v)
    # global default
    return _parse_csv(os.getenv('AKU_PROVIDER_PRIORITY'))


def _vendor_priority_for_dataset(dataset_id: str, adapter: str) -> List[str]:
    key_ds = f"AKU_VENDOR_PRIORITY__{dataset_id}__{adapter}"
    v = os.getenv(key_ds)
    if v:
        return _parse_csv(v)
    key_glob = f"AKU_VENDOR_PRIORITY__{adapter}"
    return _parse_csv(os.getenv(key_glob))


def _sort_providers(dataset: DatasetV2, adapters_pref: Optional[List[str]] = None) -> List[ProviderSpec]:
    providers = list(dataset.providers)
    # adapter order: query overrides env; then use dataset-specific or global
    if adapters_pref and len(adapters_pref) > 0:
        adapter_order = [a.lower() for a in adapters_pref]
    else:
        adapter_order = [a.lower() for a in _provider_priority_for_dataset(dataset.dataset_id)]
    if adapter_order:
        providers.sort(key=lambda p: (adapter_order.index(p.adapter.lower()) if p.adapter.lower() in adapter_order else 10**6,
                                      (p.priority if p.priority is not None else 10**6)))
    else:
        providers.sort(key=lambda p: (p.priority if p.priority is not None else 10**6))

    # within same adapter, use vendor priority if provided
    grouped: Dict[str, List[ProviderSpec]] = {}
    for p in providers:
        grouped.setdefault(p.adapter.lower(), []).append(p)

    out: List[ProviderSpec] = []
    for adapter, plist in grouped.items():
        vorder = _vendor_priority_for_dataset(dataset.dataset_id, adapter)
        if vorder:
            plist.sort(key=lambda x: (vorder.index((x.vendor or '').lower()) if (x.vendor or '').lower() in vorder else 10**6,
                                      (x.priority if x.priority is not None else 10**6)))
        out.extend(plist)
    # re-sort by adapter group according to adapter_order again
    if adapter_order:
        out.sort(key=lambda p: (adapter_order.index(p.adapter.lower()) if p.adapter.lower() in adapter_order else 10**6))
    return out


def resolve_providers(dataset_id: str, *, adapter: Optional[List[str]] = None) -> List[ProviderSpec]:
    dataset = REGISTRY_V2.get(dataset_id)
    if not dataset:
        raise KeyError(f"Dataset not registered in REGISTRY_V2: {dataset_id}")
    return _sort_providers(dataset, adapters_pref=adapter)