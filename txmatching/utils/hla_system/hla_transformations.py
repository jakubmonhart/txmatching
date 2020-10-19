import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set, Union

import numpy as np

from txmatching.utils.hla_system.hla_table import (ALL_SPLIT_BROAD_CODES,
                                                   COMPATIBILITY_BROAD_CODES,
                                                   SPLIT_TO_BROAD)
from txmatching.utils.hla_system.rel_dna_ser_exceptions import (
    PARSE_HLA_CODE_EXCEPTIONS,
    PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES)
from txmatching.utils.hla_system.rel_dna_ser_parsing import HIGH_RES_TO_SPLIT

logger = logging.getLogger(__name__)

MAX_MIN_RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI = 2

HIGH_RES_REGEX = re.compile(r'^[A-Z]+\d?\*\d{2,4}(:\d{2,3})*[A-Z]?$')
SPLIT_RES_REGEX = re.compile(r'^[A-Z]+\d+$')
HIGH_RES_WITH_SUBUNITS_REGEX = re.compile(r'([A-Za-z]{1,3})\d?\[(\d{2}:\d{2}),(\d{2}:\d{2})]')

CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX = re.compile(r'C(\d+)')
DQ_DP_B_SEROLOGICAL_CODE_WITH_B_REGEX = re.compile(r'(D[QP])B(\d+)')


def broad_to_split(hla_code: str) -> List[str]:
    if hla_code not in ALL_SPLIT_BROAD_CODES:
        logger.warning(f'Unexpected hla_code: {hla_code}')
        return [hla_code]
    splits = [split for split, broad in SPLIT_TO_BROAD.items() if broad == hla_code]
    return splits if splits else [hla_code]


def split_to_broad(hla_code: str) -> str:
    return SPLIT_TO_BROAD.get(hla_code, hla_code)


class HlaCodeProcessingResultDetail(str, Enum):
    # still returning value
    SUCCESSFULLY_PARSED = 'Code successfully parsed without anything unexpected'
    UNEXPECTED_SPLIT_RES_CODE = 'Unknown HLA code, seems to be in split resolution'

    # returning no value
    MULTIPLE_SPLITS_FOUND = 'Multiple splits were found, unable to choose the right one.' \
                            ' Immunologists shall be contacted'
    UNKNOWN_TRANSFORMATION_TO_SPLIT = 'Unable to transform high resolution HLA code. Its transformation to split' \
                                      ' code is unknown. Immunologists shall be contacted'
    UNPARSABLE_HLA_CODE = 'Completely Unexpected HLA code'


@dataclass
class HlaCodeProcessingResult:
    maybe_hla_code: Optional[str]
    result_detail: HlaCodeProcessingResultDetail


def _get_possible_splits_for_high_res_code(high_res_code: str) -> Set[str]:
    return {split for high_res, split in HIGH_RES_TO_SPLIT.items() if
            high_res.startswith(f'{high_res_code}:')}


def _high_res_to_split(high_res_code: str) -> Union[str, HlaCodeProcessingResultDetail]:
    """
    Transforms high resolution code to serological (split) code. In the case no code is found
    HlaCodeProcessingResultDetail with details is returned.
    :param high_res_code: High res code to transform.
    :return: Either found split code or HlaCodeProcessingResultDetail in case no split code is found.
    """
    maybe_split_hla_code = HIGH_RES_TO_SPLIT.get(high_res_code, _get_possible_splits_for_high_res_code(high_res_code))
    if maybe_split_hla_code is None:
        # Code found in the HIGH_RES_TO_SPLIT but none was returned as the transformation is unknown.
        return HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT
    elif isinstance(maybe_split_hla_code, str):
        return maybe_split_hla_code
    else:
        assert isinstance(maybe_split_hla_code, set), 'Unexpected type'
        if len(maybe_split_hla_code) == 0:
            # No code found in HIGH_RES_TO_SPLIT so it is code in high_res_code that does not exist in our
            # transformation table at all.
            return HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE
        possible_split_resolutions = maybe_split_hla_code.difference({None})
        if len(possible_split_resolutions) == 0:
            return HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT
        else:
            found_splits = set(possible_split_resolutions)
            if len(found_splits) == 1:
                return possible_split_resolutions.pop()
            else:
                # in case there are multiple possibilities we do not know which to choose and return None.
                logger.warning(f'Multiple possible split resolutions for high res code {high_res_code}'
                               f' found: {possible_split_resolutions}')
                return HlaCodeProcessingResultDetail.MULTIPLE_SPLITS_FOUND


