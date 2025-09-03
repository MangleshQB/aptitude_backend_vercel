from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.models import CustomUser
from utils.common import RelatedFieldAlternative
from utils.serializer import BaseModelSerializerCore
from .models import Questions, Choices, PersonsAnswers, Persons, TestPaper, Configuration, Conference, Topic
from app.serializers import DesignationSerializer
import datetime, calendar

def unicode(start_date):
    last_code = Conference.objects.filter(start_date=start_date).count() + 1
    code = f"ev{start_date.year}{start_date.month:02}{start_date.day:02}{last_code:02}"
    return code


class ChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choices
        fields = ['id', 'name', 'is_correct']


class RandomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = '__all__'


class CreateQuestionSerializer(BaseModelSerializerCore):
    choices = ChoicesSerializer(many=True)

    class Meta:
        model = Questions
        fields = ['choices', 'type', 'question', 'difficulty', 'question_type']

    @transaction.atomic
    def create(self, validated_data):
        choice = validated_data.pop('choices')
        question = Questions.objects.create(**validated_data)
        for choice_data in choice:
            question.choices.create(**choice_data)
        return question
    

class QuestionSerializer(BaseModelSerializerCore):
    choices = ChoicesSerializer(many=True, required=False)
    designation = DesignationSerializer(read_only=True)

    class Meta:
        model = Questions
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):

        choice = validated_data.pop('choices')
        que = validated_data['question']

        if Questions.objects.filter(question=que).exists():
            if Questions.objects.get(question=que).type == validated_data['type']:
                raise ValidationError('Question already exists')
        else:
            res = []
            for idx, sub in enumerate(choice, start=0):
                res.append(list(sub.values()))

            check_list = []
            for r in res:
                check_list.append(r[0])

            options = set()
            for x in check_list:
                if x not in options:
                    options.add(x)

            len_list = len(check_list)
            len_set = len(options)

            if len_set == len_list:
                question = Questions.objects.create(**validated_data)
                for choice_data in choice:
                    question.choices.create(**choice_data)
                return question
            else:
                ('Multiple options cannot be same.')
                raise serializers.ValidationError('Multiple options cannot be same.')

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data['type'] == 'choices':
            choices_data = validated_data.pop('choices', [])

            if instance.question != validated_data['question'] and Questions.objects.filter(question=validated_data['question']).exists():
                raise ValidationError('Question already exists')

            instance.question = validated_data.get('question', instance.question)
            instance.question_type = validated_data.get('question_type',instance.question_type)

            instance.type = validated_data.get('type', instance.type)
            instance.difficulty = validated_data.get('difficulty', instance.difficulty)

            current_choice_ids = [choice.id for choice in instance.choices.all()]
            new_choice_ids = [choice['id'] for choice in choices_data if 'id' in choice]

            for choice_id in current_choice_ids:
                if choice_id not in new_choice_ids:
                    instance.choices.filter(id=choice_id).delete()

            check_list = []
            for choice_data in choices_data:
                check_list.append(choice_data['name'])

            options = set()
            for x in check_list:
                if x not in options:
                    options.add(x)

            len_list = len(check_list)
            len_set = len(options)

            if len_set == len_list:
                for choice_data in choices_data:
                    if 'id' in choice_data:
                        choice = instance.choices.get(id=choice_data['id'])
                        choice.question = choice_data.get('question', choice.question)
                        choice.type = choice_data.get('type', choice.type)
                        choice.save()
                    else:
                        instance.choices.create(**choice_data)

                instance.save()
                return instance
            else:
                print('Multiple options cannot be same.')
                raise serializers.ValidationError('Multiple options cannot be same.')

        elif validated_data['type'] == 'text_area':

            instance.question = validated_data.get('question', instance.question)
            instance.type = validated_data.get('type', instance.type)
            instance.choices.clear()
            instance.difficulty = validated_data.get('difficulty', instance.difficulty)
            instance.question_type = validated_data.get('question_type', instance.question_type)
            instance.save()
            return instance


class PersonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persons
        fields = '__all__'

    def validate_phone(self, value):
        if len(str(value)) != 10:
            raise serializers.ValidationError('Atleat Enter 10 Digit Mobile Number')
        return value


class PersonsAnswersSerializer(serializers.ModelSerializer):
    choices = RelatedFieldAlternative(queryset=Choices.objects.all(), many=True, serializer=ChoicesSerializer)
    question = RelatedFieldAlternative(queryset=Questions.objects.all(), many=False, serializer=QuestionSerializer)

    class Meta:
        model = PersonsAnswers
        fields = '__all__'


class TestPaperSerializer(serializers.ModelSerializer):
    person = PersonsSerializer()
    answer = PersonsAnswersSerializer(many=True)

    class Meta:
        model = TestPaper
        fields = '__all__'
        read_only_fields = ('date', 'total_correct_answers', 'total_questions_asked', 'total_wrong_answers', 'result',
                            'total_not_attempted_answer')

    @transaction.atomic
    def create(self, validated_data):

        date = datetime.date.today()
        validated_data['date'] = date
        person_data = validated_data.pop('person')
        answers_data = validated_data.pop('answer')
        person = Persons.objects.create(**person_data)
        test_paper = TestPaper.objects.create(person=person, **validated_data)

        total_questions_asked = len(answers_data)
        test_paper.total_questions_asked = total_questions_asked

        correct_count = 0
        choice_type_count = 0
        is_not_attempted = 0

        for answer_data in answers_data:

            user_choices = answer_data.pop('choices')
            new = test_paper.answer.create(**answer_data)
            if answer_data['is_not_attempted'] == True:
                is_not_attempted += 1

            if len(user_choices) != 0:
                choice_type_count += 1
                new.choices.set(user_choices)
                new.save()
                question = answer_data.get('question', None)
                correct_choices = list(question.choices.filter(is_correct=True).values_list('id', flat=True))
                # print(correct_choices)
                if len(user_choices) == len(correct_choices):
                    # print("correct answer")
                    is_correct = all(u_choice.id in correct_choices for u_choice in user_choices)
                    if is_correct:
                        correct_count += 1
                        new.is_correct = True
                        new.save()

        test_paper.total_correct_answers = correct_count
        test_paper.final_result = correct_count
        test_paper.total_wrong_answers = choice_type_count - correct_count
        test_paper.total_questions_asked = len(answers_data)
        test_paper.total_not_attempted_answer = is_not_attempted
        test_paper.total_partially_correct_answers = 0
        test_paper.save()
        return test_paper


class TestPaperUpdateSerializer(serializers.ModelSerializer):
    answer = PersonsAnswersSerializer(many=True)
    person = PersonsSerializer()

    class Meta:
        model = TestPaper
        fields = "__all__"


class AptitudeConfigurationSerializer(BaseModelSerializerCore):
    class Meta:
        model = Configuration
        fields = ['time_limit', 'no_questions_to_asked']


class LeaderboardSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.name')
    designation_name = serializers.CharField(source='person.designation.name')

    class Meta:
        model = TestPaper
        fields = ('person_name', 'designation_name', 'final_result')


class SlotsSerializer(serializers.Serializer):
    start = serializers.TimeField()
    end = serializers.TimeField()


weekday_map = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6,
}


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = '__all__'
        exclude = ['password', 'updated_at', 'created_at', 'last_login', 'date_joined']


