from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from bson.objectid import ObjectId
import requests
from pymongo import MongoClient
from flask import Response
import re

app = Flask(__name__)
api = Api(app)

db = MongoClient('mongodb://userdb:27017/').users
uriWrite = 'http://users:8080/users/DbWrite'
uriRead = 'http://users:8080/users/DbRead'

def insertHelp(allDetails):
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse 

def readHelp(allDetails):
    dbResponse = requests.post(uriRead,data=json.dumps(allDetails))
    return dbResponse # contains either {'result':0} or {'result':1}

def deleteHelp(allDetails):
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse

class AddUser(Resource):
    # MAIN API 1 - ADD USER
    def put(self):
        try:
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
            temp = json.dumps(temp)
            allTemp = {'temp':temp,'method':'readOne'}
            dbResponse = readHelp(allTemp) # contains either {'result':0} or {'result':1}
            if dbResponse.json()["result"] == 1:
                return Response("User already exists!",status=400,mimetype='application/json')

            details = {'username' : username, 'password' : password}
            allDetails = {"details": details, "method":"insert"}

            dbResponse = insertHelp(allDetails)  # all deatils -> { {uswrname, pws}, method }
            if dbResponse.json()['result'] == 201:
                return Response("{}", status=201, mimetype="application/json")
            else:
                return Response("",status=500,mimetype='application/json')
        except:
            return Response("",status=500,mimetype='application/json')

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
        # try:
            user = db.user
            details = {'username':username}
            
            temp = {'username' : username}
            temp = json.dumps(temp)
            allTemp = {'temp':temp,'method':'readOne'}
            dbResponse = readHelp(allTemp) # contains either {'result':0} or {'result':1}
            if dbResponse.json()["result"] == 0:
                return Response("User doesn't not exists!",status=400,mimetype='application/json')
            
            # details = json.dumps(details)
            allDetails = {'details':details,'method':'delete'}
            dbResponse = deleteHelp(allDetails)
            if dbResponse.json()['result'] == 200:
                return Response("{}", status=200, mimetype="application/json")
            else:
                return Response("",status=500,mimetype='application/json')

class DbWrite(Resource):
    # DB WRITE API
    def post(self):
        user = db.user
        allDetails = request.get_json(force=True)  # all details -> { {uswrname, pws}, method }
        method = allDetails['method']
        if method == "insert":
            try:
                user.insert(allDetails['details']) # details -> {uswrname, pws}
                return jsonify({'result' : 201})
            except:
                return jsonify({'result' : 500})
        if method == "delete":
            # try:
                user.delete_one(allDetails['details'])
                return jsonify({'result' : 200})
 
class DbRead(Resource):
    # DB READ API
    def post(self):
        user = db.user
        allDetails = request.get_json(force=True)
        temp = json.loads(allDetails['temp'])
        # allDetails has {{username:username},method}
        method = allDetails['method']
        if method == "readOne":
            query = user.find_one(temp) # temp has ('username':username)
            if query:    # new user, can be added
                return jsonify({"result":1}) # already existing user
            else: 
                return jsonify({"result":0}) # user does not exist

api.add_resource(AddUser,'/users')
api.add_resource(RemUser,'/users/<username>')
api.add_resource(DbWrite,'/users/DbWrite')
api.add_resource(DbRead,'/users/DbRead')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)