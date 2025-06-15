from django.db import models


class User(models.Model):
    title = models.CharField(max_length=50, choices=[('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms')], default='Mr')
    username = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=255)

class User1(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField()

    def __str__(self):
        return self.name