from datetime import date
from celery import shared_task
from utils.skype_message import send_skype_message
from django.conf import settings
from app.models import CustomUser

def get_anniversary_employee():
    try:
        print(date.today())
        anniversary_boys = CustomUser.objects.filter(joining_date__day=date.today().day, joining_date__month=date.today().month).values('first_name', 'last_name','joining_date')
        print(anniversary_boys)
    except Exception as e:
        anniversary_boys = ''
    return anniversary_boys

def number_to_ordinal(num):
    if 11 <= num % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(num % 10, "th")
    return f"{num}{suffix}"


@shared_task(name="send_anniversary_message")
def send_anniversary_message():
    try:
        anniversary_boys = get_anniversary_employee()
        if anniversary_boys:
            for anniversary in anniversary_boys:
                if anniversary['joining_date'].year == date.today().year:
                    continue

                try:
                    # message = f"Congratulations on your {number_to_ordinal(date.today().year-anniversary['joining_date'].year)} Work Anniversary, {anniversary['first_name'].title()} {anniversary.get('last_name').title() if anniversary.get('last_name') else ''}! 🎉👏 Thank you for your dedication and hard work over the years!"
                    message = \
f'''Happy Work Anniversary, {anniversary['first_name'].title()} {anniversary.get('last_name').title() if anniversary.get('last_name') else ''}! ✨

Congratulations on completing {str(date.today().year-anniversary['joining_date'].year)} incredible {'year' if str(date.today().year-anniversary['joining_date'].year) == '1' else 'years'} with us!  Your dedication, hard work, and positive energy continue to inspire everyone around you. 🙌💼

Thank you for being an integral part of our journey and contributing to our success. 🌱💪 Here's to celebrating your achievements and looking forward to many more milestones together! 

Wishing you continued growth, happiness, and success in the years ahead. 🎯 Keep shining bright! 

Best regards.
'''
                    surveillance_skype_ids = [settings.QUANTUMBOT_SKYPE_ID]
                    send_skype_message(recipient_ids=surveillance_skype_ids, message=message)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


#app.tasks.sending_work_anniversary_message