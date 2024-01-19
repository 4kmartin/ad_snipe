from ad_snipe.ad_user import get_ad_users
from ad_snipe.new_users import get_users_not_in_snipe_it, add_missing_users_to_snipe_it
from ad_snipe.alerting import EmailClient, log, email_alert
from ad_snipe.remove_users import get_inactive_users, get_ids_of_inactive_users, delete_users, get_deleted_users
from pysnipeit import SnipeItConnection, get_users
from dotenv import dotenv_values
from datetime import datetime
from returns.result import Success, Failure

# Initialize Values:
secrets = dotenv_values(".env")
connection = SnipeItConnection()
connection.connect(secrets["SNIPEIT_URL"], secrets["SNIPEIT_API"], True)
email_client = EmailClient(secrets["EMAIL_ADDRESS"],
                           secrets["EMAIL_PASSWORD"],
                           secrets["EMAIL_LIST"].split(','),
                           secrets["EMAIL_SERVER"],
                           int(secrets["EMAIL_PORT"])
                           )
log(f"\n\n\nBegin process: {datetime.now()}\n{'-' * 10}\n")

ad_users = get_ad_users()

match get_users(connection):
    case Success(snipeit_users):
        # New Users:

        new_users = get_users_not_in_snipe_it(
            list(filter(lambda x: x.enabled, ad_users)),
            snipeit_users
        )
        names = '\n\t'.join([user.name for user in new_users])
        message = f"adding the following users to Snipe-IT {names}"
        email_alert(email_client, "Adding Users to Snipe-IT", message)
        add_missing_users_to_snipe_it(
            new_users,
            connection
        )

        # Remove users
        inactive = list(
            filter(lambda x: x.user_name in [user.username for user in snipeit_users], get_inactive_users(ad_users)))
        deleted = get_deleted_users(connection, inactive)
        ids = get_ids_of_inactive_users(connection, [user for user in inactive if user not in deleted])
        delete_users(ids, connection)

        names = '\n\t'.join([user.name for user in inactive if user not in get_deleted_users(connection, inactive)])

        if len(names) > 0:
            email_alert(email_client, "These users could not be deleted", names)

    case Failure(why):
        issue = f"could not get users from SnipeIt:\n{why}"
        log(issue)
        email_alert(email_client, "Snipe-IT Connection Error", issue)
        print(issue)
        quit()
