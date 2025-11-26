from .models import User, SiteSetting

def UserCheckRole(user):
    user_obj = User.objects.get(username=user.username)
    if user_obj.is_staff:
        return True
    return False

def get_setting(category, key, default=None):
    try:
        return SiteSetting.objects.get(category=category, key=key).value
    except SiteSetting.DoesNotExist:
        return default