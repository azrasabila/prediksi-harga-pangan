import os
import requests
import pandas as pd
import numpy as np
from prophet import Prophet
import json


def get_data():
    url = 'http://dev.priangan.org/api/api/graphic_data/2/1/day/price/2012-01-01/2021-2-15/0/city/-/eceran/null'
    res = requests.get(url)
    data = res.json()
    return data


def mean_abs_perc_err(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
