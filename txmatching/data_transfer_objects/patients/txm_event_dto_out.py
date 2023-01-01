from dataclasses import dataclass
from typing import List, Optional

from txmatching.utils.enums import StrictnessType, TxmEventState


@dataclass
class TxmEventDTOOut:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name
    name: str
    default_config_id: Optional[int]
    state: TxmEventState
    strictness_type: Optional[StrictnessType] = StrictnessType.STRICT


@dataclass
class TxmEventsDTOOut:
    events: List[TxmEventDTOOut]


@dataclass
class TxmEventCopyPatientsDTOOut:
    new_donor_ids: List[int]
