from django.db import models

from app.models import Designation
from utils.models import QBBaseModel


class Persons(QBBaseModel):
    easy = 'easy'
    medium = 'medium'
    hard = 'hard'

    difficulty_type = (
        (easy, 'Easy'),
        (medium, 'Medium'),
        (hard, 'Hard')
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    difficulty = models.CharField(choices=difficulty_type, max_length=10, default=easy)
    phone = models.IntegerField(blank=True, null=True)
    highest_education = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)