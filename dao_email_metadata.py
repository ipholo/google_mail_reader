import mysql.connector
import keyring
from access_information_module import DatabaseConfiguration


SERVICE_ID = 'LDAP USERS STORAGE'


def connect_to_database():
    return mysql.connector.connect(
        host=DatabaseConfiguration.host,
        user=DatabaseConfiguration.user,
        passwd=DatabaseConfiguration.password,
        database=DatabaseConfiguration.database,
    )


def store_mail_metadata_in_database(date, from_email, subject):
    database_connection = connect_to_database()
    cursor = database_connection.cursor()
    sql_statement = "INSERT INTO users (date, from_email_subject) VALUES (%s, %s, %s)"
    value = (date, from_email, subject)
    cursor.execute(sql_statement, value)
    database_connection.commit()
    database_connection.close()
