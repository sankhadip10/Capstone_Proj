from django.db import models

class User(models.Model):
    username = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=100,null=True)


class Product(models.Model):
    name = models.CharField(max_length=20)
    price = models.FloatField()
    description = models.TextField()
