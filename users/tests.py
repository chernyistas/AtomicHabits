from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели User"""

    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username="testuser", password="testpass123", tg_chat_id="123456789"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.tg_chat_id, "123456789")

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        admin = User.objects.create_superuser(username="admin", password="adminpass123")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)


class UserAPITest(APITestCase):
    """Тесты API пользователей"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.client = APIClient()
        User.objects.create_user(username="testuser", password="Testpass123")

    def test_register_user_success(self):
        """Тест успешной регистрации пользователя"""
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "TestPass123",
            "password2": "TestPass123",
        }
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser")
        self.assertEqual(response.data["email"], "newuser@test.com")

    def test_register_user_mismatch(self):
        """Тест: ошибка при несовпадении паролей"""
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "TestPass123",
            "password2": "WrongPass123",
        }
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Тест успешного входа и получения JWT токена"""
        data = {"username": "testuser", "password": "Testpass123"}
        response = self.client.post("/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """Тест: ошибка при неверных учётных данных"""
        data = {"username": "wronguser", "password": "Wrongpass123"}
        response = self.client.post("/login/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
