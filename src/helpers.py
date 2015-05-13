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

def isRegisterFormValid(form):
    # checking that all needed keys exist
    checkkey = lambda x : x in form.keys()
    if False in map(checkkey, ['firstname', 'lastname', 'password', 'phone', 'street', 'number', 'cp', 'city', 'card']):
        return False
    # checking for required keys
    checkrequired = lambda key : len(form[key]) > 0
    if False in map(checkrequired, ['firstname', 'lastname', 'password', 'phone', 'street', 'number', 'cp', 'city', 'card']):
        return False

    # small helper function to validate all fixed-length digits
    def validLengthDigit(toCheck, numberOfDigits):
        if len(toCheck) != numberOfDigits :
            return False
        try:
            int(toCheck)
        except Exception, e:
            return False
        return True

    # password check
    if not validLengthDigit(form["password"], 4):
        return False
    # phone check
    if not validLengthDigit(form["phone"], 10):
        return False
    # credit card check
    if not validLengthDigit(form["card"], 16):
        return False
    return True