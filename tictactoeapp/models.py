from django.db import models
from django.db.models import Count
import random
# Create your models here.
class FirstPopupMessages(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:20]
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"