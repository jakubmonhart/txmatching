from dataclasses import dataclass
from typing import Callable, List, Set

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_functions import (
    analyze_if_high_res_antibodies_are_type_a, is_all_antibodies_in_high_res)
from txmatching.patients.hla_model import (HLAAntibodies, HLAAntibody,
                                           HLAPerGroup, HLAType, HLATyping)
from txmatching.utils.enums import (AntibodyMatchTypes, HLACrossmatchLevel,
                                    HLAGroup, HLAAntibodyType)
from txmatching.utils.hla_system.rel_dna_ser_exceptions import \
    MULTIPLE_SERO_CODES_LIST


@dataclass(eq=True, frozen=True)
class AntibodyMatch:
    hla_antibody: HLAAntibody
    match_type: AntibodyMatchTypes


@dataclass
class AntibodyMatchForHLAGroup:
    hla_group: HLAGroup
    antibody_matches: List[AntibodyMatch]


def get_crossmatched_antibodies(donor_hla_typing: HLATyping,
                                recipient_antibodies: HLAAntibodies,
                                use_high_resolution: bool):
    if is_recipient_type_a(recipient_antibodies):
        antibody_matches_for_groups = do_crossmatch_in_type_a(donor_hla_typing,
                                                              recipient_antibodies,
                                                              use_high_resolution)
    else:
        antibody_matches_for_groups = do_crossmatch_in_type_b(donor_hla_typing,
                                                              recipient_antibodies,
                                                              use_high_resolution)

    # Sort antibodies
    for antibodies_per_hla_group in antibody_matches_for_groups:
        antibodies_per_hla_group.antibody_matches = sorted(
            antibodies_per_hla_group.antibody_matches,
            key=lambda hla_group: (
                hla_group.hla_antibody.raw_code,
            ))

    return antibody_matches_for_groups


