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

userdb = MongoClient('mongodb://userdb:27017/').users
ridedb = MongoClient('mongodb://ridedb:27017/').rides

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

def modifyHelp(allDetails):
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

            if not re.match("([a-fA-F0-9]{5})",password):
                return Response("Invalid Password!",status=400,mimetype='application/json')

            #CHECKING IF USER ALREADY EXISTS
            details = {'username' : username}
            allDetails = {'details':details,'method':'readOne','collection':'user'}
            dbResponse = readHelp(allDetails) # contains either {'result':0} or {'result':1}

            if dbResponse.json()["result"] == 1:
                return Response("User already exists!",status=400,mimetype='application/json')

            details = {'username' : username, 'password' : password}
            allDetails = {"details": details, "method":"insert",'collection':'user'}

            dbResponse = insertHelp(allDetails)  # all details -> { {uswrname, pws}, method }
            if dbResponse.json()['result'] == 201:
                return Response("{}", status=201, mimetype="application/json")
            else:
                return Response("",status=500,mimetype='application/json')
        except:
            return Response("",status=500,mimetype='application/json')

    # TEMP API 1 - LIST ALL USERS
    def get(self):
        output = []
        for q in userdb.user.find():
            output.append({'username':q['username'],'password':q['password']})
        return {'result':output}

class RemUser(Resource):
    # MAIN API 2 - DELETE USER
    def delete(self,username):
        try:
            details = {'username':username}

            allDetails = {'details':details,'method':'readOne','collection':'user'}
            dbResponse = readHelp(allDetails) # contains either {'result':0} or {'result':1}
            if dbResponse.json()["result"] == 0:
                return Response("User doesn't not exists!",status=400,mimetype='application/json')
            
            allDetails = {'details':details,'method':'deleteOne','collection':'user'}
            dbResponse = deleteHelp(allDetails)

            if dbResponse.json()['result'] == 200:
                # Remove all rides created by that user and remove the user from all rides he is a part of.
                details = {'created_by':username}
                allDetails = {'details':details,'method':'deleteMany','collection':'rides'}
                dbResponse_created = deleteHelp(allDetails)     # response returned after the rides created by the user have been removed

                details = {'username':username}
                allDetails = {'details':details,'method':'modifyList','collection':'rides'}
                dbResponse_partof = modifyHelp(allDetails)      # response returned after the user is pulled from all the rides he is a part of

                if ((dbResponse_created.json()['result'] == 200) and (dbResponse_partof.json()['result']==200)):
                    return Response("{}", status=200, mimetype="application/json")
                else:
                    return Response("",status=500,mimetype='application/json')
            else:
                return Response("",status=500,mimetype='application/json')


class DbWrite(Resource):
    # DB WRITE API
    def post(self):
        allDetails = request.get_json(force=True)  # all details -> { {uswrname, pws}, method }
        
        collection = allDetails['collection']
        if collection == 'user':
            collection = userdb.user
        else:
            collection = ridedb.ride

        method = allDetails['method']
        details = allDetails['details']
        
        if method == "insert":
            try:
                collection.insert(details) # details -> {uswrname, pws}
                return jsonify({'result' : 201})
            except:
                return jsonify({'result' : 500})

        elif method == "deleteOne":
            try:
                collection.delete_one(details)
                return jsonify({'result' : 200})
            except:
                return jsonify({'result' : 500})

        elif method == "deleteMany":
            try:
                collection.delete_many(details)
                return jsonify({'result' : 200})
            except:
                return jsonify({'result' : 500})

        elif method == "modifyList":
            try:
                user_to_remove = details['username']      #details => {'username':"username"} "username" - from URL
                collection.update({}, {'$pull':{ 'users':{ '$in': [user_to_remove] }}}, multi=True)
                return jsonify({'result' : user_to_remove})
            except:
                return jsonify({'result' : 500})


class DbRead(Resource):
    # DB READ API
    def post(self):
        allDetails = request.get_json(force=True)

        collection = allDetails['collection']
        if collection == 'user':
            collection = userdb.user
        else:
            collection = ridedb.ride

        method = allDetails['method']
        details = allDetails['details']

        if method == "readOne":
            query = collection.find_one(details) # details has ('username':username)
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