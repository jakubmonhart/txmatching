import json
import unittest

import numpy as np

from kidney_exchange.scorers.tabular_scorer import TabularScorer
from kidney_exchange.solvers.all_solutions_solver import AllSolutionsSolver
from kidney_exchange.utils.get_absolute_path import get_absolute_path


class TestAllSolutionsSolver(unittest.TestCase):
    def setUp(self) -> None:
        sample_score_matrix_path = get_absolute_path("/tests/resources/sample_score_matrix.json")
        with open(sample_score_matrix_path, "r") as sample_score_matrix_file:
            self._score_matrix = json.load(sample_score_matrix_file)

        self._expected_max_score = 92.0
        self._expected_num_solutions = 1886

    def test_solve(self):
        # TODO: Add more specific test
        scorer = TabularScorer(score_matrix=self._score_matrix)
        solver = AllSolutionsSolver()
        all_solutions = list(solver._solve(score_matrix=np.array(self._score_matrix)))
        all_scores = []
        for solution in all_solutions:
            solution_score = sum([scorer.score_transplant_ij(donor_index, recipient_index)
                                  for (donor_index, recipient_index) in solution])
            all_scores.append(solution_score)

        self.assertEqual(max(all_scores), self._expected_max_score)
        self.assertEqual(len(all_solutions), self._expected_num_solutions)