from typing import List
from returns.result import Success, Failure
from .ad_user import AdUser
from .alerting import log
from pysnipeit import SnipeItUser, SnipeItConnection, create_new_user
from pysnipeit.user import get_user_id

import string
import random


def get_users_not_in_snipe_it(ad_users: List[AdUser], snipeit_users: List[SnipeItUser]) -> List[AdUser]:
    snipeit = [user.username.lower() for user in snipeit_users]
    return [user for user in ad_users if user.user_name.lower() not in snipeit]


def add_missing_users_to_snipe_it(missing_users: List[AdUser], connection: SnipeItConnection) -> None:
    manager_ids = {}
    manager = None
    arbitrary_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=19))
    for user in missing_users:
        if user.manager in manager_ids.keys():
            manager = manager_ids[user.manager]
        elif user.manager is not None:
            match get_user_id(connection, user.manager.split()[0], user.manager.split()[1]):
                case Success(manager_id):
                    manager_ids[user.manager] = manager_id
                    manager = manager_id
                case _:
                    pass
            match create_new_user(
                connection,
                user.first_name,
                user.user_name,
                arbitrary_password,
                arbitrary_password,
                last_name=user.last_name,
                jobtitle=user.job_title,
                manager_id=manager,
                email=user.email_address,
            ):
                case Failure(why):
                    log(f"Failed to create user ({user.user_name})\n{why}")
                case Success(_):
                    log(f"created {user.user_name}")
