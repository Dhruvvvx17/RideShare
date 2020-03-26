from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from constants import locations

app = Flask(__name__)
api = Api(app)

app.config['MONGO_DBNAME'] = 'rides'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/rides'

mongo = PyMongo(app)

class AddRide(Resource):

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

api.add_resource(AddRide,'/rides')
# api.add_resource(AddRide,'/rides?source=<source>&destination=<destination>')

if __name__ == '__main__':
    app.run(debug=True)
