from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from constants import locations
from bson.objectid import ObjectId
import requests
from pymongo import MongoClient
from flask import Response

app = Flask(__name__)
api = Api(app)

ridedb = MongoClient('mongodb://ridedb:27017/').rides
userdb = MongoClient('mongodb://userdb:27017/').users

# # for accessing the users DB
# uriUsersWrite = 'http://users:8080/users/DbWrite'
# uriUsersRead = 'http://users:8080/users/DbRead'

# for accessing the rides DB
uriWrite = 'http://rides:8000/rides/DbWrite'
uriRead = 'http://rides:8000/rides/DbRead'


def insertHelp(allDetails):
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse 

def readHelp(allDetails):
    dbResponse = requests.post(uriRead,data=json.dumps(allDetails))
    return dbResponse # contains either {'result':0} or {'result':1, query}


def deleteHelp(allDetails):
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse


class GlobalRidesAPI(Resource):
    # MAIN API 3 - CREATE RIDE
    def post(self):
        try:
            user = userdb.user # user here is a Object of type collection, which isn't JSON serializable
            ride = ridedb.ride
            try:
                created_by = request.json['created_by']
                timestamp = request.json['timestamp']
                source = request.json['source']
                destination = request.json['destination']
            except:
                return Response("Invalid Input JSON",status=400,mimetype='application/json')
            details = {'username':created_by}
            allDetails = {'details':details, 'method':'readOne', 'collection': 'user'}
            dbResponse = readHelp(allDetails) # contains either {'result':0} or {'result':1, query}
            if dbResponse.json()["result"] == 0:
                return Response("User doesn't exists!",status=400,mimetype='application/json')
            if(source in locations.keys() and destination in locations.keys()):
                details = {'created_by': created_by, 'timestamp': timestamp, 'source':source,'destination':destination}
                allDetails = {'details':details, 'method':'insert', 'collection':'ride', 'users':[]}
                dbResponse = insertHelp(allDetails)
                if dbResponse.json()['result'] == 201:
                    return Response("{}", status=201, mimetype="application/json")
                else:
                    return Response("",status=500,mimetype='application/json')
            else:
                return Response("Invalid source or destination",status=400,mimetype='application/json')
        except:
            return Response("",status=500,mimetype='application/json')

    # MAIN API 4 - LIST RIDE FOR GIVEN SOURCE & DESTINATION
    def get(self):
        try:
            source = request.args.get('source')
            destination = request.args.get('destination')
        except: 
            return Response("Invalid Input JSON",status=400,mimetype='application/json')
        details = {'source': int(source), 'destination': int(destination)}
        allDetails = {'details':details,'method':'readMany', 'collection':'ride'}
        dbResponse = readHelp(allDetails)
        if dbResponse.json()['result']==1:
            listOfRides = dbResponse.json()['query']
            # a = len(listOfRides)
            return Response(listOfRides, status=200, mimetype='application/json')
        else:
            return Response('[]', status=204, mimetype='application/json')

        
        # uri = 'http://rides:8000/rides/DbRead'
        # dbResponse = requests.post(uri,data=json.dumps(details)).json()
        # return dbResponse

class SpecificRidesAPI(Resource):
    # MAIN API 5 - GET INFO ABOUT A SPECIFIC RIDE
    def get(self,rideID):
        if(len(str(rideID))!=24):
            return "Invalid ride ID"
        details = {'_id':rideID, 'apiNo': 5}
        uri = 'http://rides:8000/rides/DbRead'
        dbResponse = requests.post(uri,data=json.dumps(details)).json()
        return dbResponse

    # MAIN API 6 - JOIN AN EXISTING RIDE
    def post(self,rideID):
        if(len(str(rideID))!=24):
            return "Invalid ride ID"
        username = request.json['username'] # Username of the user who is trying to join the ride
        user = userdb.user
        exists = user.find_one({'username':username})
        if not exists:
            return "User does not exists"
        details = {'username':username,'rideID':rideID,'apiNo': 6}
        uri = 'http://rides:8000/rides/DbRead'
        dbResponse = requests.post(uri,data=json.dumps(details)).json()
        return dbResponse

    # MAIN API 7 - DELETE A RIDE
    def delete(self,rideID):
        ride = ridedb.ride
        details = {'_id':rideID,'apiNo':7}
        uri = 'http://rides:8000/rides/DbRead'
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
        
        allDetails = request.get_json(force=True)
        
        collection = allDetails['collection'] # either 'user' or 'ride'
        if collection == 'user':
            collection = userdb.user
        else:
            collection = ridedb.ride
        method = allDetails['method']
        if method == 'insert':
            try:
                collection.insert(allDetails['details']) # details -> all ride details
                return jsonify({'result' : 201})
            except:
                return jsonify({'result' : 500})

class DbRead(Resource):
    def post(self):
        
        allDetails = request.get_json(force=True)
        collection = allDetails['collection'] # either 'user' or 'ride'
        if collection == 'user':
            collection = userdb.user
        else:
            collection = ridedb.ride
        method = allDetails['method']
        if method == 'readOne':
            query = collection.find_one(allDetails['details']) # details has ('username':username)
            if query:
                # query = jsonify(query)
                query['_id'] = str(query['_id'])
                return jsonify({'result':1,'query':query})  # already existing user
            else: # when query contains null
                return jsonify({"result":0}) # user does not exist
        
        if method == 'readMany':
            query = collection.find(allDetails['details'])
            if (query.count() > 0):
                listOfRides = []
                for q in query:
                    q['_id'] = str(q['_id'])
                    listOfRides.append(q)
                listOfRides = json.dumps(listOfRides)    
                return jsonify({'result':1,'query':listOfRides}) # query is being returned as a list
            else: # when query contains null
                return jsonify({"result":0}) # no ride with that path exists
            
        
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
    app.run(host="0.0.0.0", port=8000, debug=True)
