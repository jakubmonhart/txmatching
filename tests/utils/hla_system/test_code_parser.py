import unittest

import pandas as pd

from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.hla_system.hla_transformations import (
    HlaCodeProcessingResultDetail, parse_hla_raw_code,
    parse_hla_raw_code_with_details, preprocess_hla_code_in)
from txmatching.utils.hla_system.rel_dna_ser_parsing import parse_rel_dna_ser

codes = {
    'A1': ('A1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A32': ('A32', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B7': ('B7', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'B51': ('B51', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR11': ('DR11', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DR15': ('DR15', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*23': ('A23', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*01:52:01N': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'A*02:03': ('A203', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'A*11:01:35': ('A11', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'C*01:02': ('CW1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DPA1*01:07': ('DPA1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DRB4*01:01': ('DR53', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'DQB1*02:01:01:01': ('DQ2', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED),
    'NONEXISTENT': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'NONEXISTENT*11': (None, HlaCodeProcessingResultDetail.UNPARSABLE_HLA_CODE),
    'A*68:06': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'B*46:10': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'A*02:719': (None, HlaCodeProcessingResultDetail.UNKNOWN_TRANSFORMATION_TO_SPLIT),
    'DQA1*01:03': ('DQA1', HlaCodeProcessingResultDetail.SUCCESSFULLY_PARSED)
}


class TestCodeParser(unittest.TestCase):
    def test_parsing(self):
        for code, (expected_result, expected_result_detail) in codes.items():
            result = parse_hla_raw_code_with_details(code)
            parse_hla_raw_code(code)  # here just to test logging
            self.assertTupleEqual((expected_result_detail, expected_result),
                                  (result.result_detail, result.maybe_hla_code),
                                  f'{code} was processed to {result.maybe_hla_code} '
                                  f'with result {result.result_detail} expected was: '
                                  f'{expected_result} with result {expected_result_detail}')

    def test_parse_hla_ser(self):
        parsing_result = parse_rel_dna_ser(get_absolute_path('tests/utils/hla_system/rel_dna_ser_test.txt'))

        self.assertEqual('A1', parsing_result.loc['A*01:01:01:01'].split)
        self.assertTrue(pd.isna(parsing_result.loc['A*05:01:01:02N'].split))
        self.assertTrue(pd.isna(parsing_result.loc['A*06:01:01:02'].split))
        self.assertEqual('DR1', parsing_result.loc['DRB1*03:01:01:02'].split)
        self.assertEqual('DP2', parsing_result.loc['DPB1*02:01:06'].split)
        self.assertEqual('CW14', parsing_result.loc['C*14:02:01:01'].split)
        self.assertEqual('CW8', parsing_result.loc['C*09'].split)

    def test_preprocessing(self):
        self.assertSetEqual({'DPA1*01:03', 'DPB1*04:02'}, set(preprocess_hla_code_in('DP4 [01:03, 04:02]')))
        self.assertSetEqual({'DQA1*01:03', 'DQB1*06:03'}, set(preprocess_hla_code_in('DQ[01:03,      06:03]')))
