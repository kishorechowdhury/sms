from django.contrib.auth.models import User, Permission

from .models import UserActivity, Profile


def log_action(userid, message='System changed'):
    user_id = User.objects.get(id=userid)
    ua = UserActivity(user=user_id, action=message)
    ua.save()
    return True


def get_profile(userid):
    try:
        profile = Profile.objects.get(user=userid)
    except:
        profile = Profile.DoesNotExist
    return profile


def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return User.get_all_permissions(user)