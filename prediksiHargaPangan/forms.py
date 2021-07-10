from django import forms
from .models import Komoditas


class CommodityForm(forms.Form):
    komoditas_list = Komoditas.objects.all()
    komoditas = []
    for i in Komoditas.objects.all():
        komoditas.append((i.ID_FOREIGN_KOMODITAS, i.NAMA_KOMODITAS))
    pilih_komoditas = forms.ChoiceField(choices=komoditas,
                                        widget=forms.Select(
                                            attrs={
                                                'class': 'form-select form-select-lg col-sm-2'
                                            }
                                        )
                                        )

    class Meta:
        Model = Komoditas
        fields = [
            "ID_FOREIGN_KOMODITAS", "NAMA_KOMODITAS"
        ]
