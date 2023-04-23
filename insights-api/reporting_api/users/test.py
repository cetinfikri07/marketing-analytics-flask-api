import re

def validate_email(email):
    path = "^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
    if re.match(path, email):
        return True
    return False

validate_email('john.doe@gmail.com')





