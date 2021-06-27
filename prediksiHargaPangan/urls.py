from prediksiHargaPangan import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('prediksi/<int:id_foreign>', views.prediksi, name='prediksi')
]