def parse_hla_raw_code_with_details(hla_raw_code: str) -> HlaCodeProcessingResult:
    maybe_exception_hla_code = PARSE_HLA_CODE_EXCEPTIONS.get(hla_raw_code)
    if maybe_exception_hla_code:
        return HlaCodeProcessingResult(maybe_exception_hla_code, HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED)

    if re.match(HIGH_RES_REGEX, hla_raw_code):
        hla_code_or_error = _high_res_to_split(hla_raw_code)
    else:
        hla_code_or_error = hla_raw_code

    if isinstance(hla_code_or_error, str) and re.match(SPLIT_RES_REGEX, hla_code_or_error):
        c_match = re.match(CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX, hla_code_or_error)
        if c_match:
            hla_code_or_error = f'CW{int(c_match.group(1))}'

        dpqb_match = re.match(DQ_DP_B_SEROLOGICAL_CODE_WITH_B_REGEX, hla_code_or_error)
        if dpqb_match:
            hla_code_or_error = f'{dpqb_match.group(1)}{int(dpqb_match.group(2))}'

        if hla_code_or_error in ALL_SPLIT_BROAD_CODES:
            return HlaCodeProcessingResult(hla_code_or_error, HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED)
        # Some split hla codes are missing in our table, therefore we still return hla_codes if they match expected
        # format of split codes
        return HlaCodeProcessingResult(hla_code_or_error,
                                       HlaCodeProcessingResultDetail.UNEXPECTED_SPLIT_RES_CODE)
    elif isinstance(hla_code_or_error, HlaCodeProcessingResultDetail):
        return HlaCodeProcessingResult(None, hla_code_or_error)
    else:
        return HlaCodeProcessingResult(None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE)


def parse_hla_raw_code(hla_raw_code: str) -> Optional[str]:
    parsing_result = parse_hla_raw_code_with_details(hla_raw_code)
    if not parsing_result.maybe_hla_code:
        logger.error(f'HLA code processing of {hla_raw_code} was not successful: {parsing_result.result_detail}')
    elif parsing_result.result_detail != HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED:
        logger.warning(f'HLA code processing of {hla_raw_code} was successful with warning: '
                       f'{parsing_result.result_detail}')
    return parsing_result.maybe_hla_code


def preprocess_hla_code_in(hla_code_in: str) -> List[str]:
    hla_code_in = hla_code_in.replace(' ', '')
    hla_code_in = hla_code_in.upper()
    matched_multi_hla_codes = re.match(HIGH_RES_WITH_SUBUNITS_REGEX, hla_code_in)
    if matched_multi_hla_codes:
        return [f'{matched_multi_hla_codes.group(1)}A1*{matched_multi_hla_codes.group(2)}',
                f'{matched_multi_hla_codes.group(1)}B1*{matched_multi_hla_codes.group(3)}']
    # Handle this case better and elsewhere: https://trello.com/c/GG7zPLyj
    elif PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.get(hla_code_in):
        return PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.get(hla_code_in)
    else:
        return [hla_code_in]


def preprocess_hla_codes_in(hla_codes_in: List[str]) -> List[str]:
    return [parsed_code for hla_code_in in hla_codes_in for parsed_code in preprocess_hla_code_in(hla_code_in)]


def get_compatibility_broad_codes(hla_codes: List[str]) -> List[str]:
    return [split_to_broad(hla_code) for hla_code in hla_codes if split_to_broad(hla_code) in COMPATIBILITY_BROAD_CODES]


def get_mfi_from_multiple_hla_codes(mfis: List[int]):
    """
    Takes list of mfis of the same hla code and estimates the mfi for the code.
    It is based on discussions with immunologists. If variance is low, take average, if variance is high, something
    is wrong and ignore the hla_code (return 0 mfi)
    :param mfis:
    :return:
    """
    max_min_difference = (np.max(mfis) - np.min(mfis)) / np.min(mfis)
    if max_min_difference < MAX_MIN_RELATIVE_DIFFERENCE_THRESHOLD_FOR_SUSPICIOUS_MFI:
        return np.mean(mfis)
    return 0