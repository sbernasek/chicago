

def includes_date(records, date):
    indices = (records.START <= date) & (records.END >= date)
    return records[indices]

def spans_daterange(records, first_date, last_date):
    indices = (records.START <= last_date) & (records.END >= first_date)
    return records[indices]

def starts_within_daterange(records, first_date, last_date):
    indices = records.START.between(first_date, last_date)
    return records[indices]

def end_within_daterange(records, first_date, last_date):
    indices = records.END.between(first_date, last_date)
    return records[indices]

def build_timeseries(selector, data, bins, groupby='ZIP'):
    within_bin = {}
    for i in range(bins.size-1):
        start, stop = bins[i:i+2]
        within_bin[start] = selector(data, start, stop).groupby(groupby)[groupby].count()
    df = pd.DataFrame(within_bin).T
    df[df.isna()] = 0
    return df


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
from modules.io import read_json, write_json
from modules.dynamics import *
from matplotlib.lines import Line2D
red_line = Line2D([], [], color='r', lw=3, label='60622')
