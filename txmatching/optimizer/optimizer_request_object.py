from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Pair:
    donor_id: int
    recipient_id: Optional[int] = None


@dataclass
class Limitations:
    max_cycle_length: Optional[int] = None
    max_chain_length: Optional[int] = None
    custom_algorithm_settings: Optional[Dict[str, int]] = None


@dataclass
class OptimizerConfiguration:
    limitations: Optional[Limitations] = None
    scoring: Optional[List[List[Dict[str, int]]]] = None


@dataclass
class CompatibilityGraphRow:
    # todo add rows according to new keywords
    donor_id: int
    recipient_id: int
    hla_compatibility_score: Optional[int] = None
    donor_age_difference: Optional[int] = None


@dataclass
class OptimizerRequest:
    compatibility_graph: List[CompatibilityGraphRow]
    pairs: List[Pair]
    configuration: OptimizerConfiguration
