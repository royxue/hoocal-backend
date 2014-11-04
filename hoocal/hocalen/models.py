from django.db import models
from django.utils.timezone import now

class Event(models.Model):
    title = models.TextField()
    content = models.TextField()
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(default=now)
    last_modified = models.DateTimeField(default=now)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    tag = models.TextField()
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)


class Org(models.Model):
    name = models.TextField()
    content = models.TextField()
    owner = models.ForeignKey(User)


