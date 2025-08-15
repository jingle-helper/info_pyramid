from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

ParamTransform = Callable[[Dict[str, any]], Dict[str, any]]
PostProcess = Callable[["pd.DataFrame", Dict[str, any]], "pd.DataFrame"]


@dataclass
class ProviderSpec:
    adapter: str
    api_id: str
    vendor: Optional[str] = None
    priority: Optional[int] = None
    param_transform: Optional[ParamTransform] = None
    field_mapping: Optional[Dict[str, str]] = None
    notes: Optional[str] = None


@dataclass
class DatasetV2:
    dataset_id: str
    category: str
    domain: str
    providers: List[ProviderSpec]
    postprocess: Optional[PostProcess] = None


REGISTRY_V2: Dict[str, DatasetV2] = {}