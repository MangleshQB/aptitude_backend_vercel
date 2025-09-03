from app.models import CustomUser
from configuration.models import TicketCategory, TicketSubCategory
from utils.models import QBBaseModel
from django.db import models
from datetime import datetime

def ticket_file_name(instance, filename):
    date = datetime.now()
    return '/'.join(['tickets', str(instance.created_by.id), str(date.year), str(date.month), str(date.day), filename])

class Ticket(QBBaseModel):
    low = 'Low'
    medium = 'Medium'
    high = 'High'
    priority_choices = (
        (low, 'Low'),
        (medium, 'Medium'),
        (high, 'High')
    )

    pending = 'pending'
    resolved = 'resolved'
    in_progress = 'in_progress'
    status_choices = (
        (pending, 'Pending'),
        (resolved, 'Resolved'),
        (in_progress, 'In-Progress')
    )

    category= models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    sub_category= models.ForeignKey(TicketSubCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    code = models.CharField(max_length=255)
    description = models.TextField()
    priorities = models.CharField(choices=priority_choices,max_length=120, default=low)
    status = models.CharField(choices=status_choices,max_length=120, default=pending)
    assigned_to = models.ForeignKey(CustomUser,on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to=ticket_file_name, blank=True, null=True)
    notify_to = models.ManyToManyField(CustomUser, blank=True, related_name='ticket_notify_to')
    # email_message_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        default_permissions = ["add", "change", "delete", "view", 'all', 'team', "owned"]