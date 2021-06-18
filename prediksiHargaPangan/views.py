from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
from prophet import Prophet
import json
import time
from django import forms
from django.http import HttpResponseRedirect

from prediksiHargaPangan.services import *
from .models import *


def index(request):

    komoditas = Komoditas.objects.all()
    context = {
        'komoditas': komoditas,
    }
    if request.method == 'POST':
        context['id_foreign'] = request.POST['id_foreign']

    return render(request, "index.html", context)


def dashboard(request):
    return render(request, "dashboard/index.html", {})


def prediksi(request, id_foreign):
    # ambil data dari services
    data = get_data(id_foreign)
    # ambil result
    df = data['data'][0]['result']
    commodity_name = data['data'][0]['commodity_name']
    # convert ke dataframe
    df = pd.DataFrame(df, columns=['value', 'time', 'date', 'span'])
    # data preprocessing
    df.drop(['time', 'span'], axis=1, inplace=True)
    df.columns = ['y', 'ds']
    # ubah index jadi tanggal dengan format datetime
    df.ds = pd.to_datetime(df.ds)
    df.index = pd.to_datetime(df.ds)
    df.y = df['y'].astype(np.int64)
    # drop nilai 0 kalo pake MAPE
    df = drop_zero(df)
    # bikin nilai carrying capacity
    df['cap'] = df['y'].mean()
    # split data training dan testing 80:20
    df_train = df[:int(df.shape[0]*0.8)]
    df_test = df[int(df.shape[0]*0.8):]
    # resampling = fill tanggal yang ke skip
    df_train = df_train.resample('D').pad()
    df_train['ds'] = df_train.index
    # fitting model
    m = Prophet(growth='logistic')
    m.add_country_holidays(country_name='ID')
    m.fit(df_train)
    # bikin prediksi dari model yang udah dibuat
    forecast = m.predict(df_test)
    # itung MAPE
    mape = mean_abs_perc_err(y_true=np.asarray(
        df_test['y']), y_pred=np.asarray(forecast['yhat']))
    # itung rmse
    rmse = root_mean_square_err(y_true=np.asarray(
        df_test['y']), y_pred=np.asarray(forecast['yhat']))
    # convert ke JSON
    # data_json = {forecast['ds'].dt.strftime(
    #    '%Y-%m-%d'), forecast['yhat'], forecast['yhat_upper'], forecast['yhat_lower']}.to_json(orient='records')
    data_json = forecast[['ds', 'yhat', 'yhat_upper',
                          'yhat_lower']].to_json(orient='records', date_format='iso', double_precision=0)
    print(data_json)
    yhat = forecast['yhat'].to_json(orient='records')
    yhat_lower = forecast['yhat_lower'].to_json(orient='records')
    yhat_upper = forecast['yhat_upper'].to_json(orient='records')
    data_json = json.loads(data_json)
    # masukin data ke object
    labels = forecast['ds'].dt.strftime('%Y-%m-%d').to_json(orient='records')
    #labels = time.ctime(labels)
    #labels = json.loads(json_data)
    #data = []
    # labels.append(forecast[['ds']])
    # data.append(forecast[['yhat']])
    context = {
        "data": data_json,
        'yhat': yhat,
        "yhat_lower": yhat_lower,
        "yhat_upper": yhat_upper,
        'df': df,
        'df_train': df_train,
        'df_test': df_test,
        'forecast': forecast[['ds', 'yhat']],
        'labels': labels,
        'commodity_name': commodity_name,
        'mape': mape,
        'akurasi': 100-mape,
        'rmse': rmse
    }
    return render(request, "prediksi/index.html", context)
