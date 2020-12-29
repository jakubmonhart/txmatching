from dataclasses import dataclass
from typing import List

import logging

from txmatching.patients.patient_parameters import HLATyping
from txmatching.utils.enums import (HLA_GROUPS_GENE,
                                    HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS,
                                    MATCH_TYPE_BONUS, HLAGroup, MatchTypes)
# Traditionally one can calculate index of incompatibility (IK) - the higher IK the higher incompatibility.
# You calculate it by calculating the number of differences in A, B, DR alleles and look up the corresponding
# column in the incompatibility index table.
# For our purposes, we will use the index of compatibility, which is the inverse of index of incompatibility
# -- see function compatibility_index -- and is calculated as the number of matches in A, B, DR alleles.
# For each matching allele a certain bonus is added to compatibility index depending on the allele type.
from txmatching.utils.hla_system.hla_transformations import (broad_to_split,
                                                             get_broad_codes)

logger = logging.getLogger(__name__)


class InvalidNumberOfAllelesError(Exception):
    pass


@dataclass
class HLAMatch:
    hla_code: str
    match_type: MatchTypes


@dataclass
class DetailedCompatibilityIndexForHLAGroup:
    hla_group: HLAGroup
    donor_matches: List[HLAMatch]
    recipient_matches: List[HLAMatch]
    group_compatibility_index: float


def compatibility_index(donor_hla_typing: HLATyping,
                        recipient_hla_typing: HLATyping) -> float:
    return sum([ci_index_for_group.group_compatibility_index for ci_index_for_group
                in get_detailed_compatibility_index(donor_hla_typing, recipient_hla_typing)
                ])


def get_detailed_compatibility_index(donor_hla_typing: HLATyping,
                                     recipient_hla_typing: HLATyping
                                     ) -> List[DetailedCompatibilityIndexForHLAGroup]:
    """
    The "compatibility index" is terminus technicus defined by immunologist:
    we calculate number of matches per Compatibility HLA indices and add bonus according
     to number of matches and the HLA code.
    This function thus should not be modified unless after consulting with immunologists.
    """
    hla_compatibility_index_detailed = []
    for hla_group in HLA_GROUPS_GENE:
        donor_split_codes = _hla_codes_for_gene_hla_group(donor_hla_typing, hla_group)
        recipient_split_codes = _hla_codes_for_gene_hla_group(recipient_hla_typing, hla_group)

        hla_compatibility_index_detailed.append(_get_ci_for_recipient_donor_split_codes(
            donor_split_codes=donor_split_codes,
            recipient_split_codes=recipient_split_codes,
            hla_group=hla_group
        )
        )
    hla_group = HLAGroup.Other
    donor_split_codes = _hla_codes_for_hla_group(donor_hla_typing, hla_group)
    recipient_split_codes = _hla_codes_for_hla_group(recipient_hla_typing, hla_group)
    hla_compatibility_index_detailed.append(_get_ci_for_recipient_donor_split_codes(
        donor_split_codes=donor_split_codes,
        recipient_split_codes=recipient_split_codes,
        hla_group=hla_group
    ))

    return hla_compatibility_index_detailed


# pylint: disable=too-many-arguments
# I think it is reasonable to have multiple arguments here
def _match_through_split_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               donor_split_codes: List[str],
                               recipient_split_codes: List[str],
                               hla_group: HLAGroup):
    for split_code in donor_split_codes.copy():
        if split_code in recipient_split_codes:
            donor_split_codes.remove(split_code)
            recipient_split_codes.remove(split_code)

            donor_matches.append(HLAMatch(split_code, MatchTypes.SPLIT))
            recipient_matches.append(HLAMatch(split_code, MatchTypes.SPLIT))
            current_compatibility_index += MATCH_TYPE_BONUS[MatchTypes.SPLIT] * HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS[
                hla_group]
    return current_compatibility_index


def _match_through_broad_codes(current_compatibility_index: float,
                               donor_matches: List[HLAMatch],
                               recipient_matches: List[HLAMatch],
                               donor_split_codes: List[str],
                               recipient_split_codes: List[str],
                               hla_group: HLAGroup):
    for split_code, broad_code in zip(donor_split_codes.copy(), get_broad_codes(donor_split_codes)):
        if broad_code in get_broad_codes(recipient_split_codes):
            if broad_code in recipient_split_codes:
                recipient_match_code = broad_code
            else:
                split_codes_for_broad = set(broad_to_split(broad_code))
                split_codes_to_remove = split_codes_for_broad.intersection(set(recipient_split_codes))
                recipient_match_code = split_codes_to_remove.pop()

            recipient_split_codes.remove(recipient_match_code)
            donor_split_codes.remove(split_code)
            donor_matches.append(HLAMatch(split_code, MatchTypes.BROAD))
            recipient_matches.append(HLAMatch(recipient_match_code, MatchTypes.BROAD))
            current_compatibility_index += MATCH_TYPE_BONUS[MatchTypes.BROAD] * HLA_TYPING_BONUS_PER_GENE_CODE_GROUPS[
                hla_group]
    return current_compatibility_index


# pylint: enable=too-many-arguments


def _get_ci_for_recipient_donor_split_codes(
        donor_split_codes: List[str],
        recipient_split_codes: List[str],
        hla_group: HLAGroup) -> DetailedCompatibilityIndexForHLAGroup:
    donor_matches = []
    recipient_matches = []

    group_compatibility_index = _match_through_split_codes(0.0,
                                                           donor_matches,
                                                           recipient_matches,
                                                           donor_split_codes,
                                                           recipient_split_codes,
                                                           hla_group)
    group_compatibility_index = _match_through_broad_codes(group_compatibility_index,
                                                           donor_matches,
                                                           recipient_matches,
                                                           donor_split_codes,
                                                           recipient_split_codes,
                                                           hla_group)

    for left_recipient_code in recipient_split_codes:
        recipient_matches.append(HLAMatch(left_recipient_code, MatchTypes.NONE))
    for left_donor_code in donor_split_codes:
        donor_matches.append(HLAMatch(left_donor_code, MatchTypes.NONE))

    return DetailedCompatibilityIndexForHLAGroup(
        hla_group=hla_group,
        donor_matches=donor_matches,
        recipient_matches=recipient_matches,
        group_compatibility_index=group_compatibility_index
    )


def _hla_codes_for_gene_hla_group(donor_hla_typing: HLATyping, hla_group: HLAGroup) -> List[str]:
    hla_codes = _hla_codes_for_hla_group(donor_hla_typing, hla_group)

    if len(hla_codes) not in {1, 2}:
        logger.error(
            f'Invalid list of alleles for gene {hla_group.name} - there have to be 1 or 2 per gene.'
            f'\nList of patient_alleles: {donor_hla_typing.codes_per_group}')
        return hla_codes
    if len(hla_codes) == 1:
        return hla_codes + hla_codes
    return hla_codes


def _hla_codes_for_hla_group(donor_hla_typing: HLATyping, hla_group: HLAGroup) -> List[str]:
    return next(codes_per_group.hla_codes for codes_per_group in donor_hla_typing.codes_per_group if
                codes_per_group.hla_group == hla_group).copy()
