from flask import Flask
from flask import request
from datetime import datetime
import data_utils as du
from flask_cors import CORS
import numpy as np
import pandas as pd
from service_state import sState

app = Flask(__name__)
CORS(app)

state = sState()

try:
    state.df = pd.read_csv(state.log_path, index_col=0)
    if state.df.empty:
        raise FileNotFoundError()

    oldlen = len(state.df)
    state.df = du.obliterate_long_delta(state.df, state.thresh_seconds)
    if len(state.df) is not oldlen:
        state.df.to_csv(state.log_path, encoding='utf-8')

    for i in range(state.num_plants):
        strplc = i+1 if i != 0 else ""
        filtered_df = state.df[['time', 'moisture{s}'.format(s=strplc)]]
        state.moist_datas.append(filtered_df.rename(columns={'moisture{s}'.format(s=strplc): 'value'}).to_dict(orient='records'))

    filtered_df = state.df[['time', 'sunlight']]
    state.sun_data = filtered_df.rename(columns={'sunlight': 'value'}).to_dict(orient='records')

except FileNotFoundError:

    for i in range(state.num_plants):
        state.moist_datas.append([{"time": state.sse, "value": 0}])
    state.sun_data = [{"time": state.sse, "value": 0}]


def write_to_global_data(mls, sun):
    global state

    state.cdt = datetime.now()
    state.sse = int(state.cdt.timestamp())

    state.dict_list.append([state.sse] + mls + [sun])
    
    if len(state.dict_list) >= state.smooth_interval:
        state.smooth()
    
    if len(state.df) > state.max_points:
        state.df.drop(index=0)

    if (state.sse - state.lw_time) >= state.write_interval:
        state.lw_time = state.sse
        state.df.to_csv(state.log_path, encoding='utf-8')

    state.moist_datas = []
    for i in range(state.num_plants):
        strplc = i+1 if i != 0 else ""
        filtered_df = state.df[['time', 'moisture{s}'.format(s=strplc)]]
        state.moist_datas.append(filtered_df.rename(columns={'moisture{s}'.format(s=strplc): 'value'}).to_dict(orient='records'))

    filtered_df = state.df[['time', 'sunlight']]
    state.sun_data = filtered_df.rename(columns={'sunlight': 'value'}).to_dict(orient='records')

    for i, moist_data in enumerate(state.moist_datas):
        if len(moist_data) > state.max_points:
            state.moist_datas[i].pop(0)
    if len(state.sun_data) > state.max_points:
        state.sun_data.pop(0)

def check_activation():
    global state
    total = 0
    seconds = []

    lms = [float(moist_data[len(moist_data)-1]['value']) for moist_data in state.moist_datas]

    for i, lm in enumerate(lms):
        if lm <state.dry_threshold: 
            total += 2**i
            seconds.append(state.dry_threshold-lm)

    return str(total)+","+str(seconds).replace("[", "").replace("]", "").replace(" ", "")

@app.route("/", methods=['POST'])
def display_message():
    data = request.data
    print(data)


@app.route("/get_moisture", methods=['GET'])
def get_moisture():
    global state
    return state.moist_datas


@app.route("/get_sunlight", methods=['GET'])
def get_sunlight():
    global state
    return state.sun_data


@app.route("/get_data", methods=['GET'])
def get_data():

    global state
    state.cdt = datetime.now()
    state.sse = int(state.cdt.timestamp())

    received_data = request.args.get('query')

    print(received_data)
    received_data = received_data.split(" ")

    # if state.sse-state.ll_time >= state.sample_interval:
    try:
        state.ll_time = state.sse
        write_to_global_data(received_data[0:state.num_plants], received_data[state.num_plants])
    except IndexError:
        return "NT"
    return "WR"
    # else:
    #     return "WT"

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
