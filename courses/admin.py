from django.contrib import admin
import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip
from courses.models import Topic, Languages, Presenter, Courses, Category, Videos


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Languages)
class LanguagesAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Presenter)
class PresenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'image']


@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']

    def save_model(self, request, obj, form, change):
        # Save the course instance first
        super().save_model(request, obj, form, change)

        if 'videos' in form.changed_data:
            data = form.cleaned_data['videos']
            total_duration = datetime.timedelta()
            for video in data:
                if video.duration:
                    total_duration += video.duration
            obj.duration = total_duration
            obj.save()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Videos)
class VideosAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'file', 'order', 'category']
    readonly_fields = ['duration']

    def save_model(self, request, obj, form, change):
        if obj.file:
            super().save_model(request, obj, form, change)
            file_path = obj.file.path
            video = VideoFileClip(file_path)
            obj.duration = datetime.timedelta(seconds=video.duration)
            video.close()
            obj.save()
        else:
            super().save_model(request, obj, form, change)

