from __future__ import annotations

from typing import Optional, List, Callable
from re import split
from subprocess import run


class AdUser:
    def __init__(self,
                 name: str,
                 givenname: Optional[str],
                 surname: Optional[str],
                 samaccountname: str,
                 enabled: bool,
                 mail: Optional[str],
                 title: Optional[str],
                 department: Optional[str],
                 manager: Optional[str],
                 office: Optional[str],
                 streetaddress: Optional[str],
                 city: Optional[str],
                 state: Optional[str],
                 country: Optional[str],
                 postalcode: Optional[str]
                 ) -> None:
        self.name = name
        self.first_name = givenname
        self.last_name = surname
        self.user_name = samaccountname
        self.enabled = enabled
        self.email_address = mail
        self.job_title = title
        self.department = department
        self.manager = manager
        self.office = office
        self.street_address = streetaddress
        self.city = city
        self.state = state
        self.country = country
        self.zip_code = postalcode

    @classmethod
    def from_str(cls, string_values: str) -> AdUser:
        pattern = '(.+:.+\n[ ]+.+)|(.+:.+)'
        pairs = list(filter(lambda x: x is not None and x != '' and x != '\n', split(pattern, string_values)))
        try:
            properties = {i.split(':')[0].strip(): i.split(':')[1].strip() for i in pairs}
        except IndexError:
            print("Could not parse the following :")
            print(string_values.encode())
            quit(1)
        for (k, v) in properties.items():
            if v == '':
                properties[k] = None
            try:
                properties["enabled"] = bool(properties["enabled"])
            except KeyError:
                print(string_values, "\n\n\n", properties)
                quit(1)
            return cls(**properties)


def get_ad_users(filter_function: Callable[[AdUser], bool] = lambda x: True) -> List[AdUser]:
    """
            Produces a List of AdUsers. The filter function allows you to filter out unwanted users.
        for example if uou only want users where the username is first initial followed by lastname you might define
        this function:

        def filter_user_name (user:AdUser) -> bool:
            return user.user_name == f"{user.first_name[0]}{user.last_name}"
    
    """
    cmd = ("get-aduser -filter * -properties * | select name, givenname, surname, samaccountname, enabled, mail, "
           "title, department, @{l='manager';e={$_.manager.split(',')[0].split('=')[1]}}, office, streetaddress, "
           "city, state, country, postalcode")
    output = run(["powershell", "-command", cmd], capture_output=True).stdout.decode()
    users = []
    for user_properties in output.replace('\r', '').split('\n\n')[1:]:
        if user_properties == '':
            continue
        users.append(AdUser.from_str(user_properties))
    return list(filter(filter_function, users))
