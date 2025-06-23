from django.db import models

class NewProductJson(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    class Meta:
        db_table = "newproduct_json"  # Optional, makes table name clear
