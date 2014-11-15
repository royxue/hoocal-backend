from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.timezone import now
from django.utils.translation import ugettext as _
import re
from django.conf import settings
import hmac
from hashlib import sha1, md5
import uuid


USER_MODEL = settings.AUTH_USER_MODEL


class Event(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_by = models.ForeignKey(USER_MODEL)
    created_at = models.DateTimeField(default=now)
    last_modified = models.DateTimeField(default=now)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField()
    tag = models.TextField(blank=True)
    org = models.ForeignKey('Org', related_name='events', null=True,)
    is_public = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    like_users = models.ManyToManyField(USER_MODEL, related_name='like_events', db_table='hoocal_event_like', null=True)

    class Meta:
        db_table = 'hoocal_event'

    def __unicode__(self):
        return unicode(self.title)


class Org(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    owner = models.ForeignKey(USER_MODEL, related_name='own_orgs')
    members = models.ManyToManyField(USER_MODEL, related_name='member_orgs', db_table='hoocal_org_member')
    followers = models.ManyToManyField(USER_MODEL, related_name='follow_orgs', db_table='hoocal_org_follow', null=True)

    class Meta:
        db_table = 'hoocal_org'

    def __unicode__(self):
        return unicode(self.name)


class Comment(models.Model):
    content = models.TextField()
    event = models.ForeignKey('Event', related_name='comments')
    user = models.ForeignKey(USER_MODEL)
    created_at = models.DateTimeField(default=now)
    reply_to = models.ForeignKey(USER_MODEL, related_name='reply_from', null=True)

    class Meta:
        db_table = 'hoocal_comment'


class UserToken(models.Model):
    user = models.ForeignKey(USER_MODEL, related_name='token')
    token = models.CharField(max_length=64)
    expired_at = models.DateTimeField()
    is_expired = models.BooleanField(default=False)

    class Meta:
        db_table = 'hoocal_user_token'


class UserManager(BaseUserManager):

    def _create_user(self, nickname, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given nickname, email and password.
        """
        now = timezone.now()
        if not nickname:
            raise ValueError('The given nickname must be set')
        if not password:
            raise ValueError('The given password must be set')
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(nickname=nickname, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        password == md5(md5(password).lower()+'hoocal').lower()
        print password
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, nickname, email, password, **extra_fields):
        return self._create_user(nickname, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, nickname, email, password, **extra_fields):
        return self._create_user(nickname, email, password, True, True,
                                 **extra_fields)


# create hoocal AbstractUser as django AbstractUser does
class User(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(_('nickname'), max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid nickname.'), 'invalid')
        ], db_column='username')
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    avatar = models.URLField()
    subscribe_events = models.ManyToManyField('Event', related_name='subscribe_users', db_table='hoocal_subscribe', null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'password']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.nickname)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def __unicode__(self):
        return unicode(self.nickname)


class HoocalApiKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='api_keys')
    key = models.CharField(max_length=128, blank=True, default='', db_index=True)
    created = models.DateTimeField(default=now)
    expired = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(HoocalApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        # Get a random UUID.
        new_uuid = uuid.uuid4()
        # Hmac that beast.
        return hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()

    class Meta:
        db_table = "hoocal_apikey"