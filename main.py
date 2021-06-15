from flask import Flask, request
from flask_cors import CORS, cross_origin
from DataBase import DB
import base64
import psycopg2
import json
import secrets
app = Flask(__name__)
#****************** TEMPORARY JUST FOR TESTING
cors = CORS(app)
#*******************
# add logging for the amount of logins and dashboard visits!!!!!!!!!!

@app.route("/authenticateUser", methods=["POST"])
def authenticateUser():
    data_object = {"status": False, "session-key": None}
    if request.content_type == "text/plain":
        username = json.loads(request.data)["username"]
        password = json.loads(request.data)["password"]
        if not username or not password:
            return json.dumps(data_object)
        elif (DB.verify_user(username, password)):
            data_object["status"] = True;
            session_key = secrets.token_urlsafe(128)
            #assume its safe because we already verified user
            DB.write_session_to_user(username, session_key)
            data_object["session-key"] = session_key
            return json.dumps(data_object)
        else:
            return json.dumps(data_object)
    return json.dumps(data_object)
@app.route("/getWatchList", methods=["GET"])
def getWatchList():
    dataObject = {"sessionKeyValid": False, "WatchList": None}
    session_key = request.headers.get("session-key")
    if not session_key:
        return dataObject
    mal_auth_details = DB.get_mal_auth_details(session_key)
    if not mal_auth_details["status"]:
        return dataObject
    else:
        dataObject["sessionKeyValid"] = True
        dataObject["WatchList"] = False
        return dataObject
        #make a mal api class and get watch list....
@app.route("/authenticateMal", methods=["POST"])
def authenticateMal():
    print(request.data)
    return json.dumps({"status": True})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
