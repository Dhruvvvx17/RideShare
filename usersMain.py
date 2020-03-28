from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
import requests

app = Flask(__name__)
api = Api(app)

app.config['MONGO_DBNAME'] = 'users'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(app)

class AddUser(Resource):
    
    # API 1
    def put(self):

        username = request.json['username']
        password = request.json['password']
        details = {'username' : username, 'password' : password, 'apiNo' : 1}
        uri = 'http://127.0.0.1:5000/DbWrite'

        dbResponse = requests.post(uri,data=json.dumps(details)) #data is a JSON
        #dbResponse contains response code eg 200 OK
        print(dbResponse.json())
        return dbResponse.json()

   # Temp api to list all users
    def get(self):
        user = mongo.db.user
        output = []
        for q in user.find():
            output.append({'username':q['username'],'password':q['password']})
        return {'result':output}


class RemUser(Resource):

    #API 2
    def delete(self,username):
        user = mongo.db.user
        q = user.find_one({'username':username})
        if q:
            user.delete_one({'_id':q['_id']})
            output = 'Deleted Successfully!'
        else:
            output = 'ERROR! RETURN APPROPRIATE ERROR CODE!!'
        return output

class DbWrite(Resource):
    def post(self):
        details = request.get_json(force=True)
        apiNo = details['apiNo']
        if apiNo == 1:
            username = details['username']
            password = details['password']
            user = mongo.db.user 
            user_id = user.insert({'username' : username, 'password' : password})
            new_user = user.find_one({'_id' : user_id})
            output = {'username' : new_user['username'], 'password' : new_user['password']}
            return jsonify(output)

# class DbRead(Resource):
#     def get(self):        #NEED TO CHECK IF GET OR POST
        


api.add_resource(AddUser,'/users')
api.add_resource(RemUser,'/users/<username>')
api.add_resource(DbWrite,'/DbWrite')
# api.add_resource(DbRead,'/DbRead')

if __name__ == '__main__':
    app.run(debug=True)
