import pandas as pd
import numpy as np
from datetime import datetime

class sState:
    def __init__(self, nil=0):
        self.log_path = "./log.csv"
        self.lw_time = nil
        self.ll_time = nil

        self.thresh_seconds = 3600 # Obliterate time deltas longer than this
        self.num_plants = 3
        self.smooth_interval = 20 # Num samples needed to smooth

        self.cdt = datetime.now()
        self.sse = int(self.cdt.timestamp())
        self.sample_interval = 60 # How often we look at arduino data
        self.max_points = 4096
        self.dry_threshold = 25.0
        self.write_interval = 1800  # How often data gets written to drive
        
        ms = ['moisture'] + ["moisture{}".format(str(i+2)) for i in range(self.num_plants-1)]
        self.df = pd.DataFrame(columns=['time'] + ms + ['sunlight'])
        self.df.loc[0] = [self.sse, 0.0, 0.0, 0.0, 0.0]

        self.dict_list = []

        self.moist_datas = []
        self.sun_data = []

    def smooth(self):
        if not self.dict_list or self.dict_list is None or self.dict_list == []: return

        cols = self.df.columns.tolist()

        averages = []
        for i in range(len(cols)):
            to_avg = []
            for j in range(self.smooth_interval):
                to_avg.append(float(self.dict_list[j][i]))
            averages.append(np.mean(to_avg))

        self.df.loc[len(self.df)] = averages
        self.dict_list = []
