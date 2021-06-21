import logging
import DataBase
import MyAnimeList
from datetime import datetime
from flask import Flask, request, g
from flask_cors import CORS, cross_origin
import base64
import psycopg2
import json
import secrets
app = Flask(__name__)
#****************** TEMPORARY JUST FOR TESTING
cors = CORS(app)
#*******************
logging.basicConfig(filename = 'NotifyAnime.meLog.log', level=logging.DEBUG, format = '%(asctime)s : %(levelname)s : %(message)s')
# add logging for the amount of logins and dashboard visits!!!!!!!!!!
def get_db():
    if "db" not in g:
        g.db = DataBase.DataBase()
    return g.db


@app.route("/authenticateUser", methods=["POST"])
def authenticateUser():
    data_object = {"status": False, "session-key": None}
    #expected data type application/json
    requestData = request.get_json()
    try:
        username = requestData["username"]
        password = requestData["password"]
    except KeyError:
        app.logger.warning(f"username or password missing in request to /authenticateUser")
        return json.dumps(data_object)
    if not username or not password:
        app.logger.warning(f"username or password missing in request to /authenticateUser")
        return json.dumps(data_object)
    elif (get_db().verify_user(username, password)):
        data_object["status"] = True;
        session_key = secrets.token_urlsafe(128)
        #assume its safe because we already verified user
        get_db().write_session_to_user(username, session_key)
        data_object["session-key"] = session_key
        app.logger.info(f"logged {username} in with session_key {session_key}")
        return json.dumps(data_object)
    else:
        return json.dumps(data_object)
@app.route("/getWatchList", methods=["GET"])
def getWatchList():
    dataObject = {"sessionKeyValid": False, "WatchList": None}
    session_key = request.headers.get("session-key")
    if not session_key or not get_db().is_session_valid(session_key):
        return dataObject
    for _ in range(2): #loop can only run twice
        mal_auth_details = get_db().get_mal_auth_details(session_key)
        if not mal_auth_details["status"]:
            return dataObject
        else:
            dataObject["sessionKeyValid"] = get_db().is_session_valid(session_key)
            dataObject["WatchList"] = MyAnimeList.get_watch_list(mal_auth_details["accesstoken"])
            if (not dataObject["WatchList"]):
                MyAnimeList.refresh_access_token(session_key, mal_auth_details["refreshtoken"], get_db())
            else:
                return dataObject
    return dataObject
@app.route("/authenticateMal", methods=["POST"])
def authenticateMal():
    data_object = {"status": False}
    data = request.get_json()
    if not "sessionKey" in data or not "authorizationCode" in data or not data["sessionKey"] or not data["authorizationCode"] or not get_db().is_session_valid(data["sessionKey"]):
        return json.dumps(data_object)
    data_object["status"] = MyAnimeList.authenticate_user(data["sessionKey"], data["authorizationCode"], data["codeChallenge"], get_db())
    app.logger.info(f"session_key {data['sessionKey']} attempted to log-in to MAL status={data_object['status']}")
    return json.dumps(data_object)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
