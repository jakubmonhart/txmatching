from dataclasses import dataclass
from typing import Dict, List, Optional

from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssue
from txmatching.patients.patient import Recipient
from txmatching.utils.recipient_donor_compatibility_details import RecipientDonorCompatibilityDetails


@dataclass
class RecipientDTOOut(Recipient):
    all_messages: Optional[Dict[str, List[ParsingIssue]]] = None
    cpra: Optional[float] = None
    compatible_donors_details: Optional[List[RecipientDonorCompatibilityDetails]] = None


@dataclass
class UpdatedRecipientDTOOut:
    recipient: RecipientDTOOut
    parsing_issues: List[ParsingIssue]
