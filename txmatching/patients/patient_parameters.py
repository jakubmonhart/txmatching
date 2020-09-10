from dataclasses import dataclass, field
from typing import List

from txmatching.utils.country import Country
from txmatching.utils.hla_system.hla_table import hla_split_to_broad, is_valid_broad_code


@dataclass
class HLAAntigens:
    codes: List[str] = field(default_factory=list)


@dataclass
class HLAAntibodies:
    codes: List[str] = field(default_factory=list)


@dataclass
class PatientParameters:
    blood_group: str
    country_code: Country
    hla_antigens: HLAAntigens = HLAAntigens()
    hla_antibodies: HLAAntibodies = HLAAntibodies()

    @property
    def hla_antigens_broad_resolution(self) -> List[str]:
        broad_res_codes = [hla_split_to_broad(antigen) for antigen in self.hla_antigens.codes]
        broad_res_codes = [code for code in broad_res_codes if is_valid_broad_code(code)]
        return broad_res_codes

    @property
    def hla_antibodies_broad_resolution(self) -> List[str]:
        broad_res_codes = [hla_split_to_broad(antibody) for antibody in self.hla_antibodies.codes]
        broad_res_codes = [code for code in broad_res_codes if is_valid_broad_code(code)]
        return broad_res_codes
