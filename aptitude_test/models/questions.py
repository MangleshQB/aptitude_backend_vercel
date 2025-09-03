from django.db import models
from app.models import Designation
from aptitude_test.models import Choices
from utils.models import QBBaseModel

class Questions(QBBaseModel):
    choices_field = 'choices'
    text_area = 'text_area'

    type_choices = (
        (choices_field, 'Choice Fields'),
        (text_area, 'Text Area'),
    )

    easy = 'easy'
    medium = 'medium'
    hard = 'hard'

    difficulty_type = (
        (easy, 'Easy'),
        (medium, 'Medium'),
        (hard, 'Hard')
    )

    technical = 'technical'
    aptitude = 'aptitude'

    type_of_Question = (
        (technical, 'Technical'),
        (aptitude, 'Aptitude')
    )
    question = models.TextField()
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    type = models.CharField(choices=type_choices, max_length=100, default=choices_field)
    choices = models.ManyToManyField(Choices, blank=True)
    difficulty = models.CharField(choices=difficulty_type, max_length=10, default=easy)
    question_type = models.CharField(choices=type_of_Question, max_length=10, default=technical)
    def __str__(self):
        return str(self.question)
