from .models import Profile


def profile(request):
    """Add `profile` to template context when user is authenticated.

    Ensures a Profile exists and returns it; returns None for anonymous users.
    """
    if not request.user or not request.user.is_authenticated:
        return {}
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    return {"profile": profile_obj}
