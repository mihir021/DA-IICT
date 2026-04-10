import os

import django
import pytest


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pulseprice.settings")
django.setup()


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()
