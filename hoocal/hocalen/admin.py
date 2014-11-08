from django.contrib import admin

from hocalen.models import User, Event, Org, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'email')
    fields = ('nickname', 'email', 'password', 'avatar', 'subscribe_events')


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'created_at', 'org')
    fields = ('title', 'content', 'created_by', 'created_at', 'last_modified',
            'start_time', 'end_time', 'tag', 'org', 'is_public', 'is_deleted', 'like_users')


class OrgAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'content', 'owner')
    fields = ('name', 'content', 'owner', 'members', 'followers')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'content', 'user', 'created_at', 'reply_to')
    fields = ('id', 'event', 'content', 'user', 'created_at', 'reply_to')


admin.site.register(User, UserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Org, OrgAdmin)
admin.site.register(Comment, CommentAdmin)
