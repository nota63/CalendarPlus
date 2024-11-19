from django.db import models

# Create your models here.


class PushSubscription(models.Model):
    endpoint = models.TextField()
    p256dh = models.TextField()
    auth = models.TextField()

    def __str__(self):
        return self.endpoint
    