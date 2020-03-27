from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from constants import locations
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)

app.config['MONGO_DBNAME'] = 'rides'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/rides'

mongo = PyMongo(app)

class Add_or_GetRide(Resource):

    def post(self):
        ride = mongo.db.ride
        created_by = request.json['created_by'] 
        timestamp = request.json['timestamp']
        source = request.json['source'] 
        destination = request.json['destination']
        if(source in locations.keys() and destination in locations.keys()):
            ride_id = ride.insert({'created_by': created_by, 'timestamp': timestamp, 'source':source,'destination':destination})
            new_ride = ride.find_one({'_id':ride_id})
            output = {'created_by':new_ride['created_by'], 'timestamp':new_ride['timestamp'], 'source':new_ride['source'], 'destination':new_ride['destination']}
            return output        
        else:
            return "Invalid source or destination"

    def get(self):
        ride = mongo.db.ride
        source = request.args.get('source')
        destination = request.args.get('destination')
        print(source,destination)
        output = []
        for query in ride.find({'source': int(source), 'destination': int(destination)}):
            output.append({'rideID':str(query['_id']),'created_by':query['created_by'],'timestamp':query['timestamp']})

        return {"result":output}


class GetSpecificRide(Resource):

    def get(self,rideID):
        ride = mongo.db.ride
        print(str(rideID))
        if(len(str(rideID))!=24):
            return "Invalid ride ID"
        query = ride.find_one({'_id': ObjectId(rideID)})
        if query:
            output = {}
            output['_id'] = str(query['_id'])
            output['created_by'] = query['created_by']
            output['timestamp'] = query['timestamp']
            output['source'] = query['source']
            output['destination'] = query['destination']
            return output
        else:
            return "No such ride exists"

class DbWrite(Resource):
    def post:

class DbRead(Resource):
    def get:

api.add_resource(Add_or_GetRide,'/rides')
api.add_resource(GetSpecificRide,'/rides/<rideID>')
api.add_resource(Add_or_GetRide,'/DbWrite')
api.add_resource(Add_or_GetRide,'/DbRead')

if __name__ == '__main__':
    app.run(debug=True)
