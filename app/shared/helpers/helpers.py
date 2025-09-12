def destructure_user(user):
    return (user.id, user.username or "", user.first_name or "", user.last_name or "")
