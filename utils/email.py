from django.conf import settings


def cleanup_email(email: str) -> str:
    # the line below prevents creating multiple accounts with different alias
    if not settings.DEBUG and email[-10:] == "@gmail.com":
        # return email.split('@')[0].split('+')[0].replace('.', '') + '@gmail.com'
        return email.split("@")[0].split("+")[0] + "@gmail.com"
    return email
