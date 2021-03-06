from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from constants import locations
from bson.objectid import ObjectId
import requests
from aws import alb_dns
from pymongo import MongoClient
from flask import Response
import re

app = Flask(__name__)
api = Api(app)

ridedb = MongoClient('mongodb://ridedb:27017/').rides
albPath = alb_dns


# for accessing the rides DB
uriWrite = 'http://rides:8000/rides/DbWrite'
uriRead = 'http://rides:8000/rides/DbRead'


def insertHelp(allDetails):
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse 

def readHelp(allDetails):
    dbResponse = requests.post(uriRead,data=json.dumps(allDetails))
    return dbResponse

def deleteHelp(allDetails):
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse

def modifyHelp(allDetails):
    dbResponse = requests.post(uriWrite,data=json.dumps(allDetails))
    return dbResponse


class GlobalRidesAPI(Resource):
    # MAIN API 3 - CREATE RIDE
    def post(self):
        try:
            try:
                created_by = request.json['created_by']
                timestamp = request.json['timestamp']
                source = request.json['source']
                destination = request.json['destination']
            except:
                return Response("Invalid Input JSON",status=400,mimetype='application/json')

            details = {'username':created_by}
            allDetails = {'details':details, 'method':'readOne', 'collection': 'user'}
            # dbResponse = readHelp(allDetails) # contains either {'result':0} or {'result':1, query}
            dbResponse = requests.post(albPath + "/users/DbRead",data=json.dumps(allDetails))

            if dbResponse.json()["result"] == 0:
                return Response("User doesn't exists!",status=400,mimetype='application/json')

            if not re.match("((0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-[0-9]{4}:[0-5][0-9]-[0-5][0-9]-(2[0-3]|[01][0-9]))",timestamp):
                return Response("Invalid Timestamp!",status=400,mimetype='application/json')

            if(source in locations.keys() and destination in locations.keys()):
                details = {'created_by': created_by, 'timestamp': timestamp, 'source':source,'destination':destination,'users':[]}
                allDetails = {'details':details, 'method':'insert', 'collection':'ride'}
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
                return Response(listOfRides, status=200, mimetype='application/json')
            else:
                return Response("[]", status=204, mimetype='application/json')
        except:
                return Response("", status=500, mimetype='application/json')


class SpecificRidesAPI(Resource):
    # MAIN API 5 - GET INFO ABOUT A SPECIFIC RIDE
    def get(self,rideID):
        try:
            if not (re.match("([a-fA-F0-9]{24})",str(rideID))):
                return Response("Invalid ride ID",400,mimetype='application/json')
        
            details = {'_id':str(rideID)}  # details has "_id" and str(rideId) is "rideID"
            allDetails = {'details':details, 'method':'readOne', 'collection':'ride'}
            dbResponse = readHelp(allDetails)

            if dbResponse.json()['result'] == 1:
                rideDetails = dbResponse.json()['query']
                return Response(rideDetails, status=200, mimetype='application/json')
            else:
                return Response("{}", status=204, mimetype='application/json')
        except:
                return Response('', status=500, mimetype='application/json')


    # MAIN API 6 - JOIN AN EXISTING RIDE
    def post(self,rideID):
        try:
            if not (re.match("([a-fA-F0-9]{24})",str(rideID))):
                return Response("Invalid ride ID",400,mimetype='application/json')

            try:
                username = request.json['username']
            except:
                return Response("Invalid Input JSON",status=400,mimetype='application/json')

            details = {'username':username}
            allDetails = {'details':details, 'method':'readOne', 'collection': 'user'}
            dbResponse = requests.post(albPath + "/users/DbRead",data=json.dumps(allDetails))

            if dbResponse.json()["result"] == 0:
                return Response("User doesn't exists!",status=400,mimetype='application/json')

            details = {'_id':str(rideID)}  # details has "_id" and str(rideId) is "rideID"
            toInsert = {'users':username}
            allDetails = {'details':details, 'toInsert':toInsert, 'method':'modify', 'collection':'ride'}
            dbResponse = modifyHelp(allDetails)

            if dbResponse.json()['result'] == 200:
                return Response("{}", status=200, mimetype="application/json")
            else:
                return Response("",status=500,mimetype='application/json')
        except:
            return Response("",status=500,mimetype='application/json')


    # MAIN API 7 - DELETE A RIDE
    def delete(self,rideID):
        try:
            if not (re.match("([a-fA-F0-9]{24})",str(rideID))):
                    return Response("Invalid ride ID",400,mimetype='application/json')

            details = {'_id':str(rideID)}  # details has "_id" and str(rideId) is "rideID
            allDetails = {'details':details,'method':'readOne','collection':'ride'}
            dbResponse = readHelp(allDetails)
            if dbResponse.json()['result'] == 0:
                return Response("Ride ID doesn't exist",400,mimetype='application/json')

            allDetails = {'details':details,'method':'deleteOne','collection':'ride'}
            dbResponse = deleteHelp(allDetails)
            if dbResponse.json()['result'] == 200:
                return Response("{}", status=200, mimetype="application/json")
            else:
                return Response("",status=500,mimetype='application/json')
        except:
            return Response("",status=500,mimetype='application/json')


class DbWrite(Resource):
    def post(self):
        
        allDetails = request.get_json(force=True)
        
        collection = allDetails['collection'] # either 'user' or 'ride'
        if collection == 'ride':
            collection = ridedb.ride
        # Any other collection other than "ride" should not be accessed in this API.
        else:
            return jsonify({'result' : 500})

        method = allDetails['method']
        details = allDetails['details']
        if '_id' in details:
            details['_id'] = ObjectId(details['_id'])
        
        if method == 'insert':
            try:
                collection.insert(details) # details -> all ride details
                return jsonify({'result' : 201})
            except:
                return jsonify({'result' : 500})

        elif method == 'modify':
            try:
                toInsert = allDetails['toInsert']
                #toinsert = {'users' : username}
                collection.find_one_and_update(details,{'$addToSet' : toInsert})
                return jsonify({'result' : 200})
            except:
                return jsonify({'result' : 500})

        elif method == 'deleteOne':
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
                return jsonify({'result' : 200})
            except:
                return jsonify({'result' : 500})


class DbRead(Resource):
    def post(self):
        
        allDetails = request.get_json(force=True)
        collection = allDetails['collection']
        
        if collection == 'ride':
            collection = ridedb.ride
        # Any other collection other than "ride" should not be accessed in this API.
        else:
            return jsonify({'result' : 500})

        method = allDetails['method']
        details = allDetails['details']
        if '_id' in details:
            temp = details['_id']
            details['_id'] = ObjectId(temp)

        if method == 'readOne':
            query = collection.find_one(details) # details has ('username':username)
            if query:
                query['_id'] = str(query['_id'])
                query = json.dumps(query)
                return jsonify({'result':1,'query':query})  # already existing user
            else: # when query contains null
                return jsonify({"result":0}) # user does not exist
        
        if method == 'readMany':
            query = collection.find(details)
            if (query.count() > 0):
                listOfRides = []
                for q in query:
                    q['_id'] = str(q['_id'])
                    listOfRides.append(q)
                listOfRides = json.dumps(listOfRides)    
                return jsonify({'result':1,'query':listOfRides}) # query is being returned as a list
            else: # when query contains null
                return jsonify({"result":0}) # no ride with that path exists
            
        
api.add_resource(GlobalRidesAPI,'/rides')
api.add_resource(SpecificRidesAPI,'/rides/<rideID>')
api.add_resource(DbWrite,'/rides/DbWrite')
api.add_resource(DbRead,'/rides/DbRead')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
