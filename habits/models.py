from django.core.exceptions import ValidationError
from django.db import models

from users.models import User


class Habit(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Связанная привычка",
        limit_choices_to={"is_pleasant": True},
    )
    periodicity = models.PositiveIntegerField(
        default=1, verbose_name="Периодичность(дни)"
    )
    reward = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Вознаграждение"
    )
    duration = models.PositiveIntegerField(verbose_name="Время на выполнение(сек)")
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def clean(self):
        """Валидация правил."""

        # ПРАВИЛО 1: Нельзя одновременно заполнять reward и related_habit
        if self.reward and self.related_habit:
            raise ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку"
            )

        # ПРАВИЛО 2: Время выполнения не больше 120 секунд
        if self.duration > 120:
            raise ValidationError(
                "Время выполнения привычки не должно превышать 120 секунд"
            )

        # ПРАВИЛО 3: Связанная привычка может быть только с признаком is_pleasant=True
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка должна быть приятной (is_pleasant=True)"
            )

        # ПРАВИЛО 4: У приятной привычки не может быть reward или related_habit
        if self.is_pleasant:
            if self.reward:
                raise ValidationError("Приятная привычка не может иметь вознаграждение")
            if self.related_habit:
                raise ValidationError(
                    "Приятная привычка не может иметь связанную привычку"
                )

        # ПРАВИЛО 5: Периодичность от 1 до 7 дней
        if self.periodicity is not None and (
            self.periodicity < 1 or self.periodicity > 7
        ):
            raise ValidationError("Периодичность должна быть от 1 до 7 дней")

        # Проверка на самоссылку
        if self.related_habit and self.related_habit.pk == self.pk:
            raise ValidationError("Привычка не может ссылаться на себя")

    def save(self, *args, **kwargs):
        """Переопределяем сохранение, чтобы всегда вызывать валидацию"""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["time"]

    def __str__(self):
        return f"{self.action} в {self.time} в {self.place}"
