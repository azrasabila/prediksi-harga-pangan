from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
from prophet import Prophet
import json
import time
from datetime import date, timedelta
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from prediksiHargaPangan.services import *
from .models import *
from .forms import CommodityForm


def index(request):
    commodityForm = CommodityForm()
    context = {
        'commodityForm': commodityForm
    }

    if request.method == 'POST':
        context['id_foreign'] = request.POST['pilih_komoditas']
        return redirect('/prediksi/' + request.POST['pilih_komoditas'], )

    return render(request, "index.html", context)


def dashboard(request):
    return render(request, "dashboard/index.html", {})


def prediksi(request, id_foreign):
    commodityForm = CommodityForm()
    now = date.today()
    print(now)
    print(now+timedelta(1))
    # ambil data dari services
    df = get_data(request, id_foreign)
    commodity_name = df['data'][0]['commodity_name']
    df = df['data'][0]['result']
    df = pd.DataFrame(df, columns=['value', 'date'])
    df.columns = ['y', 'ds']
    # ubah index jadi tanggal dengan format datetime
    df.ds = pd.to_datetime(df.ds)
    df.index = pd.to_datetime(df.ds)
    df.y = df['y'].astype(np.int64)
    # bikin nilai carrying capacity
    df['cap'] = df['y'].mean()
    # drop nilai 0 kalo pake MAPE
    df = drop_zero(df)
    # split data training dan testing 80:20
    #df_train = df[:int(df.shape[0]*0.8)]
    #df_test = df[int(df.shape[0]*0.8):]
    # resampling = fill tanggal yang ke skip
    #df_train = df_train.resample('D').pad()
    #df_train['ds'] = df_train.index
    # fitting model
    m = Prophet(growth='logistic')
    m.add_country_holidays(country_name='ID')
    m.fit(df)
    # bikin prediksi dari model yang udah dibuat
    future = m.make_future_dataframe(periods=90)
    future['cap'] = df['y'].mean()
    forecast = m.predict(future)
    prediksi = forecast[(pd.to_datetime(forecast["ds"])
                         >= pd.to_datetime(now))]
    today = forecast[(pd.to_datetime(forecast["ds"])
                      == pd.to_datetime(now))]
    tomorrow = forecast[(pd.to_datetime(forecast["ds"])
                         == pd.to_datetime(now+timedelta(1)))]
    # split training data
    df_test = df[int(df.shape[0]*0.8):]
    y_true = df[int(df.shape[0]*0.8):]
    y_pred = m.predict(df_test)
    # itung MAPE
    mape = mean_abs_perc_err(y_true=np.asarray(
        y_true['y']), y_pred=np.asarray(y_pred['yhat']))
    # itung rmse
    rmse = root_mean_square_err(y_true=np.asarray(
        y_true['y']), y_pred=np.asarray(y_pred['yhat']))
    # convert ke JSON
    data_json = prediksi[['ds', 'yhat', 'yhat_upper',
                          'yhat_lower']].to_json(orient='records', date_format='iso', double_precision=0)
    yhat = prediksi['yhat'].to_json(orient='records')
    yhat_lower = prediksi['yhat_lower'].to_json(orient='records')
    yhat_upper = prediksi['yhat_upper'].to_json(orient='records')
    print(data_json)
    data_json = json.loads(data_json)
    print(data_json)
    labels = prediksi['ds'].dt.strftime(
        '%d-%m-%Y').to_json(orient='records')
    today = today[['ds', 'yhat', 'yhat_upper',
                   'yhat_lower']].to_json(orient='records', date_format='iso')
    tomorrow = tomorrow[['ds', 'yhat', 'yhat_upper',
                         'yhat_lower']].to_json(orient='records', date_format='iso')
    today = json.loads(today)
    tomorrow = json.loads(tomorrow)
    context = {
        "data": data_json,
        'yhat': yhat,
        "yhat_lower": yhat_lower,
        "yhat_upper": yhat_upper,
        'df': df,
        'today': today,
        'tomorrow': tomorrow,
        'forecast': forecast[['ds', 'yhat']],
        'labels': labels,
        'commodity_name': commodity_name,
        'mape': mape,
        'akurasi': 100-mape,
        'rmse': rmse,
        'commodityForm': commodityForm
    }
    if request.method == 'POST':
        context['id_foreign'] = request.POST['pilih_komoditas']
        return redirect('/prediksi/' + request.POST['pilih_komoditas'], )
    return render(request, "prediksi/index.html", context)
