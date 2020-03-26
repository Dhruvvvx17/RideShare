from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

app.config['MONGO_DBNAME'] = 'users'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(app)

class AddUser(Resource):
    
    def put(self):
        user = mongo.db.user 
        username = request.json['username']
        password = request.json['password']
        user_id = user.insert({'username' : username, 'password' : password})
        new_user = user.find_one({'_id' : user_id})
        output = {'username' : new_user['username'], 'password' : new_user['password']}
        return output


    def get(self):
        user = mongo.db.user
        output = []
        for q in user.find():
            output.append({'username':q['username'],'password':q['password']})
        return {'result':output}


class RemUser(Resource):
    def delete(self,username):
        user = mongo.db.user
        q = user.find_one({'username':username})
        if q:
            user.delete_one({'_id':q['_id']})
            output = 'Deleted Successfully!'
        else:
            output = 'ERROR! RETURN APPROPRIATE ERROR CODE!!'

        return output

api.add_resource(AddUser,'/user')
api.add_resource(RemUser,'/user/<username>')

if __name__ == '__main__':
    app.run(debug=True)
