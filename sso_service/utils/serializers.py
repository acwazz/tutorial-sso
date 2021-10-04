from pydantic import SecretStr
import re

class PasswordValidationError(ValueError):
    pass


class PasswordString(SecretStr):
    @classmethod
    def validate(cls, val):
        result = re.fullmatch('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#.$%^&*])[A-Za-z\d@$!#%*?&]{8,}', val)
        if not result:
            raise PasswordValidationError(
                "Password must contain at least 1 Uppercase letter, 1 lowercase letter, 1 number and 1 special character, with a minimum length of 8 characters."
                )
        return super().validate(val)
