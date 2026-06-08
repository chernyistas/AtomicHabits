from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "tg_chat_id",
    )
    search_fields = ("id", "email", "username")
    list_filter = ("email", "tg_chat_id")

    @admin.display(description="Полное имя")
    def full_name(self, obj):
        return obj.get_full_name() or obj.username
