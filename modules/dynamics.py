from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt


def normalize_by_baseline(timeseries, baseline_length=4):
    baseline = timeseries.iloc[:baseline_length].mean(axis=0)
    normalized_timeseries = np.log2(timeseries / baseline)
    normalized_timeseries = normalized_timeseries.iloc[baseline_length:, :]
    return normalized_timeseries

def detrend(timeseries):
    trend = timeseries.mean(axis=1)
    return timeseries.subtract(trend, axis=0)

def ptp(timeseries):
    return timeseries.max(axis=0) - timeseries.min(axis=0)

def differentiate(timeseries, window_size=3, polyorder=1):
    return timeseries.diff(axis=0, periods=1).apply(savgol_filter, axis=0, args=(window_size, polyorder))

def plot_timeseries(timeseries):
    fig, ax = plt.subplots()
    timeseries.plot(ax=ax, legend=False, color='k', lw=0.2)
    return ax
