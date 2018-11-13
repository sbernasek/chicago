import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr



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

def evaluate_correlation(X, Y, offset=0, freq='1Y'):
    window = X.index.shift(offset, freq)
    available = window <= Y.index.max()
    Y = Y.loc[window[available], :]
    R, pval = pearsonr(X[available].values.flatten(), Y.values.flatten())
    return R, pval

def evaluate_correlation_individual(X, Y, offset=0):
    window = X.index.shift(offset)
    available = window <= Y.index.max()
    Y = Y.loc[window[available], :]

    xx, yy = X[available], Y

    adict = {}
    for i, (xrow, yrow) in enumerate(zip(xx.values.T, yy.values.T)):
        adict[xx.columns[i]] = pearsonr(xrow, yrow)
    df = pd.DataFrame.from_dict(adict, orient='index', columns=['R', 'P'])


    bonferoni = 0.05 / len(df)

    false_positive_rate = 0.1
    ind = (df.P <= (false_positive_rate * df.P.argsort() / len(df)))
    bh_threshold = df.P[ind].max()


    df['bonferoni'] = df.P <= bonferoni
    df['benjamini_hochberg'] = df.P <= bh_threshold

    return df, bonferoni,  bh_threshold
