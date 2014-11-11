from django.db import models
from django.utils.timezone import now


class Event(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_by = models.ForeignKey('User')
    created_at = models.DateTimeField(default=now)
    last_modified = models.DateTimeField(default=now)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField()
    tag = models.TextField(blank=True)
    org = models.ForeignKey('Org', related_name='events', null=True,)
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    like_users = models.ManyToManyField('User', related_name='like_events', db_table='hoocal_event_like', null=True)
    
    def __unicode__(self):
        return unicode(self.title)


class Org(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    owner = models.ForeignKey('User', related_name='own_orgs')
    members = models.ManyToManyField('User', related_name='member_orgs', db_table='hoocal_org_member')
    followers = models.ManyToManyField('User', related_name='follow_orgs', db_table='hoocal_org_follow', null=True)
    
    def __unicode__(self):
        return unicode(self.name)


class User(models.Model):
    nickname = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=50)
    avatar = models.URLField()
    subscribe_events = models.ManyToManyField('Event', related_name='subscribe_user', db_table='hoocal_subscribe', null=True)
    
    def __unicode__(self):
        return unicode(self.nickname)


class Comment(models.Model):
    content = models.TextField()
    event = models.ForeignKey('Event', related_name='comments')
    user = models.ForeignKey('User')
    created_at = models.DateTimeField(default=now)
    reply_to = models.ForeignKey('User', related_name='reply_from', null=True)


class UserToken(models.Model):
    user = models.ForeignKey('User', related_name='token')
    token = models.CharField(max_length=64)
    expired_at = models.DateTimeField()
    is_expired = models.BooleanField(default=False)

