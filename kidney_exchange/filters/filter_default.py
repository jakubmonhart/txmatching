from typing import List

from kidney_exchange.filters.filter_base import FilterBase
from kidney_exchange.patients.patient import Patient
from kidney_exchange.solvers.matching.matching import Matching


class FilterDefault(FilterBase):
    def __init__(self, max_cycle_lenght: int = None,
                 max_sequence_lenght: int = None,
                 max_number_of_distinct_countries_in_round: int = None,
                 required_patients: List[Patient] = None):
        self._max_cycle_length = max_cycle_lenght
        self._max_sequence_length = max_sequence_lenght
        self._max_number_of_distinct_countries_in_round = max_number_of_distinct_countries_in_round
        self._required_patients = required_patients

    def keep(self, matching: Matching) -> bool:
        sequences = matching.get_sequences()
        cycles = matching.get_cycles()

        if max([cycle.length for cycle in cycles]) > self._max_cycle_length:
            return False

        if max([sequence.length for sequence in sequences]) > self._max_sequence_length:
            return False

        if max([rnd.country_count for rnd in
                set.union(sequences, cycles)]) > self._max_number_of_distinct_countries_in_round:
            return False

        for patient in self._required_patients:
            for rnd in set.union(sequences, cycles):
                if rnd.contains_patient(patient):
                    return True

        return False