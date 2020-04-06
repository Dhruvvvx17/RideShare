from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from bson.objectid import ObjectId
import requests
from pymongo import MongoClient

app = Flask(__name__)
#from userflask import app
api = Api(app)

#app.config['MONGO_DBNAME'] = 'users'
#app.config['MONGO_URI'] = 'mongodb://usersdb:27017'

db = MongoClient('mongodb://userdb:27017/').users


class AddUser(Resource):
    # MAIN API 1 - ADD USER
    def put(self):
        username = request.json['username']
        password = request.json['password']
        details = {'username' : username, 'password' : password, 'apiNo' : 1}
        uri = 'http://users:8080/users/DbWrite'
        dbResponse = requests.post(uri,data=json.dumps(details)).json()
        return dbResponse


    # TEMP API 1 - LIST ALL USERS
    def get(self):
        #print("Hello World")
        #return "Hello World"
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
        uri = 'http://users:8080/users/DbRead'
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
        details = request.get_json(force=True)
        apiNo = details['apiNo']
        if apiNo == 1:
            username = details['username']
            password = details['password']
            user_id = user.insert({'username' : username, 'password' : password})
            new_user = user.find_one({'_id' : user_id})
            output = {'username' : new_user['username'], 'password' : new_user['password']}
            print(output)
            return jsonify(output)


class DbRead(Resource):
    # DB READ API
    def post(self):
        user = db.user
        details = request.get_json(force=True)
        apiNo = details['apiNo']
        if apiNo == 2:
            username = details['username']
            query = user.find_one({'username':username})
            if not query:
                resp = {'_id': -1}
            else:
                resp = {'_id' : str(query['_id'])}
            return jsonify(resp)


api.add_resource(AddUser,'/users')
api.add_resource(RemUser,'/users/<username>')
api.add_resource(DbWrite,'/users/DbWrite')
api.add_resource(DbRead,'/users/DbRead')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
