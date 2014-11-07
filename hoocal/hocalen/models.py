from django.db import models
from django.utils.timezone import now


class Event(models.Model):
    title = models.TextField()
    content = models.TextField()
    created_by = models.ForeignKey('User')
    created_at = models.DateTimeField(default=now)
    last_modified = models.DateTimeField(default=now)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    tag = models.TextField()
    org = models.ForeignKey('Org', related_name='events')
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    like_users = models.ManyToManyField('User', related_name='like_events', db_table='hoocal_event_like')


class Org(models.Model):
    name = models.TextField()
    content = models.TextField()
    owner = models.ForeignKey('User', related_name='own_orgs')
    members = models.ManyToManyField('User', related_name='member_orgs', db_table='hoocal_org_member')
    followers = models.ManyToManyField('User', related_name='follow_orgs', db_table='hoocal_org_follow')


class User(models.Model):
    nickname = models.TextField()
    email = models.EmailField()
    password = models.TextField()
    avatar = models.URLField()
    subscribe_events = models.ManyToManyField('Event', related_name='subscribe_user', db_table='hoocal_subscribe')


class Comment(models.Model):
    event = models.ForeignKey('Event', related_name='comments')
    user = models.ForeignKey('User')
    created_at = models.DateTimeField(default=now)
    reply_to = models.ForeignKey('User', related_name='reply_from')




    