def is_positive_hla_crossmatch(donor_hla_typing: HLATyping,
                               recipient_antibodies: HLAAntibodies,
                               use_high_resolution: bool,
                               crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE,
                               crossmatch_logic: Callable = get_crossmatched_antibodies) -> bool:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    e.g. A23 -> A23 True
         A9 -> A9  True
         A23 -> A9 True
         A23 -> A24 False if use_high_resolution else True
         A9 -> A23 True
         A9 broad <=> A23, A24 split
    :param donor_hla_typing: donor hla_typing to crossmatch
    :param recipient_antibodies: recipient antibodies to crossmatch
    :param use_high_resolution: setting whether to high res resolution for crossmatch determination
    :param crossmatch_level:
    :param crossmatch_logic:
    :return:
    """
    common_codes = {antibody_match.hla_antibody for antibody_match_group in
                    crossmatch_logic(donor_hla_typing, recipient_antibodies, use_high_resolution)
                    for antibody_match in antibody_match_group.antibody_matches
                    if antibody_match.match_type.is_positive_for_level(crossmatch_level)}
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


# pylint: disable=too-many-branches
def do_crossmatch_in_type_a(donor_hla_typing: HLATyping,
                            recipient_antibodies: HLAAntibodies,
                            use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        for antibody in antibodies_per_group.hla_antibody_list:
            # TODO improve the code around multiple sero codes https://github.com/mild-blue/txmatching/issues/1036
            if antibody.code.high_res is None and antibody.code.split not in MULTIPLE_SERO_CODES_LIST:
                raise InvalidArgumentException(f'Crossmatch type a cannot be computed if some of'
                                               f'patient antibodies is not in high res. Antibody: '
                                               f'{antibody} does not have high res')
        positive_matches = set()
        antibodies = antibodies_per_group.hla_antibody_list

        _add_undecidable_crossmatch_type(_get_antibodies_over_cutoff(antibodies), hla_per_group, positive_matches)

        for hla_type in hla_per_group.hla_types:
            if use_high_resolution and hla_type.code.high_res is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.high_res == antibody.code.high_res]

                # HIGH_RES_1
                if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                                   AntibodyMatchTypes.HIGH_RES,
                                                   positive_matches):
                    continue

                if not _recipient_was_tested_for_donor_antigen(antibodies, hla_type.code):
                    tested_antibodies_that_match = [antibody for antibody in antibodies
                                                    if hla_type.code.split == antibody.code.split
                                                    if hla_type.code.split is not None]
                    positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                    # HIGH_RES_2
                    if _add_all_tested_positive_antibodies(tested_antibodies_that_match,
                                                           positive_tested_antibodies,
                                                           AntibodyMatchTypes.HIGH_RES,
                                                           positive_matches):
                        continue

                    # HIGH_RES_WITH_SPLIT_2
                    if _add_positive_tested_antibodies(positive_tested_antibodies,
                                                       AntibodyMatchTypes.HIGH_RES_WITH_SPLIT,
                                                       positive_matches):
                        continue

            if hla_type.code.split is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split
                                                if hla_type.code.split is not None]
                positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                # HIGH_RES_3
                if hla_type.code.high_res is None:
                    if _add_all_tested_positive_antibodies(tested_antibodies_that_match,
                                                           positive_tested_antibodies,
                                                           AntibodyMatchTypes.HIGH_RES,
                                                           positive_matches):
                        continue

                # HIGH_RES_WITH_SPLIT_1
                if _add_positive_tested_antibodies(positive_tested_antibodies,
                                                   AntibodyMatchTypes.HIGH_RES_WITH_SPLIT,
                                                   positive_matches):
                    continue

                # SPLIT_1
                if hla_type.code.high_res is None:
                    if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                                       AntibodyMatchTypes.SPLIT,
                                                       positive_matches):
                        continue

            if hla_type.code.broad is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.broad == antibody.code.broad]
                positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

                # HIGH_RES_3
                if hla_type.code.high_res is None:
                    if _add_all_tested_positive_antibodies(tested_antibodies_that_match,
                                                           positive_tested_antibodies,
                                                           AntibodyMatchTypes.HIGH_RES,
                                                           positive_matches):
                        continue

                # HIGH_RES_WITH_BROAD_1
                if hla_type.code.high_res is None and hla_type.code.split is None:
                    if _add_positive_tested_antibodies(positive_tested_antibodies,
                                                       AntibodyMatchTypes.HIGH_RES_WITH_BROAD,
                                                       positive_matches):
                        continue

                # BROAD_1
                if hla_type.code.high_res is None and hla_type.code.split is None:
                    if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                                       AntibodyMatchTypes.BROAD,
                                                       positive_matches):
                        continue

        _add_theoretical_crossmatch_type(positive_matches)
        _add_none_crossmatch_type(_get_antibodies_over_cutoff(antibodies), positive_matches)

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, list(positive_matches)))

    return antibody_matches_for_groups


def do_crossmatch_in_type_b(donor_hla_typing: HLATyping,
                            recipient_antibodies: HLAAntibodies,
                            use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        positive_matches = set()
        antibodies = antibodies_per_group.hla_antibody_list

        _add_undecidable_crossmatch_type(_get_antibodies_over_cutoff(antibodies), hla_per_group, positive_matches)

        for hla_type in hla_per_group.hla_types:
            if use_high_resolution and hla_type.code.high_res is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.high_res == antibody.code.high_res]
                # HIGH_RES_1
                if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                                   AntibodyMatchTypes.HIGH_RES,
                                                   positive_matches):
                    continue

            if hla_type.code.split is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split
                                                if hla_type.code.split is not None]
                if _add_split_crossmatch_type(hla_type, tested_antibodies_that_match, positive_matches):
                    continue

            if hla_type.code.broad is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.broad == antibody.code.broad]
                if _add_broad_crossmatch_type(hla_type, tested_antibodies_that_match, positive_matches):
                    continue

        _add_theoretical_crossmatch_type(positive_matches)
        _add_none_crossmatch_type(antibodies, positive_matches)

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, list(positive_matches)))

    return antibody_matches_for_groups


def is_recipient_type_a(recipient_antibodies: HLAAntibodies) -> bool:
    hla_antibodies_from_all_groups = []
    for antibodies_per_group in recipient_antibodies.hla_antibodies_per_groups:
        hla_antibodies_from_all_groups += antibodies_per_group.hla_antibody_list

    if not is_all_antibodies_in_high_res(hla_antibodies_from_all_groups):
        return False

    return analyze_if_high_res_antibodies_are_type_a(
        hla_antibodies_from_all_groups).is_type_a_compliant


def _get_antibodies_over_cutoff(antibodies: List[HLAAntibody]) -> List[HLAAntibody]:
    return [antibody for antibody in antibodies if antibody.mfi >= antibody.cutoff]


def _recipient_was_tested_for_donor_antigen(antibodies: List[HLAAntibody], antigen: HLACode) -> bool:
    return antigen in [antibody.code for antibody in antibodies]


def _add_all_tested_positive_antibodies(tested_antibodies_that_match: List[HLAAntibody],
                                        positive_tested_antibodies: List[HLAAntibody],
                                        match_type: AntibodyMatchTypes,
                                        positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if crossmatch has happened."""

    if len(positive_tested_antibodies) > 0:
        if len(tested_antibodies_that_match) == len(positive_tested_antibodies):
            for antibody in tested_antibodies_that_match:
                positive_matches.add(AntibodyMatch(antibody, match_type))
            return True
    return False


