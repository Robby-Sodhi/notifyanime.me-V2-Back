import DataBase
import MyAnimeList
import datetime
from flask import Flask, request, g
import base64
import psycopg2
import json
import secrets
app = Flask(__name__)
#****************** TEMPORARY JUST FOR DEVELOPMENT


#cors = CORS(app) //for development only
#from flask_cors import CORS, cross_origin


#*******************
# add logging for the amount of logins and dashboard visits!!!!!!!!!!
def get_db():
    if "db" not in g:
        g.db = DataBase.DataBase()
    return g.db
def generate_30_day_date():
    date_format_string = "%Y-%m-%d"
    return (datetime.datetime.now() + datetime.timedelta(30)).strftime(date_format_string)
def get_user_agent():
    return request.headers.get('User-Agent')

@app.route("/api/authenticateUser", methods=["POST"])
def authenticateUser():
    data_object = {"status": False, "session-key": None}
    #expected data type application/json
    requestData = request.get_json()
    try:
        username = requestData["username"]
        password = requestData["password"]
        type = requestData["type"]
    except KeyError:
        return json.dumps(data_object)
    if not username or not password or not type:
        return json.dumps(data_object)
    if type == "signup":
        if (get_db().check_if_username_exists(username)):
            return json.dumps(data_object)
        else:
            #assume its safe
            get_db().createUser(username, password)
    if (get_db().verify_user(username, password)):
        data_object["status"] = True;
        session_key = secrets.token_urlsafe(128)
        #assume its safe because we already verified user
        get_db().write_session_to_user(username, session_key, generate_30_day_date(), get_user_agent())
        data_object["session-key"] = session_key
        return json.dumps(data_object)
    else:
        return json.dumps(data_object)
    return json.dumps(data_object)
@app.route("/api/getWatchList", methods=["GET"])
def getWatchList():
    1 / 0
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
@app.route("/api/authenticateMal", methods=["POST"])
def authenticateMal():
    data_object = {"status": False}
    data = request.get_json()
    if not "sessionKey" in data or not "authorizationCode" in data or not data["sessionKey"] or not data["authorizationCode"] or not get_db().is_session_valid(data["sessionKey"]):
        return json.dumps(data_object)
    data_object["status"] = MyAnimeList.authenticate_user(data["sessionKey"], data["authorizationCode"], data["codeChallenge"], get_db())
    return json.dumps(data_object)
@app.route("/api/adjustEpisode", methods=["POST"])
def adjustEpisode():
    dataObject = {"status": False}
    requestData = json.loads(request.data)
    try:
        numWatched = requestData["numWatched"]
        id = requestData["id"]
    except KeyError:
        return json.dumps(dataObject)
    session_key = request.headers.get("session-key")
    if not session_key or not get_db().is_session_valid(session_key):
        return dataObject
    mal_auth_details = get_db().get_mal_auth_details(session_key)
    if not mal_auth_details["status"]:
        return dataObject
    if (not MyAnimeList.update_episode(mal_auth_details["accesstoken"], id, numWatched)):
        return json.dumps(dataObject)
    dataObject["status"] = True
    return json.dumps(dataObject)

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")
