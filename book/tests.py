from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import Book

class BookAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.token, _ = Token.objects.get_or_create(user=self.user)  # ✅ 언팩하여 self.token에 저장
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_book_list_authenticated(self):
        response = self.client.get('/api/generic/books/')
        self.assertEqual(response.status_code, 200)

    def test_book_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/generic/books/')
        self.assertEqual(response.status_code, 401)
from django.test import TestCase

# Create your tests here.
