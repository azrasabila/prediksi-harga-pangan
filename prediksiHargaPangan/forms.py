from django import forms
from .models import *


class CommodityForm(forms.Form):
    komoditas = (
        (3, 'Bawang Merah'),
        (18, 'Cabe Rawit Merah'),
        (8, 'Gula Pasir')
    )
    # print(komoditas)
    pilih_komoditas = forms.ChoiceField(choices=komoditas)
