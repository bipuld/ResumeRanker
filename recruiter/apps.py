from django.apps import AppConfig


class RecruiterConfig(AppConfig):
    name = 'recruiter'

    def ready(self):
        import recruiter.signals