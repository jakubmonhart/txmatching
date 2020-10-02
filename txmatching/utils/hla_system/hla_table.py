import re
from enum import Enum

from txmatching.utils.hla_system.rel_dna_ser_parsing import SPLIT_CODES

# TODO All the codes below are used purely to get set of broad codes its not user this set is complete. Get better
# maybe use http://hla.alleles.org/antigens/recognised_serology.html task: https://trello.com/c/JdmZ3iMY
HLA_A = {'A1', 'A2', 'A203', 'A210', 'A3', 'A11', 'A23', 'A24', 'A2403',
         'A25', 'A26', 'A29', 'A30', 'A31', 'A32', 'A33', 'A34', 'A36',
         'A43', 'A66', 'A68', 'A69', 'A74', 'A80'}

HLA_A_BROAD = {'A9', 'A10', 'A19', 'A28'}

HLA_B = {'B7', 'B703', 'B8', 'B13', 'B18', 'B27', 'B2708', 'B35', 'B37',
         'B38', 'B39', 'B3901', 'B3902', 'B4005', 'B41', 'B42', 'B44',
         'B45', 'B46', 'B47', 'B48', 'B49', 'B50', 'B51', 'B5102', 'B5103',
         'B52', 'B53', 'B54', 'B55', 'B56', 'B57', 'B58', 'B59', 'B60',
         'B61', 'B62', 'B63', 'B64', 'B65', 'B67', 'B71', 'B72', 'B73',
         'B75', 'B76', 'B77', 'B78', 'B81', 'B82'}

HLA_B_BROAD = {'B5', 'B12', 'B14', 'B15', 'B16', 'B17', 'B22', 'B40', 'B70'}

HLA_BW = {'BW4', 'BW6'}

HLA_CW = {'CW1', 'CW2', 'CW4', 'CW5', 'CW6', 'CW7', 'CW8', 'CW9', 'CW10'}

HLA_CW_BROAD = {'CW3'}

HLA_DR = {'DR1', 'DR103', 'DR4', 'DR7', 'DR8', 'DR9', 'DR10', 'DR11', 'DR12',
          'DR13', 'DR14', 'DR1403', 'DR1404', 'DR15', 'DR16', 'DR17', 'DR18'}

HLA_DR_BROAD = {'DR2', 'DR3', 'DR5', 'DR6'}

HLA_DRDR = {'DR51', 'DR52', 'DR53'}

HLA_DQ = {'DQ2', 'DQ4', 'DQ5', 'DQ6', 'DQ7', 'DQ8', 'DQ9'}

HLA_DQ_BROAD = {'DQ1', 'DQ3'}

SPLIT_TO_BROAD = {'A23': 'A9',
                  'A24': 'A9',
                  'A25': 'A10',
                  'A26': 'A10',
                  'A29': 'A19',
                  'A30': 'A19',
                  'A31': 'A19',
                  'A32': 'A19',
                  'A33': 'A19',
                  'A34': 'A10',
                  'A66': 'A10',
                  'A68': 'A28',
                  'A69': 'A28',
                  'A74': 'A19',
                  'B38': 'B16',
                  'B39': 'B16',
                  'B44': 'B12',
                  'B45': 'B12',
                  'B49': 'B21',
                  'B50': 'B21',
                  'B51': 'B5',
                  'B52': 'B5',
                  'B54': 'B22',
                  'B55': 'B22',
                  'B56': 'B22',
                  'B57': 'B17',
                  'B58': 'B17',
                  'B60': 'B40',
                  'B61': 'B40',
                  'B62': 'B15',
                  'B63': 'B15',
                  'B64': 'B14',
                  'B65': 'B14',
                  'B71': 'B70',
                  'B72': 'B70',
                  'B75': 'B15',
                  'B76': 'B15',
                  'B77': 'B15',
                  'CW9': 'CW3',
                  'CW10': 'CW3',
                  'DR11': 'DR5',
                  'DR12': 'DR5',
                  'DR13': 'DR6',
                  'DR14': 'DR6',
                  'DR15': 'DR2',
                  'DR16': 'DR2',
                  'DR17': 'DR3',
                  'DR18': 'DR3',
                  'DQ5': 'DQ1',
                  'DQ6': 'DQ1',
                  'DQ7': 'DQ3',
                  'DQ8': 'DQ3',
                  'DQ9': 'DQ3'
                  }
A_B_DR_HLA_CODE_REGEX = re.compile(r'^A|B|(DR(?!5(1|2|3)))')

PURELY_BROAD_CODES = set.union(HLA_A_BROAD, HLA_B_BROAD, HLA_CW_BROAD, HLA_DR_BROAD, HLA_DQ_BROAD)

BROAD_CODES = {SPLIT_TO_BROAD.get(hla_code, hla_code) for hla_code in SPLIT_CODES}

COMPATIBILITY_BROAD_CODES = {broad_code for broad_code in BROAD_CODES if re.match(A_B_DR_HLA_CODE_REGEX, broad_code)}

ALL_SPLIT_BROAD_CODES = SPLIT_CODES.union(BROAD_CODES)

