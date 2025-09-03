from django.db import models
from aptitude_test.models.person_answer import PersonsAnswers
from aptitude_test.models.persons import Persons
from utils.models import QBBaseModel


class TestPaper(QBBaseModel):
    person = models.ForeignKey(Persons, on_delete=models.CASCADE)
    date = models.DateField()
    answer = models.ManyToManyField(PersonsAnswers)
    total_correct_answers = models.IntegerField(blank=True, null=True)
    total_questions_asked = models.IntegerField(blank=True, null=True)
    total_wrong_answers = models.IntegerField(blank=True, null=True)
    total_not_attempted_answer = models.IntegerField(blank=True, null=True)
    total_partially_correct_answers = models.IntegerField(blank=True, null=True)
    final_result = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.total_correct_answers)
    