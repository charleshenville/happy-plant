from flask import Flask
from flask import request
from datetime import datetime
import data_utils as du
from flask_cors import CORS
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

log_path = "./log.csv"
lw_time = 0
ll_time = 0

thresh_seconds = 3600 # Obliterate time deltas longer than this
num_plants = 3

cdt = datetime.now()
sse = int(cdt.timestamp())
sample_interval = 60 # How often we look at arduino data
max_points = 4096
dry_threshold = 25.0
write_interval = 1800  # How often data gets written to drive

df = pd.DataFrame(columns=['time', 'moisture',
                  'moisture2', 'moisture3', 'sunlight'])
df.loc[0] = [sse, 0.0, 0.0, 0.0, 0.0]

moist_datas = []

try:
    df = pd.read_csv(log_path, index_col=0)
    if df.empty:
        raise FileNotFoundError()

    oldlen = len(df)
    df = du.obliterate_long_delta(df, thresh_seconds)
    if len(df) is not oldlen:
        df.to_csv(log_path, encoding='utf-8')

    for i in range(num_plants):
        strplc = i+1 if i is not 0 else ""
        filtered_df = df[['time', 'moisture{s}'.format(s=strplc)]]
        moist_datas.append(filtered_df.rename(columns={'moisture{s}'.format(s=strplc): 'value'}).to_dict(orient='records'))

    filtered_df = df[['time', 'sunlight']]
    sun_data = filtered_df.rename(columns={'sunlight': 'value'}).to_dict(orient='records')

except FileNotFoundError:

    for i in range(num_plants):
        moist_datas.append([{"time": sse, "value": 0}])
    sun_data = [{"time": sse, "value": 0}]


def write_to_global_data(mls, moist, moist2, moist3, sun):
    global moist_datas, sun_data, cdt, max_points, lw_time

    cdt = datetime.now()
    sse = int(cdt.timestamp())

    new_idx = len(df)
    df.loc[new_idx] = [sse] + mls + [sun]
    
    if len(df) > max_points:
        df.drop(index=0)

    if (sse - lw_time) >= write_interval:
        lw_time = sse
        df.to_csv(log_path, encoding='utf-8')

        for i in range(num_plants):
            strplc = i+1 if i is not 0 else ""
            filtered_df = df[['time', 'moisture{s}'.format(s=strplc)]]
            moist_datas.append(filtered_df.rename(columns={'moisture{s}'.format(s=strplc): 'value'}).to_dict(orient='records'))

        filtered_df = df[['time', 'sunlight']]
        sun_data = filtered_df.rename(columns={'sunlight': 'value'}).to_dict(orient='records')
    else:
        for i, ml in enumerate(mls):
            moist_datas[i].append({"time": sse, "value": ml})
        sun_data.append({"time": sse, "value": sun})

    for i, moist_data in enumerate(moist_datas):
        if len(moist_data) > max_points:
            moist_datas[i].pop(0)
    if len(sun_data) > max_points:
        sun_data.pop(0)

def check_activation():
    global moist_datas
    total = 0
    seconds = []

    lms = [float(moist_data[len(moist_data)-1]['value']) for moist_data in moist_datas]

    for i, lm in enumerate(lms):
        if lm <dry_threshold: 
            total += 2**i
            seconds.append(dry_threshold-lm)

    return str(total)+","+str(seconds).replace("[", "").replace("]", "")

@app.route("/", methods=['POST'])
def display_message():
    data = request.data
    print(data)


@app.route("/get_moisture", methods=['GET'])
def get_moisture():
    global moist_datas
    return moist_datas


@app.route("/get_sunlight", methods=['GET'])
def get_sunlight():
    global sun_data
    return sun_data


@app.route("/get_data", methods=['GET'])
def get_data():

    global ll_time
    cdt = datetime.now()
    sse = int(cdt.timestamp())

    received_data = request.args.get('query')

    print(received_data)
    received_data = received_data.split(" ")

    if sse-ll_time >= sample_interval:
        try:
            ll_time = sse
            write_to_global_data(received_data[0], received_data[1], received_data[2], received_data[3])
        except IndexError:
            return "NT"
        return "WR"
    else:
        return "WT"

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
