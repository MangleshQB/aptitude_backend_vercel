import bcrypt
import requests


def check_bcrypt_password(user_input: str, password: str) -> bool:
    """
    Check if password is valid or not using bcrypt for CRM user
    :param user_input:
    :param password:
    :return: bool
    """
    return bcrypt.checkpw(user_input.encode('utf-8'), password.encode('utf-8'))