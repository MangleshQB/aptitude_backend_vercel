from django.db import models
from datetime import datetime, date
from app.models import Designation
from utils.models import QBBaseModel


class KnowledgeBaseCategory(QBBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def knowledge_files_name(instance, filename):
    date_now = date.today()
    return '/'.join(['knowledge_files', str(date_now.year), str(date_now.month), str(date_now.day), filename])

class KnowledgeBaseFile(QBBaseModel):
    file = models.FileField(upload_to=knowledge_files_name)


class KnowledgeBase(QBBaseModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(KnowledgeBaseCategory,on_delete=models.CASCADE)
    description = models.TextField()
    # file = models.ManyToManyField(KnowledgeBaseFile,blank=True)
    file = models.FileField(upload_to=knowledge_files_name,blank=True,null=True)
    designation = models.ManyToManyField(Designation, blank=True)
