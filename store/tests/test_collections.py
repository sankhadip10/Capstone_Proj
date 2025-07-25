from store.models import Collection, Product
from rest_framework import status
import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)

    return do_create_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client, create_collection):
        response = create_collection({'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client, create_collection):
        # Now User is properly imported and available
        user = baker.make(User, is_staff=False)
        api_client.force_authenticate(user=user)

        response = create_collection({'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, api_client, create_collection):
        admin_user = baker.make(User, is_staff=True)
        api_client.force_authenticate(user=admin_user)

        response = create_collection({'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, api_client, create_collection):
        admin_user = baker.make(User, is_staff=True)
        api_client.force_authenticate(user=admin_user)

        response = create_collection({'title': 'Electronics'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)
        response = api_client.get(f'/store/collections/{collection.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == collection.id
        assert response.data['title'] == collection.title