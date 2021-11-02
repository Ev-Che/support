from django.contrib.auth.models import User
from django.db import models


class Ticket(models.Model):
    body = models.CharField(max_length=256)
    is_completed = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Ticket({self.id})'
