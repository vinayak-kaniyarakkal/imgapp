from __future__ import unicode_literals
from django.db import models
import hashlib
import time


def _create_hash():
    hash = hashlib.sha1()
    hash.update(str(time.time()))
    return hash.hexdigest()[:20]


class Token(models.Model):
    token = models.CharField(default=_create_hash, max_length=100, unique=True)
