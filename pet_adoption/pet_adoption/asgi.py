"""
ASGI config for pet_adoption project.
It exposes the ASGI callable as a module-level variable named ``application``.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_adoption.settings')
application = get_asgi_application()