from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="AtomicHabits",
        default_version="v1",
        description="""
        Приложение AtomicHabits является трекером полезных привычек на основе книги Джеймса Клира «Атомные привычки»
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="itsmechernyi@gmail.com"),
        license=openapi.License(name="MIT License 2026 © [Chernyi Stas]"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("habits/", include("habits.urls", namespace="habits")),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "doc/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
