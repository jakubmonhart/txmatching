# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask_restx import Resource

from txmatching.auth.login_check import login_required
from txmatching.data_transfer_objects.tx_session.txm_event_swagger import (
    TxmEventJsonIn, TxmEventJsonOut, UploadPatientsJson, FailJson, PatientUploadSuccessJson)
from txmatching.web.api.namespaces import txm_event_api

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@txm_event_api.route('/tx_session', methods=['POST'])
class TxSessionApi(Resource):

    @txm_event_api.doc(body=TxmEventJsonIn, security='bearer',
                       description='Endpoint that lets an ADMIN create a new TX session. \
                        The ADMIN should specify TX session name.')
    @txm_event_api.response(code=200, model=TxmEventJsonOut,
                            description='Returns the newly created TX session object.')
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication Denied')
    @txm_event_api.response(code=409, model=FailJson, description='Non-unique patients provided')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected, see contents for details')
    @login_required()
    def post(self):
        pass


@txm_event_api.route('/upload_patients', methods=['PUT'])
class TxSessionUploadPatients(Resource):

    @txm_event_api.doc(body=UploadPatientsJson, security='bearer',
                       description='This endpoint allows the country editor to upload patient data for given \
                        TX session. TX session name has to be provided by an ADMIN. The endpoint removes all patients \
                        from respective country in case there were any.')
    @txm_event_api.response(code=200, description='Success', model=PatientUploadSuccessJson)
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication Denied')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected, see contents for details')
    # TODO validate based on country of the user https://trello.com/c/8tzYR2Dj
    @login_required()
    def put(self):
        # TODO add here the logic that will update patients https://trello.com/c/Yj70es9D
        pass
