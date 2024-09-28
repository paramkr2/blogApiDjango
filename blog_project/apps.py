from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'blog'

    def ready(self):
        import blog.signals  # Import the signals module
