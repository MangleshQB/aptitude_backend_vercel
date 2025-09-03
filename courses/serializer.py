from rest_framework import serializers
from courses.models import Courses, Topic, Languages, Presenter, Videos
from utils.serializer import BaseModelSerializerCore


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']


class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ['id', 'name']


class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presenter
        fields = ['id', 'name', 'image', 'designation']


class VideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = ['title', 'description', 'file', 'order', 'category', 'thumbnail','duration']


class CoursesWithVideoSerializer(serializers.Serializer):
    languages = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    presenter = PresenterSerializer()
    videos = VideosSerializer(many=True)
    title = serializers.CharField()
    description = serializers.CharField()
    thumbnail = serializers.ImageField()
    duration =serializers.DurationField()

    def get_languages(self, instance):
        return [i.name for i in instance.languages.all()]

    def get_topic(self, instance):
        return [i.name for i in instance.topic.all()]


class CoursesSerializer(serializers.ModelSerializer):
    languages = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    presenter = PresenterSerializer()
    title = serializers.CharField()
    description = serializers.CharField()
    thumbnail = serializers.ImageField()

    class Meta:
        fields = ['id', 'languages', 'topic', 'presenter', 'title', 'description', 'thumbnail']
        model = Courses

    def get_languages(self, instance):
        return [i.name for i in instance.languages.all()]

    def get_topic(self, instance):
        return [i.name for i in instance.topic.all()]


