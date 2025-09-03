from django.db import models
from multiselectfield import MultiSelectField
from app.models import CustomUser
from courses.models import Topic
from aptitude_test.models.topic import Topic
from utils.models import QBBaseModel


class Conference(QBBaseModel):
    NEVER = "Never"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

    TYPE_OF_REPEAT = (
        (NEVER, "Never"),
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
    )

    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"

    DAYS = (
        (SUNDAY, "Sunday"),
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
    )
    title = models.CharField(max_length=255)
    event_code = models.CharField(max_length=255)
    agenda = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    repeat = models.CharField(choices=TYPE_OF_REPEAT, max_length=100, default=NEVER)
    week_day = MultiSelectField(choices=DAYS, max_length=100, blank=True, null=True, max_choices=7)
    repeat_every_days = models.PositiveIntegerField(blank=True, null=True,
                                                    help_text="Number of days between repetitions")
    repeat_every_weeks = models.PositiveIntegerField(blank=True, null=True,
                                                     help_text="Number of weeks between repetitions")
    repeat_every_months = models.PositiveIntegerField(blank=True, null=True,
                                                      help_text="Number of months between repetitions")
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='created_by')
    # updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    presenting = models.ManyToManyField(CustomUser, blank=True, related_name='presenting')
    attending = models.ManyToManyField(CustomUser, blank=True, related_name='attending')
    topic = models.ManyToManyField(Topic, blank=True, related_name='topic')

    def __str__(self):
        return self.title
