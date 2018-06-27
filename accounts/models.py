from django.db import models
from django.contrib.auth.models import User


class ActivateValidation(models.Model):
    user = models.ForeignKey(User, verbose_name='用户')
    activate_key = models.CharField('激活码', max_length=50)
    #expire_time = models.DateTimeField