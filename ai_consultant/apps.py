from django.apps import AppConfig


class AiConsultantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_consultant'
    verbose_name = 'AI Консультант'

    def ready(self):
        import ai_consultant.signals