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
    week = prediksi[(pd.to_datetime(forecast["ds"])
                     <= pd.to_datetime(now+timedelta(7)))]
    month = prediksi[(pd.to_datetime(forecast["ds"])
                      <= pd.to_datetime(now+timedelta(30)))]
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
    # data forecast
    data_df = df.to_json(
        orient='records', double_precision=0)
    data_df = json.loads(data_df)
    data_forecast = forecast.to_json(
        orient='records', double_precision=0)
    data_forecast = json.loads(data_forecast)
    # prediksi kuartal
    prediksi_kuartal = prediksi[['ds', 'yhat', 'yhat_upper',
                                 'yhat_lower']].to_json(orient='records', double_precision=0)
    prediksi_kuartal = json.loads(prediksi_kuartal)
    # prediksi weekly
    prediksi_seminggu = week[['ds', 'yhat', 'yhat_upper',
                              'yhat_lower']].to_json(orient='records', double_precision=0)
    prediksi_seminggu = json.loads(prediksi_seminggu)
    # prediksi bulanan
    prediksi_sebulan = month[['ds', 'yhat', 'yhat_upper',
                              'yhat_lower']].to_json(orient='records', double_precision=0)
    prediksi_sebulan = json.loads(prediksi_sebulan)
    today = today[['ds', 'yhat', 'yhat_upper',
                   'yhat_lower']].to_json(orient='records')
    tomorrow = tomorrow[['ds', 'yhat', 'yhat_upper',
                         'yhat_lower']].to_json(orient='records', date_format='iso')
    today = json.loads(today)
    tomorrow = json.loads(tomorrow)
    tommorow_date = date.today() + timedelta(1)
    context = {
        "prediksi_kuartal": prediksi_kuartal,
        'data_df': data_df,
        "data_forecast": data_forecast,
        'prediksi_seminggu': prediksi_seminggu,
        'prediksi_sebulan': prediksi_sebulan,
        'today': today,
        'tomorrow': tomorrow,
        'tommorow_date': tommorow_date,
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
