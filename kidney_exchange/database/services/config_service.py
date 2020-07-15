import dataclasses
from typing import Iterator

from kidney_exchange.config.configuration import Configuration, RecipientDonorScore
from kidney_exchange.database.db import db
from kidney_exchange.database.sql_alchemy_schema import ConfigModel

manual_recipients = 'manual_recipient_donor_scores'


def config_model_to_configuration(config_model: ConfigModel) -> Configuration:
    configuration_dict = config_model.parameters.copy()
    if 'manual_recipient_donor_scores' in configuration_dict:
        configuration_dict[manual_recipients] = [RecipientDonorScore(**recipient_donor_score) for
                                                 recipient_donor_score in
                                                 configuration_dict[manual_recipients]]
    return Configuration(**configuration_dict)


def get_configurations() -> Iterator[Configuration]:
    for config_model in get_config_models():
        yield config_model_to_configuration(config_model)


def get_current_configuration() -> Configuration:
    current_config_model = ConfigModel.query.get(0)
    if current_config_model is None:
        save_configuration_as_current(Configuration())
        return Configuration()
    else:
        return config_model_to_configuration(current_config_model)


def save_configuration_as_current(configuration: Configuration) -> int:
    maybe_config = ConfigModel.query.get(0)
    if maybe_config is not None:
        db.session.delete(maybe_config)
    config_model = _configuration_to_config_model(configuration)
    config_model.id = 0
    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def save_configuration_to_db(configuration: Configuration) -> int:
    config_model = _configuration_to_config_model(configuration)
    for existing_config in get_config_models():
        if existing_config.parameters == config_model.parameters:
            return existing_config.id

    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def get_config_models() -> Iterator[ConfigModel]:
    configs = ConfigModel.query.filter(ConfigModel.id > 0).all()
    return configs


def _configuration_to_config_model(configuration: Configuration) -> ConfigModel:
    return ConfigModel(parameters=dataclasses.asdict(configuration), created_by=1)
