from django.db import models
from .ticket_category import TicketCategory
from utils.models import QBBaseModel


class TicketSubCategory(QBBaseModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TicketCategory,on_delete=models.CASCADE, related_name='ticket_subcategory_category', related_query_name='ticket_subcategory_category')

    def __str__(self):
        return self.name