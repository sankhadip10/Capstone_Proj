from unittest.mock import Mock

from django.contrib.auth.models import User
from requests import patch
from rest_framework.test import APIClient
import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate

@pytest.fixture
def mock_razorpay():
    """Mock Razorpay client for testing"""
    with patch('payments.services.razorpay.Client') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def celery_eager(settings):
    """Run Celery tasks synchronously for testing"""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
