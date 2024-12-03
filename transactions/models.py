from django.db import models
from members.models import Member

# Create your models here.

class Transaction(models.Model):
  '''comment here'''
  member = models.ForeignKey(Member, on_delete=models.SET_NULL, related_name="transactions", null=True, blank=True)

  description = models.CharField(
    max_length = 200)

  reference_number = models.CharField(
    max_length = 20)

  amount = models.DecimalField(
    max_digits=6,
    decimal_places=2)

  transaction_date = models.DateTimeField(
    auto_now_add=True)

  def __str__(self):
    if self.member==None:
      return self.reference_number
    else:
      return self.member.long_name + " - " + self.reference_number