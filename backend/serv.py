from flask import Flask
from flask import request
import json
from datetime import datetime
import time
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

moist_data=[]
moist_data_2=[]
sun_data=[]
cdt = 0

def write_to_global_data(moist, moist2, sun):
    global moist_data, moist_data_2, sun_data, cdt

    cdt = datetime.now()
    sse = int(cdt.timestamp())

    moist_data.append({"time": sse, "value": moist})
    moist_data_2.append({"time": sse, "value": moist2})
    sun_data.append({"time": sse, "value": sun})

    if len(moist_data) > 100:
        moist_data.pop(0)
    if len(moist_data_2) > 100:
        moist_data_2.pop(0)
    if len(sun_data) > 100:
        sun_data.pop(0)

def check_activation():
    global moist_data
    total=0
    seconds=0
    seconds2=0

    if moist_data[len(moist_data)-1]['value']<=30: 
        total+=1
        seconds=30-moist_data[len(moist_data)-1]
    if moist_data_2[len(moist_data)-1]['value']<=30: 
        total+=2
        seconds=30-moist_data_2[len(moist_data_2)-1]

    return str(total)+","+str(seconds)+","+str(seconds2)

@app.route("/", methods=['POST'])
def display_message():
    data = request.data
    print(data)

@app.route("/get_moisture", methods=['GET'])
def get_moisture():
    global moist_data, moist_data_2
    return [moist_data, moist_data_2]

@app.route("/get_sunlight", methods=['GET'])
def get_sunlight():
    global sun_data
    return sun_data

@app.route("/get_data", methods=['GET'])
def get_data():

    received_data = request.args.get('query')
    
    print(received_data)
    received_data = received_data.split(" ") 

    write_to_global_data(received_data[0], received_data[1], received_data[2])
    return "pstd"

@app.route("/get_activation", methods=['GET'])
def get_activation():

    activate = check_activation()
    return activate
"""
@app.route("/post_water", methods=['POST'])
def post_water():
    data = request.data
    return "Hello World!"

@app.route("/post_state", methods=['POST'])
def post_state():
    data = request.data
    return "Hello World!"
"""


###
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) 
