import logging

import firebase_admin
from django.conf import settings
from firebase_admin import credentials

logger = logging.getLogger(__name__)


def init_firebase():
    """Initialize the firebase-admin app once, if a service account key is present."""
    if firebase_admin._apps:
        return

    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    if not cred_path.exists():
        logger.warning('Firebase credentials not found at %s — Google sign-in disabled.', cred_path)
        return

    firebase_admin.initialize_app(credentials.Certificate(str(cred_path)))
