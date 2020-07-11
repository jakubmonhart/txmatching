from kidney_exchange.config.configuration import Configuration
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.scorers.additive_scorer import AdditiveScorer
from kidney_exchange.scorers.scorer_base import TRANSPLANT_IMPOSSIBLE
from kidney_exchange.utils.hla_system.compatibility_index import compatibility_index


class HLAAdditiveScorer(AdditiveScorer):
    def __init__(self, enforce_same_blood_group: bool = True,
                 minimum_compatibility_index: float = 0.0,
                 require_new_donor_having_better_match_in_compatibility_index: bool = True,
                 require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = True,
                 use_binary_scoring: bool = False):
        """
        :param enforce_same_blood_group:
            True: donor has to have the same blood group as recipient
            False: donor just needs to have blood group that is in recipients acceptable blood groups
        :param minimum_compatibility_index: Minimum index of compatibility that is required for a transplant to be possible
        :param require_new_donor_having_better_match_in_compatibility_index: New donor for recipient needs to have
            a better match in the compatibility index than (the best of) his original relative(s)
        :param require_new_donor_having_better_match_in_compatibility_index_or_blood_group: New donor for recipient needs
            to have a better match in compatibility index or in blood group than (the best of) his original relative(s)
        :param use_binary_scoring: If all the conditions above are satisfied, then use just 1 for possible transplant
            and -inf for impossible
        """
        self._enforce_same_blood = enforce_same_blood_group
        self._minimum_compatibility_index = minimum_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index = require_new_donor_having_better_match_in_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group = require_new_donor_having_better_match_in_compatibility_index_or_blood_group
        self._use_binary_scoring = use_binary_scoring

    def score_transplant(self, donor: Donor, recipient: Recipient) -> float:
        donor_recipient_ci = compatibility_index(donor.parameters, recipient.parameters)
        related_donor_recipient_ci = compatibility_index(recipient.related_donor.parameters, recipient.parameters)

        # Donor must have blood group that is acceptable for recipient
        if donor.parameters.blood_group not in recipient.parameters.acceptable_blood_groups:
            return TRANSPLANT_IMPOSSIBLE

        # Recipient can't have antibodies that donor has antigens for
        # TODO: Ask immunologists what is exactly the bad combination and for what antigens?
        for antibody_code in recipient.parameters.hla_antibodies.codes + recipient.parameters.hla_antibodies_low_resolution:
            if antibody_code in donor.parameters.hla_antigens.codes + donor.parameters.hla_antigens_low_resolution:
                return TRANSPLANT_IMPOSSIBLE

        # If required, donor must have either better match in blood group or better compatibility index than
        # the donor related to the recipient
        if self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group \
                and (donor.parameters.blood_group != recipient.parameters.blood_group
                     and donor_recipient_ci <= related_donor_recipient_ci):
            return TRANSPLANT_IMPOSSIBLE

        # If required, the donor must have the same blood group as recipient
        if self._enforce_same_blood and (donor.parameters.blood_group != recipient.parameters.blood_group):
            return TRANSPLANT_IMPOSSIBLE

        # If required, the compatibility index between donor and recipient must be higher than
        # between recipient and the donor related to him
        if self._require_new_donor_having_better_match_in_compatibility_index \
                and donor_recipient_ci <= related_donor_recipient_ci:
            return TRANSPLANT_IMPOSSIBLE

        # The compatibility index must be higher than the minimum required
        if donor_recipient_ci < self._minimum_compatibility_index:
            return TRANSPLANT_IMPOSSIBLE

        if self._use_binary_scoring:
            return 1.0
        else:
            return donor_recipient_ci

    @classmethod
    def from_config(cls, configuration: Configuration) -> "HLAAdditiveScorer":
        hla_additive_scorer = HLAAdditiveScorer(enforce_same_blood_group=configuration.enforce_same_blood_group,
                                                minimum_compatibility_index=configuration.minimum_compatibility_index,
                                                require_new_donor_having_better_match_in_compatibility_index=configuration.require_new_donor_having_better_match_in_compatibility_index,
                                                require_new_donor_having_better_match_in_compatibility_index_or_blood_group=configuration.require_new_donor_having_better_match_in_compatibility_index_or_blood_group,
                                                use_binary_scoring=configuration.use_binary_scoring)

        return hla_additive_scorer
