from typing import List

from pysnipeit import SnipeItConnection
from pysnipeit.user import get_user_id, delete_user, get_users
from returns.result import Success, Failure

from .ad_user import AdUser
from .alerting import log


def get_inactive_users(users: List[AdUser]) -> List[AdUser]:
    return list(filter(__is_inactive, users))


def __is_inactive(user: AdUser) -> bool:
    return not user.enabled


def get_deleted_users(connection: SnipeItConnection, users: List[AdUser]) -> List[AdUser]:
    deleted_users = []
    match get_users(connection, deleted=True):
        case Failure(why):
            log(f'Failed to get deleted users\n\t{why}\n\n')
        case Success(del_users):
            user_names = [user.username for user in del_users]
            for user in users:
                if user.user_name in user_names:
                    deleted_users.append(user)
    return deleted_users


def get_ids_of_inactive_users(connection: SnipeItConnection, inactive_users: List[AdUser]) -> List[int]:
    user_ids = []
    for user in inactive_users:
        match get_user_id(connection, user.first_name, user.last_name):
            case Failure(why):
                log(why)
            case Success(v):
                user_ids.append(v)
    return user_ids


def delete_users(user_ids: List[int], connection: SnipeItConnection) -> None:
    for user_id in user_ids:
        match delete_user(connection, user_id):
            case Failure(why):
                log(why)
            case Success(_):
                pass
