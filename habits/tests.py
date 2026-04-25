from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.serializers import HabitSerializer

User = get_user_model()


class HabitModelTest(TestCase):
    """Тесты модели Habit"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(
            username="user", password="testpass123", tg_chat_id="123456789"
        )
        self.pleasant_habit = Habit.objects.create(
            owner=self.user,
            place="Ванна",
            time="11:00:00",
            action="Принять ванну",
            is_pleasant=True,
            duration=100,
        )

    def test_create_habit_success(self):
        """Тест успешного создания полезной привычки"""
        habit = Habit.objects.create(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Сделать зарядку",
            duration=60,
        )
        self.assertEqual(habit.action, "Сделать зарядку")
        self.assertEqual(habit.owner, self.user)
        self.assertFalse(habit.is_pleasant)

    def test_create_pleasant_habit_success(self):
        """Тест успешного создания приятной привычки"""
        habit = Habit.objects.create(
            owner=self.user,
            place="Кинотеатр",
            time="20:00:00",
            action="Посмотреть фильм",
            is_pleasant=True,
            duration=120,
        )
        self.assertTrue(habit.is_pleasant)

    def test_duration_validation_over_120(self):
        """Тест: время выполнения не может быть больше 120 секунд"""
        habit = Habit(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Слишком долго",
            duration=121,
        )
        try:
            habit.full_clean()
            self.fail("Ожидалась ValidationError для duration > 120")
        except ValidationError as e:
            self.assertIn("120 секунд", str(e))

    def test_reward_and_related_habit_together(self):
        """Тест: нельзя одновременно reward и related_habit"""
        habit = Habit(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Уборка",
            reward="Шоколадка",
            related_habit=self.pleasant_habit,
            duration=60,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_periodicity_range(self):
        """Тест на превышение периодичности"""
        habit = Habit(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Чтение",
            periodicity=8,
            duration=60,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()


class HabitAPITest(APITestCase):
    """Тесты модели Habit"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(
            username="user", password="testpass123", tg_chat_id="123456789"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        self.pleasant_habit = Habit.objects.create(
            owner=self.user,
            place="Ванна",
            time="11:00:00",
            action="Принять ванну",
            is_pleasant=True,
            duration=60,
        )

        self.client.force_authenticate(user=self.user)

    def test_create_habit_success(self):
        """Тест создания привычки"""
        data = {
            "place": "Дома",
            "time": "10:00:00",
            "action": "Сделать зарядку",
            "duration": 60,
        }
        response = self.client.post("/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.all().count(), 2)

    def test_get_habits_list(self):
        """Тест получения списка привычек пользователя"""
        Habit.objects.create(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Зарядка",
            duration=60,
        )
        Habit.objects.create(
            owner=self.user,
            place="Парк",
            time="18:00:00",
            action="Прогулка",
            duration=120,
        )
        response = self.client.get("/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_user_sees_only_own_habits(self):
        """Тест: пользователь видит только свои привычки"""
        Habit.objects.create(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Моя привычка",
            duration=60,
        )
        Habit.objects.create(
            owner=self.other_user,
            place="Дома",
            time="09:00:00",
            action="Чужая привычка",
            duration=60,
        )
        response = self.client.get("/habits/")
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["action"], "Моя привычка")

    def test_update_own_habit(self):
        """Тест: пользователь может редактировать свою привычку"""
        habit = Habit.objects.create(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Зарядка",
            duration=60,
        )
        data = {"action": "Утренняя зарядка", "duration": 60}
        response = self.client.patch(f"/habits/{habit.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "Утренняя зарядка")

    def test_delete_own_habit(self):
        """Тест: пользователь может удалить свою привычку"""
        habit = Habit.objects.create(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Зарядка",
            duration=60,
        )
        response = self.client.delete(f"/habits/{habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=habit.id).count(), 1)

    def test_cannot_delete_other_habit(self):
        """Тест: пользователь не может удалить чужую привычку"""
        habit = Habit.objects.create(
            owner=self.other_user,
            place="Дома",
            time="09:00:00",
            action="Чужая привычка",
            duration=60,
        )
        response = self.client.delete(f"/habits/{habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_other_habit(self):
        """Тест: пользователь не может редактировать чужую привычку"""
        habit = Habit.objects.create(
            owner=self.other_user,
            place="Дома",
            time="09:00:00",
            action="Чужая привычка",
            duration=60,
        )
        data = {"action": "Попытка взлома"}
        response = self.client.patch(f"/habits/{habit.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_habits_list(self):
        """Тест на список публичных привычек"""
        self.client.credentials()
        Habit.objects.create(
            owner=self.user,
            place="Дома",
            time="10:00:00",
            action="Публичная привычка",
            duration=60,
            is_public=True,
        )
        response = self.client.get("/habits/public_habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Публичная привычка")

    def test_pagination(self):
        """Тест: пагинация по 5 привычек на страницу"""
        for i in range(6):
            Habit.objects.create(
                owner=self.user,
                place="Дома",
                time=f"{10 + i}:00:00",
                action=f"Привычка {i}",
                duration=60,
            )
        response = self.client.get("/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["next"])
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 7)


class HabitSerializerTest(TestCase):
    """Тесты сериализатора HabitSerializer"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.serializer_data = {
            "owner": self.user.id,
            "place": "Дома",
            "time": "10:00:00",
            "action": "Зарядка",
            "duration": 60,
        }

    def test_serializer_valid(self):
        """Тест: валидные данные проходят сериализацию"""
        serializer = HabitSerializer(data=self.serializer_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_duration(self):
        """Тест: невалидные данные не проходят сериализацию"""
        self.serializer_data["duration"] = 121
        serializer = HabitSerializer(data=self.serializer_data)
        self.assertTrue(serializer.is_valid())

        with self.assertRaises(ValidationError):
            habit = serializer.save(owner=self.user)
            habit.full_clean()
