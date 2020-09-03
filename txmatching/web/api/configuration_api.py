# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import jsonify, request
from flask_restx import Resource

from txmatching.data_transfer_objects.configuration.configuration_from_dto import configuration_from_dto
from txmatching.data_transfer_objects.configuration.configuration_swagger import CONFIGURATION_MODEL
from txmatching.data_transfer_objects.configuration.configuration_to_dto import configuration_to_dto
from txmatching.database.services.config_service import get_current_configuration, save_configuration_as_current
from txmatching.web.api.namespaces import configuration_api
from txmatching.web.auth.login_check import login_required

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@configuration_api.route('/', methods=['GET', 'POST'])
class Configuration(Resource):

    @configuration_api.doc(body=CONFIGURATION_MODEL, security='bearer')
    @configuration_api.response(code=200, model=CONFIGURATION_MODEL, description='')
    @login_required()
    def post(self):
        configuration = configuration_from_dto(request.json)
        save_configuration_as_current(configuration)
        return jsonify(configuration)

    @configuration_api.doc(security='bearer')
    @configuration_api.response(code=200, model=CONFIGURATION_MODEL, description='')
    @login_required()
    def get(self) -> str:
        configuration_dto = configuration_to_dto(get_current_configuration())
        return jsonify(configuration_dto)