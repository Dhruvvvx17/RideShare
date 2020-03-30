from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from constants import locations
from bson.objectid import ObjectId
import requests

app = Flask(__name__)
api = Api(app)

app.config['MONGO_DBNAME'] = 'rides'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/rides'
# UserDB used in API 4
userDB = PyMongo(app, uri = 'mongodb://localhost:27017/users')

mongo = PyMongo(app)



class GlobalRidesAPI(Resource):
    # MAIN API 3 - CREATE RIDE
    def post(self):
        created_by = request.json['created_by'] 
        timestamp = request.json['timestamp']
        source = request.json['source'] 
        destination = request.json['destination']
        user = userDB.db.user
        exists = user.find_one({'username':created_by})
        if not exists:
            return "User does not exists"
        if(source in locations.keys() and destination in locations.keys()):
            details = {'created_by': created_by, 'timestamp': timestamp, 'source':source,'destination':destination,'apiNo':3}
            uri = 'http://127.0.0.1:5000/rides/DbWrite'
            dbResponse = requests.post(uri,data=json.dumps(details)).json()
            return dbResponse
        else:
            return "Invalid source or destination"

    # MAIN API 4 - LIST RIDE FOR GIVEN SOURCE & DESTINATION
    def get(self):
        source = request.args.get('source')
        destination = request.args.get('destination')
        details = {'source': int(source), 'destination': int(destination), 'apiNo':4}
        uri = 'http://127.0.0.1:5000/rides/DbRead'
        dbResponse = requests.post(uri,data=json.dumps(details)).json()
        return dbResponse

class SpecificRidesAPI(Resource):
    # MAIN API 5 - GET INFO ABOUT A SPECIFIC RIDE
    def get(self,rideID):
        if(len(str(rideID))!=24):
            return "Invalid ride ID"
        details = {'_id':rideID, 'apiNo': 5}
        uri = 'http://127.0.0.1:5000/rides/DbRead'
        dbResponse = requests.post(uri,data=json.dumps(details)).json()
        return dbResponse

    # MAIN API 6 - JOIN AN EXISTING RIDE
    def post(self,rideID):
        if(len(str(rideID))!=24):
            return "Invalid ride ID"
        username = request.json['username'] # Username of the user who is trying to join the ride
        user = userDB.db.user
        exists = user.find_one({'username':username})
        if not exists:
            return "User does not exists"
        details = {'username':username,'rideID':rideID,'apiNo': 6}
        uri = 'http://127.0.0.1:5000/rides/DbRead'
        dbResponse = requests.post(uri,data=json.dumps(details)).json()
        return dbResponse

    # MAIN API 7 - DELETE A RIDE
    def delete(self,rideID):
        ride = mongo.db.ride
        details = {'_id':rideID,'apiNo':7}
        uri = 'http://127.0.0.1:5000/rides/DbRead'
        rid = requests.post(uri,data=json.dumps(details)).json()['_id']
        print(rid)
        if (rid == -1):
            output = "Ride does not exist"
        else:
            ride.delete_one({'_id':ObjectId(rid)})
            output = 'Deleted Successfully!'
        return output

class DbWrite(Resource):
    def post(self):
        ride = mongo.db.ride
        details = request.get_json(force=True)
        apiNo = details['apiNo']
        if apiNo == 3:
            created_by = details['created_by'] 
            timestamp = details['timestamp']
            source = details['source'] 
            destination = details['destination']
            rideID = ride.insert({'created_by':created_by,'timestamp':timestamp,'source':source,'destination':destination,'users':[]})
            new_ride = ride.find_one({'_id':rideID})
            output = {'created_by': new_ride['created_by'], 'timestamp': new_ride['timestamp'], 'source' : new_ride['source'], 'destination' : new_ride['destination'] }
            return jsonify(output) 


class DbRead(Resource):
    def post(self):
        ride = mongo.db.ride
        details = request.get_json(force=True)
        apiNo = details['apiNo']
        if apiNo == 4:
            source = details['source']
            destination = details['destination']
            results = ride.find({'source': source, 'destination': destination})
            print(results)
            output = []
            for row in results:
                output.append({'rideID':str(row['_id']),'created_by':row['created_by'],'timestamp':row['timestamp']})
            return output

        elif apiNo == 5:
            rideID = details['_id']
            query = ride.find_one({'_id': ObjectId(rideID)})
            if query:
                output = {}
                output['_id'] = str(query['_id'])
                output['created_by'] = query['created_by']
                output['timestamp'] = query['timestamp']
                output['source'] = query['source']
                output['destination'] = query['destination']
                output['users'] = query['users']
                return output
            else:
                return "No such ride exists"
  
        elif apiNo == 6:
            rideID = details['rideID']
            username = details['username']
            query = ride.find_one({'_id': ObjectId(rideID)})
            if query:   
                users = query['users']
                users.append(username)
                ride.find_one_and_update({'_id':ObjectId(rideID)},{'$set':{'users':users}},upsert=False)
                return "User Added"
            else:
                return "Ride does not exist"

        elif apiNo == 7:
            rideID = details['_id']
            #rideID is coming in as a string, thus we typecast it to ObjectID to access it
            query = ride.find_one({'_id':ObjectId(rideID)})
            if not query:
                resp = {'_id': -1}
            else:
                resp = {'_id' : str(query['_id'])}
            return jsonify(resp)


api.add_resource(GlobalRidesAPI,'/rides')
api.add_resource(SpecificRidesAPI,'/rides/<rideID>')
api.add_resource(DbWrite,'/rides/DbWrite')
api.add_resource(DbRead,'/rides/DbRead')

if __name__ == '__main__':
    app.run(debug=True)
