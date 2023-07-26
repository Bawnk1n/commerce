from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListings(models.Model):
    title = models.CharField(max_length = 64)
    description = models.CharField(max_length = 255)
    starting_price = models.IntegerField()  
    image = models.ImageField(default='', upload_to='media/')
    category = models.CharField(max_length=64, default='')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_open = models.BooleanField(default=True)
    

class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)
    amount = models.IntegerField()

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    upvotes = models.IntegerField(default=0)

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)