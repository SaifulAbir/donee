
def profile_view_count(profile):
    profile.view_count += 1
    profile.save()