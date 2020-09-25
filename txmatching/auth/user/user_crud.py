from typing import Optional

from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import UserUpdateException
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.database.services.app_user_management import get_app_user_by_email, persist_user, \
    update_password_for_user
from txmatching.database.sql_alchemy_schema import AppUserModel


def register_user(email: str, password: str, role: UserRole, phone_number: str) -> AppUserModel:
    """
    Registers new user for given email, password and role.
    """
    assert role != UserRole.SERVICE

    _assert_user_registration(email, password, role, phone_number)
    user = AppUserModel(
        email=email,
        pass_hash=encode_password(password),
        role=role,
        second_factor_material=generate_totp_seed(),
        phone_number=phone_number
    )
    persist_user(user)
    return user


def change_user_password(user_id: int, new_password: str):
    """
    Updates password for the user.
    """
    _assert_user_password_validity(new_password)
    pwd_hash = encode_password(new_password)
    update_password_for_user(user_id=user_id, new_password_hash=pwd_hash)


def _assert_user_registration(email: str, password: str, role: Optional[UserRole], phone_number: str):
    if not email:
        raise UserUpdateException('Invalid email address.')
    if not role:
        raise UserUpdateException('Invalid user role.')
    if get_app_user_by_email(email):
        raise UserUpdateException('The e-mail address is already in use.')
    _assert_user_password_validity(password)
    _assert_phone_number_validity(phone_number)


def _assert_phone_number_validity(phone_number: str):
    # TODO verify that this is phone number
    if not phone_number:
        raise UserUpdateException('Invalid phone number.')


def _assert_user_password_validity(password: str):
    # TODO define our password policies for the users
    if not password:
        raise UserUpdateException('Invalid password.')
