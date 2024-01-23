from datetime import datetime
import numpy as np
import pandas as pd

def obliterate_long_delta(df, maxdelta):
    
    if df.empty: return df
    modded_df = df
    time_list = df['time'].tolist()
    last_time = time_list[0]

    longest_delta = 0

    for idx, time in enumerate(time_list):

        newdelta = time-last_time
        if newdelta > longest_delta:
            longest_delta = newdelta
        if  newdelta>= maxdelta:
            modded_df=df.drop(index=range(idx))
        last_time = time
    print("Longest Delta: {delta}".format(delta=longest_delta))

    return modded_df
