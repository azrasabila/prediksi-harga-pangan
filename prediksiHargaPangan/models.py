from django.db import models


class Wilayah(models.Model):
    id = models.AutoField(primary_key=True)
    NAMA_WILAYAH = models.CharField(max_length=255)
    ID_FOREIGN_WILAYAH = models.IntegerField()

    def __str__(self):
        return self.NAMA_WILAYAH

    class Meta:
        db_table = "wilayah"
        #managed = False
        unique_together = (('NAMA_WILAYAH', 'ID_FOREIGN_WILAYAH'))


class Komoditas(models.Model):
    id = models.AutoField(primary_key=True)
    NAMA_KOMODITAS = models.CharField(max_length=255)
    ID_FOREIGN_KOMODITAS = models.IntegerField()

    def __str__(self):
        return self.NAMA_KOMODITAS

    class Meta:
        db_table = 'komoditas'
        #managed = False
        unique_together = (('NAMA_KOMODITAS', 'ID_FOREIGN_KOMODITAS'))


class Harga(models.Model):
    id = models.AutoField(primary_key=True)
    HARGA = models.IntegerField(unique=False)
    TANGGAL = models.DateField(unique=False)
    ID_KOMODITAS = models.ForeignKey(
        Komoditas, related_name='ID_KOMODITAS', default=1,  on_delete=models.CASCADE)
    ID_WILAYAH = models.ForeignKey(
        Wilayah, related_name='ID_WILAYAH', default=1, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {} : {}".format(self.ID_KOMODITAS, self.TANGGAL, self.HARGA)

    class Meta:
        db_table = 'harga'
        #managed = False
