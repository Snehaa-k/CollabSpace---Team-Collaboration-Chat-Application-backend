from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.

class AccountsUser(AbstractUser):
    username = models.CharField(max_length=150, unique=False)  
    email = models.EmailField(unique=True)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']



