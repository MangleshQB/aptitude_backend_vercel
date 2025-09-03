from datetime import date
from configuration.models import Holiday
from utils.skype_message import send_skype_message
from django.conf import settings
import calendar
from celery import shared_task
from datetime import datetime

@shared_task(name="upcoming_holiday_list")
def upcoming_holiday_list():
    now = datetime.now()
    _, last_day = calendar.monthrange(now.year, now.month)
    if now.day == last_day:
        try:
            today = date.today()
            next_month = (today.month % 12) + 1
            next_year = today.year if next_month != 1 else today.year + 1

            holiday_list = Holiday.objects.filter(
                date__month=next_month, date__year=next_year
            ).values('name', 'date', 'type', 'description')

            if holiday_list:
                month_name = calendar.month_name[next_month]
                holiday_list_str = [
                    f"📢 **Upcoming Holidays Announcement 🌟**\n\n",
                    f"Dear Team,\n\nHere’s the list of upcoming holidays for {month_name}:\n\n"
                ]

                for idx, holiday in enumerate(holiday_list, start=1):
                    holiday_details = [
                        f"{idx}️ {holiday['name']} - {holiday['date']} 🎉\n",
                        f"- {holiday['description']}\n\n" if holiday['description'] else "\n"
                    ]
                    holiday_list_str.extend(holiday_details)

                holiday_list_str.append(
                    "Please plan your tasks and schedules accordingly to ensure a smooth workflow. "
                    "Wishing you a relaxing and joyful time during these breaks! 💆‍♂️✨\n\n"
                    "Best regards"
                )
                try:
                    surveillance_skype_ids = [settings.QUANTUMBOT_SKYPE_ID]
                    send_skype_message(recipient_ids=surveillance_skype_ids, message="".join(holiday_list_str))
                except Exception as e:
                    print(f"Error sending Skype message: {e}")
        except Exception as e:
            print(f"Error fetching holiday list: {e}")

