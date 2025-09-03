from django.db import models
from aptitude_test.models import Choices
from aptitude_test.models.questions import Questions
from utils.models import QBBaseModel


class PersonsAnswers(QBBaseModel):
    choices_field = 'choices'
    text_area = 'text_area'

    type_choices = (
        (choices_field, 'Choice Fields'),
        (text_area, 'Text Area'),
    )
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choices, blank=True)
    type = models.CharField(choices=type_choices, max_length=100, default=choices_field)
    text = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    is_partially_correct = models.BooleanField(default=False)
    is_not_attempted = models.BooleanField(default=False)
    is_wrong = models.BooleanField(default=False)

    def __str__(self):
        return str(self.question)