class ConferenceRoomViewSerializer(BaseModelSerializerCore):
    week_day = serializers.MultipleChoiceField(choices=Conference.DAYS, required=False)
    repeat_every_days = serializers.CharField(required=False, allow_blank=True)
    repeat_every_weeks = serializers.CharField(required=False, allow_blank=True)
    repeat_every_months = serializers.CharField(required=False, allow_blank=True)
    selectedSlots = SlotsSerializer(many=True, write_only=True)
    event_code = serializers.CharField(required=False)
    topics = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True, required=False,allow_null=True,allow_empty=True)

    class Meta:
        model = Conference
        fields = "__all__"
        read_only_fields = ['end_date', 'start_time', 'end_time']
        # depth = 1

    @transaction.atomic
    def create(self, validated_data):
        global weekday_map
        repeatType = validated_data['repeat']
        start_date = validated_data['start_date']
        title = validated_data['title']
        agenda = validated_data['agenda']

        presenting = validated_data.pop('presenting', [])
        attending = validated_data.pop('attending', [])
        topic = validated_data.pop('topic', [])

        # if datetime.datetime.now().date() > start_date:
        #     raise serializers.ValidationError('Cannot book the given date !!')
        conferences = []
        if repeatType == Conference.NEVER:
            event_code = unicode(start_date)
            end_date = start_date
            selectedSlots = validated_data.pop('selectedSlots')
            created_conferences = []

            for slot in selectedSlots:
                start_time = slot['start']
                end_time = slot['end']

                if not datetime.datetime.combine(start_date, end_time) < datetime.datetime.now():
                    conference = Conference.objects.create(
                        title=title,
                        agenda=agenda,
                        repeat=repeatType,
                        created_by=self.context['user'],
                        start_date=start_date,
                        end_date=end_date,
                        start_time=start_time,
                        end_time=end_time,
                        event_code=event_code
                    )
                    conference.presenting.set(presenting)
                    conference.attending.set(attending)
                    conference.topic.set(topic)
                    created_conferences.append(conference)
                    conferences.extend(created_conferences)

            return conferences[0] if conferences else None

        if repeatType == Conference.DAILY:

            event_code = unicode(start_date)
            days = int(validated_data['repeat_every_days'])
            selectedSlots = validated_data.pop('selectedSlots')
            current_time = datetime.datetime.now().time()
            start_date = datetime.datetime.combine(start_date, current_time)
            end_of_month = datetime.date(start_date.year, start_date.month,
                                         calendar.monthrange(start_date.year, start_date.month)[1])
            date_start = start_date

            while date_start.date() <= end_of_month:
                for slot in selectedSlots:
                    start_time = slot['start']
                    end_time = slot['end']

                    if not Conference.objects.filter(
                            Q(start_date=date_start) & Q(end_date=date_start) & Q(start_time=start_time) & Q(
                                end_time=end_time)).exists():
                        if not datetime.datetime.combine(start_date, end_time) < datetime.datetime.now():
                            conference = Conference.objects.create(
                                title=title,
                                agenda=agenda,
                                repeat=repeatType,
                                created_by=self.context['user'],
                                start_date=date_start.date(),
                                end_date=date_start.date(),
                                start_time=start_time,
                                end_time=end_time,
                                repeat_every_days=days,
                                event_code=event_code
                            )
                            conference.presenting.set(presenting)
                            conference.attending.set(attending)
                            conference.topic.set(topic)


                date_start += datetime.timedelta(days=days + 1)

            return conference

        if repeatType == Conference.WEEKLY:
            event_code = unicode(start_date)
            weeks = int(validated_data['repeat_every_weeks'])
            week_days = validated_data['week_day']
            selectedSlots = validated_data.pop('selectedSlots')
            current_time = datetime.datetime.now().time()
            start_date = datetime.datetime.combine(start_date, current_time)

            end_of_year = datetime.datetime(start_date.year + 1, 1, 1)
            total_weeks = ((end_of_year - start_date).days // 7 + 1) + 1
            start_day_of_week = start_date.weekday()

            for week_offset in range(0, total_weeks, weeks + 1):

                for day_name in week_days:
                    day_of_week = weekday_map[day_name]
                    day_offset = (day_of_week - start_day_of_week) + (week_offset * 7)
                    date_start = start_date + datetime.timedelta(days=day_offset)
                    end_date = date_start

                    if date_start > end_of_year:
                        continue

                    if start_date.date() > date_start.date():
                        continue

                    for slot in selectedSlots:
                        start_time = slot['start']
                        end_time = slot['end']

                        if not Conference.objects.filter(
                                Q(start_date=date_start.date()) & Q(end_date=end_date.date()) &
                                Q(start_time=start_time) & Q(end_time=end_time)).exists():

                            if not datetime.datetime.combine(date_start, end_time) < datetime.datetime.now():
                                conference = Conference.objects.create(
                                    title=title,
                                    agenda=agenda,
                                    repeat=repeatType,
                                    created_by=self.context['user'],
                                    start_date=date_start.date(),
                                    end_date=end_date.date(),
                                    start_time=start_time,
                                    end_time=end_time,
                                    repeat_every_weeks=weeks,
                                    week_day=week_days,
                                    event_code=event_code
                                )
                                conference.presenting.set(presenting)
                                conference.attending.set(attending)
                                conference.topic.set(topic)
                                # conferences.extend(conference)
            return conference

        if repeatType == Conference.MONTHLY:

            event_code = unicode(start_date)
            date = int(validated_data['repeat_every_months'])
            selectedSlots = validated_data.pop('selectedSlots')
            current_time = datetime.datetime.now().time()
            start_date = datetime.datetime.combine(datetime.date(start_date.year, start_date.month, date), current_time)
            year = start_date.year

            for slot in selectedSlots:
                date_start = start_date
                end_date = date_start
                start_time = slot['start']
                end_time = slot['end']

                if not Conference.objects.filter(
                        Q(start_date=date_start) & Q(end_date=end_date) & Q(start_time=start_time) & Q(
                            end_time=end_time)).exists():
                    if not datetime.datetime.combine(date_start, end_time) < datetime.datetime.now():
                        conference = Conference.objects.create(
                            title=title,
                            agenda=agenda,
                            repeat=repeatType,
                            created_by=self.context['user'],
                            start_date=date_start.date(),
                            end_date=end_date.date(),
                            repeat_every_months=date,
                            start_time=start_time,
                            end_time=end_time,
                            event_code=event_code
                        )
                        conference.presenting.set(presenting)
                        conference.attending.set(attending)
                        conference.topic.set(topic)
                        conferences.append(conference)

            for month in range(start_date.month + 1, 13):
                last_day_of_month = calendar.monthrange(year, month)[1]
                day_to_use = min(date, last_day_of_month)
                date_start = datetime.datetime.combine(datetime.date(year, month, day_to_use), current_time)
                end_date = date_start

                for slot in selectedSlots:
                    start_time = slot['start']
                    end_time = slot['end']

                    if not Conference.objects.filter(
                            Q(start_date=date_start) & Q(end_date=end_date) & Q(start_time=start_time) & Q(
                                end_time=end_time)).exists():
                        if not datetime.datetime.combine(date_start, end_time) < datetime.datetime.now():
                            conference = Conference.objects.create(
                                title=title,
                                agenda=agenda,
                                repeat=repeatType,
                                created_by=self.context['user'],
                                start_date=date_start.date(),
                                end_date=end_date.date(),
                                repeat_every_months=date,
                                start_time=start_time,
                                end_time=end_time,
                                event_code=event_code
                            )
                            conference.presenting.set(presenting)
                            conference.attending.set(attending)
                            conference.topic.set(topic)
                            conferences.append(conference)

            # print('Conf = ', conferences)
            return conferences[0]

    @transaction.atomic
    def update(self, instance, validated_data):
        global weekday_map
        title = validated_data.get('title', instance.title)
        agenda = validated_data.get('agenda', instance.agenda)
        event_code = instance.event_code
        repeat = validated_data['repeat']
        created_by = instance.created_by

        old_start_date = Conference.objects.filter(event_code=event_code).order_by('start_date').values('start_date').first()['start_date']

        today_date = datetime.datetime.now().date()

        selectedSlots = validated_data.pop('selectedSlots', [])

        old_conference = Conference.objects.filter(event_code=event_code, start_date__gte=today_date,start_time =selectedSlots[0]['start'] )

        old_conference.delete()


        print("selectedSlots-------->", selectedSlots)

        presenting = validated_data.pop('presenting', [])
        attending = validated_data.pop('attending', [])
        topic = validated_data.pop('topic', [])

        created_conferences = []

        if repeat == Conference.NEVER:
            start_date = validated_data['start_date']

            if old_start_date < start_date:
                start_date = old_start_date

            if today_date > start_date:
                start_date = today_date

            end_date = start_date

            for slot in selectedSlots:
                start_time = slot['start']
                end_time = slot['end']
                print("step 1")
                if not Conference.objects.filter(Q(start_date=start_date) & Q(end_date=start_date) & Q(start_time=start_time) & Q(end_time=end_time)).exists():
                    conference = Conference.objects.create(
                        title=title,
                        agenda=agenda,
                        repeat=repeat,
                        created_by=created_by,
                        updated_by=self.context['user'],
                        start_date=start_date,
                        end_date=end_date,
                        start_time=start_time,
                        end_time=end_time,
                        event_code=event_code
                    )
                    print("step 2")
                    conference.presenting.set(presenting)
                    conference.attending.set(attending)
                    conference.topic.set(topic)

                    created_conferences.append(conference)
                    print("in for loop:", conference)
            print("step 3")
            print("out of for loop:", conference)
            print("list of conferences:", created_conferences)
            return conference

        if repeat == Conference.DAILY:

            days = int(validated_data['repeat_every_days'])
            start_date = validated_data['start_date']

            if old_start_date < start_date:
                start_date = old_start_date

            if today_date > start_date:
                start_date = today_date

            current_time = datetime.datetime.now().time()
            start_date = datetime.datetime.combine(start_date, current_time)
            end_of_month = datetime.date(start_date.year, start_date.month,
                                         calendar.monthrange(start_date.year, start_date.month)[1])

            date_start = start_date

            while date_start.date() <= end_of_month:
                for slot in selectedSlots:
                    start_time = slot['start']
                    end_time = slot['end']

                    if not Conference.objects.filter(
                            Q(start_date=date_start.date()) & Q(end_date=date_start.date()) & Q(
                                start_time=start_time) & Q(end_time=end_time)).exists():
                        if not datetime.datetime.combine(date_start, end_time) < datetime.datetime.now():
                            conference = Conference.objects.create(
                                title=title,
                                agenda=agenda,
                                repeat=repeat,
                                created_by=created_by,
                                updated_by=self.context['user'],
                                start_date=date_start.date(),
                                end_date=date_start.date(),
                                start_time=start_time,
                                end_time=end_time,
                                repeat_every_days=days,
                                event_code=event_code
                            )
                            conference.presenting.set(presenting)
                            conference.attending.set(attending)
                            conference.topic.set(topic)
                            # created_conferences.append(conference)

                date_start += datetime.timedelta(days=days + 1)
            return instance

        if repeat == Conference.WEEKLY:

            conference = None

            event_code = instance.event_code
            start_date = validated_data['start_date']

            if old_start_date < start_date:
                start_date = old_start_date

            if today_date < start_date:
                start_date = today_date

            weeks = int(validated_data['repeat_every_weeks'])
            week_days = validated_data['week_day']
            # selectedSlots = validated_data.pop('selectedSlots')
            current_time = datetime.datetime.now().time()
            start_date = datetime.datetime.combine(start_date, current_time)

            end_of_year = datetime.datetime(start_date.year + 1, 1, 1)

            total_weeks = ((end_of_year - start_date).days // 7 + 1) + 1

            start_day_of_week = start_date.weekday()

            for week_offset in range(0, total_weeks, weeks + 1):

                for day_name in week_days:
                    day_of_week = weekday_map[day_name]

                    if day_of_week >= start_day_of_week:
                        day_offset = (day_of_week - start_day_of_week) + (week_offset * 7)
                    else:
                        day_offset = (day_of_week - start_day_of_week) + ((week_offset + 1) * 7)
                    date_start = start_date + datetime.timedelta(days=day_offset)
                    end_date = date_start

                    if date_start > end_of_year:
                        continue

                    if old_start_date > date_start.date():
                        continue

                    for slot in selectedSlots:
                        start_time = slot['start']
                        end_time = slot['end']

                        if not Conference.objects.filter(
                                Q(start_date=date_start.date()) & Q(end_date=end_date.date()) &
                                Q(start_time=start_time) & Q(end_time=end_time)).exists():
                            if not datetime.datetime.combine(date_start, end_time) < datetime.datetime.now():
                                conference = Conference.objects.create(
                                    title=title,
                                    agenda=agenda,
                                    repeat=repeat,
                                    created_by=created_by,
                                    updated_by=self.context['user'],
                                    start_date=date_start.date(),
                                    end_date=end_date.date(),
                                    start_time=start_time,
                                    end_time=end_time,
                                    repeat_every_weeks=weeks,
                                    week_day=week_days,
                                    event_code=event_code
                                )
                                conference.presenting.set(presenting)
                                conference.attending.set(attending)
                                conference.topic.set(topic)

            # return conference[0]
            return instance
            # if conference is not None:
            #     return conference
            # else:
            #     return None

        if repeat == Conference.MONTHLY:

            start_date = validated_data['start_date']

            if old_start_date < start_date:
                start_date = old_start_date

            if today_date > start_date:
                start_date = today_date

            date = int(validated_data['repeat_every_months'])
            # selectedSlots = validated_data.pop('selectedSlots')
            current_time = datetime.datetime.now().time()
            start_date = datetime.datetime.combine(datetime.date(start_date.year, start_date.month, date), current_time)
            year = start_date.year

            for slot in selectedSlots:
                date_start = start_date
                end_date = date_start
                start_time = slot['start']
                end_time = slot['end']

                # if start_date.date() > today_date:
                #     continue

                if not Conference.objects.filter(
                        Q(start_date=date_start) & Q(end_date=end_date) & Q(start_time=start_time) & Q(
                            end_time=end_time)).exists():
                    if not datetime.datetime.combine(date_start, end_time) < datetime.datetime.now():
                        conference = Conference.objects.create(
                            title=title,
                            agenda=agenda,
                            repeat=repeat,
                            created_by=created_by,
                            updated_by=self.context['user'],
                            start_date=date_start.date(),
                            end_date=end_date.date(),
                            start_time=start_time,
                            repeat_every_months=date,
                            end_time=end_time,
                            event_code=event_code
                        )
                        conference.presenting.set(presenting)
                        conference.attending.set(attending)
                        conference.topic.set(topic)

            for month in range(start_date.month + 1, 13):
                last_day_of_month = calendar.monthrange(year, month)[1]
                day_to_use = min(date, last_day_of_month)
                date_start = datetime.datetime.combine(datetime.date(year, month, day_to_use), current_time)
                end_date = date_start

                for slot in selectedSlots:
                    start_time = slot['start']
                    end_time = slot['end']

                    if not Conference.objects.filter(
                            Q(start_date=date_start) & Q(end_date=end_date) & Q(start_time=start_time) & Q(
                                end_time=end_time)).exists():
                        if not datetime.datetime.combine(date_start, end_time) < datetime.datetime.now():
                            conference = Conference.objects.create(
                                title=title,
                                agenda=agenda,
                                repeat=repeat,
                                updated_by=self.context['user'],
                                created_by=created_by,
                                start_date=date_start.date(),
                                end_date=end_date.date(),
                                repeat_every_months=date,
                                start_time=start_time,
                                end_time=end_time,
                                event_code=event_code
                            )
                            conference.presenting.set(presenting)
                            conference.attending.set(attending)
                            conference.topic.set(topic)

            return conference



class TopicViewSetSerializer(BaseModelSerializerCore):
    class Meta:
        model = Topic
        fields = '__all__'

    def create(self, validated_data):
        topic = Topic.objects.create(**validated_data)
        topic.created_by = self.context['user']
        topic.save()
        return topic

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.updated_by = self.context['user']
        instance.save()
        return instance


class UpcomingConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conference
        fields = "__all__"
        depth = 1


class getTopPresenterSerializer(serializers.Serializer):
    id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    num_presented = serializers.IntegerField()


class getTopTopicsSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    num_topic = serializers.IntegerField()

class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()