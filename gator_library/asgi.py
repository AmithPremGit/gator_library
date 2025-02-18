"""
ASGI config for gator_library project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gator_library.settings')

application = get_asgi_application()