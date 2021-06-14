from flask import Flask, request
from flask_cors import CORS, cross_origin
from DataBase import DB
import base64
import psycopg2
import json
app = Flask(__name__)
#****************** TEMPORARY JUST FOR TESTING
cors = CORS(app)
#*******************


@app.route("/authenticateUser", methods=["POST"])
def authenticateUser():
    data_object = {"status": False, "session-key": None, "expires": None}
    if request.content_type == "text/plain":
        username = json.loads(request.data)["username"]
        password = json.loads(request.data)["password"]
        if not username or not password:
            return json.dumps(data_object)
        elif (DB.verify_user(username, password)):
            data_object["status"] = True;
            data_object["session-key"] = username
            data_object["expires"] = "18 Dec 2013 12:00:00 UTC"
            return json.dumps(data_object)
        else:
            return json.dumps(data_object)
    return json.dumps(data_object)
if __name__ == "__main__":
    app.run(debug=True, port=8000)
