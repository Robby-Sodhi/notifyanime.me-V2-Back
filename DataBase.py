import psycopg2
from flask_bcrypt import Bcrypt
import copy
from constants import host, database, user, password, port


class DataBase():
    def __init__(self):
        self.connection = psycopg2.connect(host=host,database=database,user=user,password=password,port="5432")

    def createUser(self, username, password):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO userinfo (username, password) VALUES (%s, %s)", (username, Bcrypt().generate_password_hash(password).decode('utf-8')))
    def check_if_username_exists(self, username):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT username FROM userinfo WHERE username=(%s)", (username, ))
                data = cursor.fetchall()
                if data:
                    return True #user exists
                return False #user doesn't exist
    def fetch_password(self, username):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT password FROM userinfo WHERE username=(%s)", (username, ))
                data = cursor.fetchall()
                #if somehow more than one person have that username just automatically fail password
                if not data or len(data) > 1 or not data[0]: #it is a list of tuples
                    return None
                return data[0][0] #first tuple first password
    def verify_user(self, username, password):
        crypt = Bcrypt()
        hashed_password = self.fetch_password(username)
        if (not hashed_password):
            return False
        elif crypt.check_password_hash(hashed_password, password):
            return True
        else:
            return False
    def write_session_to_user(self, username, session_key, expire, device):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO sessions (username, session, expire, device) VALUES ((%s), (%s), (%s), (%s))", (username, session_key, expire, device))
    def get_mal_auth_details(self, session_key):
        with self.connection:
            with self.connection.cursor() as cursor:
                dataObject = {"status": False, "accesstoken": None, "refreshtoken": None}
                username = self.get_username_from_session(session_key)
                if (not username):
                    return dataObject
                cursor.execute("SELECT accesstoken, refreshtoken FROM userinfo WHERE username=(%s)", (username, ))
                data = cursor.fetchall()
                if not data or len(data) > 1:
                    return dataObject
                else:
                    try:
                        dataObject2 = copy.deepcopy(dataObject)
                        dataObject2["accesstoken"] = data[0][0]
                        dataObject2["refreshtoken"] = data[0][1]
                        dataObject2["status"] = True
                    except:
                        return dataObject
                    else:
                        return dataObject2
    def write_mal_auth_details(self, session_key, access_token, refresh_token):
        with self.connection:
            with self.connection.cursor() as cursor:
                username = self.get_username_from_session(session_key)
                if (not username):
                    return;
                else:
                    cursor.execute("UPDATE userinfo SET accesstoken=(%s), refreshtoken=(%s) WHERE username=(%s)", (access_token, refresh_token, username))

    def get_username_from_session(self, session_key):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT username FROM sessions WHERE session=(%s)", (session_key, ))
                data = cursor.fetchall()
                #add expired checks
                if not data:
                    return None
                #it is safe because we assume all session keys are unique
                return data[0]
    def is_session_valid(self, session_key):
        if (self.get_username_from_session(session_key)):
            return True
        else:
            return False
    def clear_expired(self):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM sessions WHERE expire < now()")
