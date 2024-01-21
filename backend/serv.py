from flask import Flask
from flask import request
import json
from datetime import datetime
import time
import random
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route("/", methods=['POST'])
def display_message():
    data = request.data
    print(data)

@app.route("/get_moisture", methods=['GET'])
def get_moisture():

    data = []
    for x in range(50):
        current_time = datetime.now()
        value = (int(current_time.timestamp()) % 50) + random.randint(-10, 10)
        data.append({"time": x, "value": value})
    
    return data

@app.route("/get_data", methods=['GET'])
def get_data():

    received_data = request.args.get('query')
    
    print(received_data)
    received_data = received_data.split(" ") 

    # Create a response dictionary with both the received and processed data
    #response_data = {
      #  "moist" : received_data[0], 
     #   "sun": received_data[1]
    #}
    print(received_data)
    return str(received_data)
    #print(response_data)
    #return str(response_data)
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
