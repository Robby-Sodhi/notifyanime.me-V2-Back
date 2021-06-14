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
    print(request.data)



if __name__ == "__main__":
    app.run(debug=True, port=8000)
