from datetime import datetime
import numpy as np
import pandas as pd

def obliterate_long_delta(df, maxdelta):
    
    if df.empty: return df
    modded_df = df
    time_list = df['time'].tolist()
    last_time = time_list[0]
    for idx, time in enumerate(time_list):
        if time-last_time >= maxdelta:
            modded_df=df.drop(index=range(idx))
        last_time = time

    return modded_df
