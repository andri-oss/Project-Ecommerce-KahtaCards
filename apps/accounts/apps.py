from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        from .firebase import init_firebase
        init_firebase()
