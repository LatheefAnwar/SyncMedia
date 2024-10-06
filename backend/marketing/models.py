from django.db import models
from authentication.models import UserProfile
# Create your models here.

class ProductsDetail(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    productname = models.CharField(max_length=50)
    productlogo = models.ImageField(upload_to='productlogo')

    def __str__(self):
        return self.productname
