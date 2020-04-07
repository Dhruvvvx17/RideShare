from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from bson.objectid import ObjectId
import requests
from pymongo import MongoClient
from flask import Response
import re

app = Flask(__name__)
#from userflask import app
api = Api(app)

#app.config['MONGO_DBNAME'] = 'users'
#app.config['MONGO_URI'] = 'mongodb://usersdb:27017'

db = MongoClient('mongodb://userdb:27017/').users
uriWrite = 'http://users:8080/users/DbWrite'
uriRead = 'http://users:8080/users/DbRead'

def insertHelp(allDetails):

    # dbResponse = requests.post(uriWrite,data=json.dumps(allDetails)).json()
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse 

def readHelp(allDetails):
    dbResponse = requests.post(uriRead,data=json.dumps(allDetails))
    return dbResponse # contains either {'result':0} or {'result':1}


class AddUser(Resource):
    # MAIN API 1 - ADD USER
    def put(self):
        try:
            username = request.json['username']
            password = request.json['password']

        except:
            return Response("Invalid Input JSON",status=400,mimetype='application/json')
            # NEED TO CHECK PWS HERE -> 40 (5) chars, hex symbols only
            # if not re.match("([a-fA-F0-9]{5})",password):

        if not len(password) == 5:
            return Response("Invalid Password!",status=400,mimetype='application/json')

        #CHECKING IF USER ALREADY EXISTS
        temp = {'username' : username}
        allTemp = {'temp':temp,'method':'readOne'}
        dbResponse = readHelp(allTemp).json # contains either {'result':0} or {'result':1}
        if dbResponse == {'result':1}:
            return Response("User already exists!",status=400,mimetype='application/json')

        details = {'username' : username, 'password' : password}
        allDetails = {"details": details, "method":"insert"}

        dbResponse = insertHelp(allDetails).json  # all deatils -> { {uswrname, pws}, method }
        if dbResponse:
            return Response("{}", status=201, mimetype="application/json")
        elif dbResponse == "500":
            return Response("",status=500,mimetype='application/json').json()


    # TEMP API 1 - LIST ALL USERS
    def get(self):
        user = db.user
        output = []
        for q in user.find():
            output.append({'username':q['username'],'password':q['password']})
        return {'result':output}



class RemUser(Resource):
    # MAIN API 2 - DELETE USER
    def delete(self,username):
        user = db.user
        details = {'username':username,'apiNo':2}
	    # users:8080 -> here users is the service 'users'
        uid = requests.post(uri,data=json.dumps(details)).json()['_id']
        print(uid)
        if (uid == -1):
            output = "User does not exist"
        else:
            user.delete_one({'_id':ObjectId(uid)})
            output = 'Deleted Successfully!'
        return output



class DbWrite(Resource):
    # DB WRITE API
    def post(self):
        user = db.user
        allDetails = request.get_json(force=True)  # all deatils -> { {uswrname, pws}, method }
        method = allDetails['method']
        if method == "insert":
            try:
                user_id = user.insert(allDetails['details']) # details -> {uswrname, pws}
                return jsonify({'result' : {}})
            except:
                return "500"

class DbRead(Resource):
    # DB READ API
    def post(self):
        user = db.user
        allDetails = request.get_json(force=True)
        # allDetails has {{username:username},method}
        method = allDetails['method']
        if method == "readOne":
            query = user.find_one(allDetails['temp'])
            # temp has ('username':username)
            # user_id = query['_id']
            if not query:   # new user, can be added
                return jsonify({'result':0})
            else: 
                return jsonify({'result':1}) # already existing user


api.add_resource(AddUser,'/users')
api.add_resource(RemUser,'/users/<username>')
api.add_resource(DbWrite,'/users/DbWrite')
api.add_resource(DbRead,'/users/DbRead')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
