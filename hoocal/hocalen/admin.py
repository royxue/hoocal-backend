from django.contrib import admin

from hocalen.models import User, Event, Org, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'email')
    fields = ('nickname', 'email', 'password', 'avatar')


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'created_at', 'org')
    fields = ()