def _add_positive_tested_antibodies(tested_antibodies_that_match: List[HLAAntibody],
                                    match_type: AntibodyMatchTypes,
                                    positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if crossmatch has happened."""

    if len(tested_antibodies_that_match) > 0:
        for antibody in _get_antibodies_over_cutoff(tested_antibodies_that_match):
            positive_matches.add(AntibodyMatch(antibody, match_type))
        return True
    return False


def _add_split_crossmatch_type(hla_type: HLAType,
                               tested_antibodies_that_match: List[HLAAntibody],
                               positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if split crossmatch has happened."""

    # SPLIT_1
    if hla_type.code.high_res is None:
        if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                           AntibodyMatchTypes.SPLIT,
                                           positive_matches):
            return True

    tested_antibodies_that_match = [antibody for antibody in tested_antibodies_that_match
                                    if antibody.code.high_res is None]
    # SPLIT_2
    if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                       AntibodyMatchTypes.SPLIT,
                                       positive_matches):
        return True

    return False


def _add_broad_crossmatch_type(hla_type: HLAType,
                               tested_antibodies_that_match: List[HLAAntibody],
                               positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if broad crossmatching has happened."""

    # BROAD_1
    if hla_type.code.high_res is None and hla_type.code.split is None:
        if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                           AntibodyMatchTypes.BROAD,
                                           positive_matches):
            return True

    tested_antibodies_that_match = [antibody for antibody in tested_antibodies_that_match
                                    if antibody.code.high_res is None and antibody.code.split is None]
    # BROAD_2
    if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                       AntibodyMatchTypes.BROAD,
                                       positive_matches):
        return True

    return False


def _add_undecidable_crossmatch_type(antibodies: List[HLAAntibody],
                                     hla_per_group: HLAPerGroup,
                                     positive_matches: Set[AntibodyMatch]):
    if len(hla_per_group.hla_types) == 0:
        for antibody in antibodies:
            positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE))


def _add_theoretical_crossmatch_type(positive_matches: Set[AntibodyMatch]):
    for match in positive_matches:
        if match.hla_antibody.type == HLAAntibodyType.THEORETICAL and match.match_type != AntibodyMatchTypes.UNDECIDABLE:
            positive_matches.remove(match)
            positive_matches.add(AntibodyMatch(match.hla_antibody, AntibodyMatchTypes.THEORETICAL))


def _add_none_crossmatch_type(antibodies: List[HLAAntibody],
                              positive_matches: Set[AntibodyMatch]):
    antibodies_positive_matches = {match.hla_antibody for match in positive_matches}
    for antibody in _get_antibodies_over_cutoff(antibodies):
        if antibody not in antibodies_positive_matches:
            positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))
