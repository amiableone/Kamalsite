from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    likes = models.IntegerField("times liked", default=0)
    additions = models.IntegerField("additions to cart", default=0)
    purchases = models.IntegerField("times purchased", default=0)

    def __str__(self):
        return (f"{self.name.title()}(Likes={self.likes})")
