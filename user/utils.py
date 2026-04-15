import random
import string


def generate_random_password(min_length=8, max_length=12) -> str:
    """Generates a secure random password with a mix of upper, lower, digits, and special characters."""
    char_set = (
        string.ascii_uppercase
        + string.ascii_lowercase
        + string.digits
        + string.punctuation
    )
    password_length = random.randint(min_length, max_length)

    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]

    # Fill the remaining characters
    password += [random.choice(char_set) for _ in range(password_length - 4)]
    random.shuffle(password)

    return "".join(password)
