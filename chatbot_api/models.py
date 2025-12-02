from django.db import models

class RealEstateData(models.Model):
    year = models.IntegerField()
    area = models.CharField(max_length=100)
    price = models.FloatField()
    demand = models.FloatField()
    size = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.area} - {self.year}"