from django.db import models


class Newproduct(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()


class DiaryProduct(Newproduct):

    expiry_date = models.DateField(
        auto_now=False,
        auto_now_add=True
    )

    class Meta:
        db_table = 'diaryproduct'
