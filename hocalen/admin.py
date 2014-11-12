from django.contrib import admin

from hocalen.models import User, Event, Org, Comment


# class UserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'nickname', 'email')
#     fields = ('nickname', 'email', 'password', 'avatar')

class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'created_at', 'org', 'is_public', 'is_deleted')
    fields = ('title', 'content', 'created_by', 'created_at', 'last_modified',
            'start_time', 'end_time', 'tag', 'org', 'is_public', 'is_deleted')


class OrgAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'content', 'owner')
    fields = ('name', 'content', 'owner', 'members')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'content', 'user', 'created_at', 'reply_to')
    fields = ('id', 'event', 'content', 'user', 'created_at')

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'nickname')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'nickname', 'password', 'is_active', 'is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class HoocalUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'nickname', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'nickname', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password1', 'password2')}
        ),
    )
    search_fields = ('email', 'nickname')
    ordering = ('email',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(User, HoocalUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

# admin.site.register(User, UserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Org, OrgAdmin)
admin.site.register(Comment, CommentAdmin)
