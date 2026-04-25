from celery import shared_task
from django.utils import timezone

from habits.models import Habit


@shared_task
def send_telegram_message(chat_id, message):
    """Эмуляция отправки сообщений в Telegram.
    В реальном проекте здесь был бы код отправки через API Telegram."""
    # url = f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage"
    # payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    # proxies = {
    #     "http": "socks5://127.0.0.1:9150",
    #     "https": "socks5://127.0.0.1:9150",
    # }
    # try:
    #     response = requests.post(url, json=payload, timeout=10)
    #     return response.json()
    # except Exception as e:
    #     return {"error": str(e)}
    print(f"\n{'=' * 60}")
    print("[TELEGRAM УВЕДОМЛЕНИЕ - ЭМУЛЯЦИЯ]")
    print(f"Кому (Chat ID): {chat_id}")
    print(f"Время: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Текст сообщения:")
    print(f"{message}")
    print(f"{'=' * 60}\n")
    return {"ok": True, "emulated": True, "chat_id": chat_id}


@shared_task
def check_habit_reminders():
    """Проверяет привычки и отправляет напоминания (каждую минуту)."""
    now = timezone.now()
    current_time = now.time()
    current_hour = current_time.hour
    current_minute = current_time.minute

    habits = Habit.objects.filter(
        is_pleasant=False,
        time__hour=current_hour,
        time__minute=current_minute,
    )

    for habit in habits:
        chat_id = habit.owner.tg_chat_id
        if not chat_id:
            continue

        message = "<b>Напоминание о привычке!</b>\n\n"
        message += f"<b>Действие:</b> {habit.action}\n"
        message += f"<b>Место:</b> {habit.place}\n"
        message += f"<b>Время выполнения:</b> {habit.duration} сек."

        if habit.reward:
            message += f"\n <b>Вознаграждение:</b> {habit.reward}"

        if habit.related_habit:
            message += f"\n <b>Приятная привычка:</b> {habit.related_habit.action}"

        send_telegram_message.delay(chat_id, message)
