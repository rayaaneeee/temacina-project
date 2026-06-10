import re
from django.core.exceptions import ValidationError


class StrongPasswordValidator:
    """
    Enforces:
      - Min 10 characters
      - At least 1 uppercase letter
      - At least 1 lowercase letter
      - At least 1 digit
      - At least 1 special character  (!@#$%^&*...)
      - Not a common weak password
    """
    COMMON = {"password", "123456789", "azerty123", "admin1234",
               "qwerty123", "letmein1", "welcome1"}

    def validate(self, password, user=None):
        if len(password) < 10:
            raise ValidationError("Password must be at least 10 characters.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain an uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain a lowercase letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain a digit.")
        if not re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]", password):
            raise ValidationError("Password must contain a special character.")
        if password.lower() in self.COMMON:
            raise ValidationError("Password is too common.")

    def get_help_text(self):
        return ("Password: 10+ chars, uppercase, lowercase, digit, "
                "special character.")
