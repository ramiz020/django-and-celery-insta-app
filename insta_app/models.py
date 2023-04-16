from django.db import models

class Profiles(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=30)

    class Meta:  
        db_table = "Profiles"


class Instagram(models.Model):
    username = models.CharField(max_length=50)
    following = models.CharField(max_length=100)
    followers = models.CharField(max_length=100)

    class Meta:  
        db_table = "Instagram"
