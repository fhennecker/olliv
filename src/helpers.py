def isLoginFormValid(form):
    if "userid" not in form.keys():
        return False
    if "password" not in form.keys():
        return False
    try:
        int(form["userid"])
    except Exception, e:
        return False
    return True