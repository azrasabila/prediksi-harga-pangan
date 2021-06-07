from django.db import models


class Wilayah(models.Model):
    ID_WILAYAH = models.AutoField(primary_key=True)
    NAMA_WILAYAH = models.CharField(max_length=50)
    ID_FOREIGN_WILAYAH = models.IntegerField()

    class Meta:
        db_table = "wilayah"
        managed = False
        unique_together = (('NAMA_WILAYAH', 'ID_FOREIGN_WILAYAH'))


class Komoditas(models.Model):
    ID_KOMODITAS = models.AutoField(primary_key=True)
    NAMA_KOMODITAS = models.CharField(max_length=50)
    ID_FOREIGN = models.IntegerField()

    class Meta:
        db_table = 'komoditas'
        managed = False
        unique_together = (('NAMA_KOMODITAS', 'ID_FOREIGN'))
