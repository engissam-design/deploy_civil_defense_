from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "map.accounts"

    def ready(self):
        import map.accounts.signals
