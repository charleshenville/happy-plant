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
sun_data=[]
cdt = 0

def write_to_global_data(moist, sun):
    global moist_data, sun_data, cdt

    cdt = datetime.now()
    sse = int(cdt.timestamp())

    moist_data.append({"time": sse, "value": moist})
    sun_data.append({"time": sse, "value": sun})

    if len(moist_data) > 100:
        moist_data.pop(0)
    if len(sun_data) > 100:
        sun_data.pop(0)

@app.route("/", methods=['POST'])
def display_message():
    data = request.data
    print(data)

@app.route("/get_moisture", methods=['GET'])
def get_moisture():
    global moist_data
    return moist_data

@app.route("/get_sunlight", methods=['GET'])
def get_sunlight():
    global sun_data
    return sun_data

@app.route("/get_data", methods=['GET'])
def get_data():

    received_data = request.args.get('query')
    
    print(received_data)
    received_data = received_data.split(" ") 

    write_to_global_data(received_data[0], received_data[1])
    return "pstd"
"""
@app.route("/get ")
@app.route("/get_sunlight", methods=['GET'])
def get_sunlight():
    data = request.data
    return "Hello World!"

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
