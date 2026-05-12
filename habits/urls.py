from django.urls import path
from rest_framework.routers import SimpleRouter

from habits.apps import HabitsConfig
from habits.views import HabitViewSet, PublicHabitListView

app_name = HabitsConfig.name

router = SimpleRouter()
router.register(r"", HabitViewSet, basename="habits")

urlpatterns = [
    path("public_habits/", PublicHabitListView.as_view(), name="public_habits"),
]

urlpatterns += router.urls
