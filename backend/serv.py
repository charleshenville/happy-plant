from flask import Flask
from flask import request
from datetime import datetime
from flask_cors import CORS
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

log_path = "./log.csv"
lw_time = 0
cdt = datetime.now()
sse = int(cdt.timestamp())
max_points = 4096
dry_threshold = 25.0
write_interval = 1800  # How often data gets written to drive

df = pd.DataFrame(columns=['time', 'moisture',
                  'moisture2', 'moisture3', 'sunlight'])
df.loc[0] = [sse, 0.0, 0.0, 0.0, 0.0]

try:
    df = pd.read_csv(log_path, index_col=0)
    if df.empty:
        raise FileNotFoundError()

    filtered_df = df[['time', 'moisture']]
    moist_data = filtered_df.rename(columns={'moisture': 'value'}).to_dict(orient='records')

    filtered_df = df[['time', 'moisture2']]
    moist_data_2 = filtered_df.rename(columns={'moisture2': 'value'}).to_dict(orient='records')

    filtered_df = df[['time', 'moisture3']]
    moist_data_3 = filtered_df.rename(columns={'moisture3': 'value'}).to_dict(orient='records')

    filtered_df = df[['time', 'sunlight']]
    sunlight_data = filtered_df.rename(columns={'sunlight': 'value'}).to_dict(orient='records')
except FileNotFoundError:
    moist_data = [{"time": sse, "value": 0}]
    moist_data_2 = [{"time": sse, "value": 0}]
    moist_data_3 = [{"time": sse, "value": 0}]
    sun_data = [{"time": sse, "value": 0}]


def write_to_global_data(moist, moist2, moist3, sun):
    global moist_data, moist_data_2, moist_data_3, sun_data, cdt, max_points, lw_time

    cdt = datetime.now()
    sse = int(cdt.timestamp())

    new_idx = len(df)
    df.loc[new_idx] = [sse, moist, moist2, moist3, sun]
    if len(df) > max_points:
        df.drop(index=0)

    if (sse - lw_time) >= write_interval:
        lw_time = sse
        df.to_csv(log_path, encoding='utf-8')
        filtered_df = df[['time', 'moisture']]
        moist_data = filtered_df.rename(columns={'moisture': 'value'}).to_dict(orient='records')
        filtered_df = df[['time', 'moisture2']]
        moist_data_2 = filtered_df.rename(columns={'moisture2': 'value'}).to_dict(orient='records')
        filtered_df = df[['time', 'moisture3']]
        moist_data_3 = filtered_df.rename(columns={'moisture3': 'value'}).to_dict(orient='records')
        filtered_df = df[['time', 'sunlight']]
        sun_data = filtered_df.rename(columns={'sunlight': 'value'}).to_dict(orient='records')
    else:
        moist_data.append({"time": sse, "value": moist})
        moist_data_2.append({"time": sse, "value": moist2})
        moist_data_3.append({"time": sse, "value": moist3})
        sun_data.append({"time": sse, "value": sun})

    if len(moist_data) > max_points:
        moist_data.pop(0)
    if len(moist_data_2) > max_points:
        moist_data_2.pop(0)
    if len(moist_data_3) > max_points:
        moist_data_3.pop(0)
    if len(sun_data) > max_points:
        sun_data.pop(0)


def check_activation():
    global moist_data, moist_data_2, moist_data_3
    total = 0
    seconds = 0
    seconds2 = 0

    lm = float(moist_data[len(moist_data)-1]['value'])
    lm2 = float(moist_data_2[len(moist_data_2)-1]['value'])
    lm3 = float(moist_data_3[len(moist_data_3)-1]['value'])

    if lm <dry_threshold: 
        total += 1
        seconds = dry_threshold-lm
    if lm2 <dry_threshold: 
        total += 2
        seconds2 = dry_threshold-lm2
    if lm3 <dry_threshold: 
        total += 4
        seconds3 = dry_threshold-lm3

    return str(total)+","+str(seconds)+","+str(seconds2)+","+str(seconds3)


@app.route("/", methods=['POST'])
def display_message():
    data = request.data
    print(data)


@app.route("/get_moisture", methods=['GET'])
def get_moisture():
    global moist_data, moist_data_2, moist_data_3
    return [moist_data, moist_data_2, moist_data_3]


@app.route("/get_sunlight", methods=['GET'])
def get_sunlight():
    global sun_data
    return sun_data


@app.route("/get_data", methods=['GET'])
def get_data():

    received_data = request.args.get('query')

    print(received_data)
    received_data = received_data.split(" ")

    try:
        write_to_global_data(
            received_data[0], received_data[1], received_data[2], received_data[3])
    except IndexError:
        return "F"
    return "T"


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
