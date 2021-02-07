from tests.test_utilities.create_dataclasses import (get_test_donors,
                                                     get_test_recipients)
from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.db import db
from txmatching.database.services.patient_service import \
    get_patients_persistent_hash
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_one_country
from txmatching.database.services.txm_event_service import get_txm_event
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.patients.hla_model import HLAType
from txmatching.patients.patient import DonorType, TxmEvent
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex
from txmatching.utils.logged_user import get_current_user_id

TXM_EVENT_NAME = 'test'

DONOR_UPLOAD_DTOS = [
    DonorUploadDTO(
        medical_id='D1',
        blood_group=BloodGroup.A,
        hla_typing=[
            'A9', 'A21'
        ],
        donor_type=DonorType.DONOR.value,
        related_recipient_medical_id='R1',
        sex=Sex.M,
        height=180,
        weight=90,
        year_of_birth=1965
    ),
    DonorUploadDTO(
        medical_id='D2',
        blood_group=BloodGroup.B,
        hla_typing=[
            'A9', 'A21'
        ],
        donor_type=DonorType.DONOR.value,
        related_recipient_medical_id='R2',
        sex=Sex.M,
        height=178,
        weight=69,
        year_of_birth=1967
    ),
    DonorUploadDTO(
        medical_id='D3',
        blood_group=BloodGroup.AB,
        hla_typing=[
            'A9'
        ],
        donor_type=DonorType.DONOR.value,
        related_recipient_medical_id='R3',
        sex=Sex.M,
        height=145,
        weight=56,
        year_of_birth=1989
    ),
]

RECIPIENT_UPLOAD_DTOS = [
    RecipientUploadDTO(
        acceptable_blood_groups=[
            BloodGroup.A,
            BloodGroup.ZERO
        ],
        medical_id='R1',
        blood_group=BloodGroup.A,
        hla_typing=[
            'A9', 'A21'
        ],
        hla_antibodies=[
            HLAAntibodiesUploadDTO(
                name='B42',
                mfi=2000,
                cutoff=2100
            )
        ],
        sex=Sex.F,
        height=150,
        weight=65,
        year_of_birth=2001,
        waiting_since='2020-01-06',
        previous_transplants=0
    ),
    RecipientUploadDTO(
        acceptable_blood_groups=[
            BloodGroup.B,
            BloodGroup.ZERO
        ],
        medical_id='R2',
        blood_group=BloodGroup.B,
        hla_typing=[
            'A9', 'A21'
        ],
        hla_antibodies=[
            HLAAntibodiesUploadDTO(
                name='B42',
                mfi=2000,
                cutoff=2200
            )
        ],
        sex=Sex.F,
        height=189,
        weight=70,
        year_of_birth=1996,
        waiting_since='2020-02-07',
        previous_transplants=0
    ),
    RecipientUploadDTO(
        acceptable_blood_groups=[
            BloodGroup.ZERO
        ],
        medical_id='R3',
        blood_group=BloodGroup.ZERO,
        hla_typing=[
            'A9', 'A21'
        ],
        hla_antibodies=[
            HLAAntibodiesUploadDTO(
                name='B42',
                mfi=2000,
                cutoff=2300
            )
        ],
        sex=Sex.M,
        height=201,
        weight=120,
        year_of_birth=1999,
        waiting_since='2020-05-13',
        previous_transplants=0
    )
]

PATIENT_UPLOAD_DTO = PatientUploadDTOIn(
    country=Country.CZE,
    txm_event_name=TXM_EVENT_NAME,
    donors=DONOR_UPLOAD_DTOS,
    recipients=RECIPIENT_UPLOAD_DTOS
)


class TestPatientService(DbTests):

    def test_update_txm_event_patients(self):
        txm_event = create_or_overwrite_txm_event(name=TXM_EVENT_NAME)

        # Insert config and validates that it is stored into DB
        user_id = get_current_user_id()
        config = ConfigModel(
            txm_event_id=txm_event.db_id,
            parameters={},
            patients_hash=get_patients_persistent_hash(txm_event),
            created_by=user_id
        )

        db.session.add(config)
        db.session.commit()
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()
        self.assertEqual(1, len(configs))

        replace_or_add_patients_from_one_country(PATIENT_UPLOAD_DTO)

        # Validate that configs of particular TXM event are not deleted.
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()
        self.assertEqual(1, len(configs))

        # Validate that patients hash has changed
        txm_event_new = get_txm_event(txm_event.db_id)
        self.assertNotEqual(config.patients_hash, get_patients_persistent_hash(txm_event_new))

    def test_get_patients_hash(self):
        txm_event_1 = TxmEvent(
            1, 'event_name_1',
            all_donors=get_test_donors(),
            all_recipients=get_test_recipients()
        )
        hash_1 = get_patients_persistent_hash(txm_event_1)
        self.assertEqual(hash_1, 1602329590066289936)

        # changing event db id, event name does not change the hash
        txm_event_2 = TxmEvent(
            2, 'event_name_2',
            all_donors=get_test_donors(),
            all_recipients=get_test_recipients()
        )
        hash_2 = get_patients_persistent_hash(txm_event_2)
        self.assertEqual(hash_1, hash_2)

        # Changing donors changes the hash
        txm_event_3 = TxmEvent(
            1, 'event_name_1',
            all_donors=[],
            all_recipients=get_test_recipients()
        )
        hash_3 = get_patients_persistent_hash(txm_event_3)
        self.assertNotEqual(hash_1, hash_3)

        # Changing recipients changes the hash
        txm_event_4 = TxmEvent(
            1, 'event_name_1',
            all_donors=get_test_donors(),
            all_recipients=[]
        )
        hash_4 = get_patients_persistent_hash(txm_event_4)
        self.assertNotEqual(hash_1, hash_4)

        # changing hla type changes the hash
        new_donors = get_test_donors()
        self.assertEqual(
            new_donors[0].parameters.hla_typing.hla_per_groups[0].hla_types[0],
            HLAType('A1')
        )
        new_donors[0].parameters.hla_typing.hla_per_groups[0].hla_types[0] = HLAType('A3')

        txm_event_5 = TxmEvent(
            1, 'event_name_1',
            all_donors=new_donors,
            all_recipients=get_test_recipients()
        )
        hash_5 = get_patients_persistent_hash(txm_event_5)
        self.assertNotEqual(hash_1, hash_5)
