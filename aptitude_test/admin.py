from django.contrib import admin
from .models import Choices, Questions, PersonsAnswers, Configuration, Persons, TestPaper, Conference, Topic


@admin.register(Choices)
class ChoicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_correct')


@admin.register(Questions)
class ChoicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'designation', 'type', 'question_type',)

# @admin.register(Holiday)
# class HolidayAdmin(admin.ModelAdmin):
#     list_display = ('id',)


@admin.register(PersonsAnswers)
class ChoicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'type')
    search_fields = ['id']


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'designation', 'no_questions_to_asked', 'time_limit')


@admin.register(Persons)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'designation', 'highest_education', 'phone']
    search_fields = ['email', 'name', 'phone']


@admin.register(TestPaper)
class TestPaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'person', 'date', 'total_correct_answers', 'total_wrong_answers', 'total_questions_asked']


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']


# @admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     list_display = ['id', 'first_name', 'last_name']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']