from datetime import date
from celery import shared_task
from utils.skype_message import send_skype_message
from django.conf import settings
from app.models import CustomUser


def get_birthday_employee():
    try:
        birthday_boys = CustomUser.objects.filter(date_of_birth__day=date.today().day,date_of_birth__month=date.today().month).values('first_name', 'last_name')
    except Exception as e:
        birthday_boys = ''

    return birthday_boys

@shared_task(name="send_birthday_message")
def send_birthday_message():
    try:
        birthday_boys = get_birthday_employee()
        for birthday in birthday_boys:
            try:
                # message = f"Happy Birthday, {birthday['first_name'].title()} {birthday.get('last_name').title() if birthday.get('last_name') else ''}! 🎉🎂 May your day be filled with joy and happiness!"
                message = \
f'''🎉🎂 Happy Birthday, {birthday['first_name'].title()} {birthday.get('last_name').title() if birthday.get('last_name') else ''} 🎂🎉

May your day be filled with laughter, joy, and all the love you deserve! 🎈💖 Wishing you an incredible year ahead full of exciting opportunities, cherished memories, and endless success. 🌟✨

Let’s celebrate the amazing person you are and all the happiness you bring into our lives! 🥳🎁 Here's to making today as special as you are. 🥂🍰 Enjoy every moment to the fullest—you deserve it! 🎊🎉

Cheers, team! 🙌🎉
'''
                surveillance_skype_ids = [settings.QUANTUMBOT_SKYPE_ID]
                send_skype_message(recipient_ids=surveillance_skype_ids, message=message)
            except Exception as e:
                print(e)

    except Exception as e:
        print(e)

#app.tasks.send_birthday_email
