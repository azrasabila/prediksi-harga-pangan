import os
import requests
import pandas as pd
import numpy as np
from prophet import Prophet
import json
from datetime import date


def get_data(id_komoditas):
    today = date.today()
    url = 'http://dev.priangan.org/api/api/graphic_data/' + str(id_komoditas) + \
        '/1/day/price/2009-01-01/' + \
        str(today.strftime("%Y-%m-%d")) + '/0/city/-/eceran/null'
    res = requests.get(url)
    data = res.json()
    return data


def mean_abs_perc_err(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
