import os
import requests
import pandas as pd
import numpy as np
from prophet import Prophet
import json
from datetime import date
from math import sqrt
from sklearn.metrics import mean_squared_error
from django.contrib import messages

from .models import Harga, Komoditas, Wilayah


def get_data(request, id_komoditas):
    today = date.today()
    komoditas = Komoditas.objects.get(ID_FOREIGN_KOMODITAS=id_komoditas)
    wilayah = Wilayah.objects.get(ID_FOREIGN_WILAYAH=1)
    url = 'http://dev.priangan.org/api/api/graphic_data/' + str(id_komoditas) + \
        '/1/day/price/2009-01-01/' + \
        str(today.strftime("%Y-%m-%d")) + '/0/city/-/eceran/null'

    res = requests.get(url)
    data = res.json()
    df = data['data'][0]['result']

    df_db = Harga.objects.filter(
        ID_KOMODITAS=komoditas).values('HARGA', 'TANGGAL')

    df_db = pd.DataFrame.from_dict(df_db)
    df = pd.DataFrame.from_dict(df)

    df = df.drop(['time', 'span'], axis=1)
    df = df.rename(columns={'value': 'HARGA', 'date': 'TANGGAL'})
    df = df.astype({'HARGA': 'int64'})

    if len(df) > len(df_db) and len(df_db) > 0:

        compare = df
        compare['HARGA_DF'] = df_db['HARGA']
        compare = compare[compare['HARGA_DF'].isna()]

        if len(compare) > 0:
            for index, row in compare.iterrows():
                harga = row['HARGA']
                tanggal = row['TANGGAL']
                Harga.objects.create(
                    HARGA=harga,
                    TANGGAL=tanggal,
                    ID_KOMODITAS=komoditas,
                    ID_WILAYAH=wilayah
                )
            messages.success(
                request, "Data terbaru berhasil ditambahkan ke database.")
    elif len(df_db) == 0:
        for index, row in df.iterrows():
            harga = row['HARGA']
            tanggal = row['TANGGAL']
            Harga.objects.create(
                HARGA=harga,
                TANGGAL=tanggal,
                ID_KOMODITAS=komoditas,
                ID_WILAYAH=wilayah
            )
        messages.success(
            request, "Data terbaru berhasil ditambahkan ke database.")
    return data


def mean_abs_perc_err(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def root_mean_square_err(y_true, y_pred):
    return sqrt(mean_squared_error(y_true, y_pred))


def drop_zero(df):
    return df[(df != 0).all(1)]
