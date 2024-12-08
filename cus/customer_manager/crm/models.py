from django.db import models

# Create your models here.
from django.db import models
from datetime import datetime, timedelta

class Customer(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    TREATMENT_CHOICES = [
        ('Physiotherapy', 'Physiotherapy'),
        ('Chiropractic', 'Chiropractic'),
        ('Osteopathy', 'Osteopathy'),
        ('Cupping Therapy', 'Cupping Therapy'),
        ('Hijama', 'Hijama'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    problem = models.TextField(verbose_name="Patient's Problem")  # Added field for patient's problem
    age = models.PositiveIntegerField()  # Added field for age
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)  # Added field for sex with a choice dropdown
    treatment = models.ManyToManyField('Treatment')  # Added field for multiple treatment selection


    def __str__(self):
        return self.name

class Treatment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(upload_to='receipts/')

    def __str__(self):
        return f"Invoice {self.id} - {self.customer.name}"

class MessageSchedule(models.Model):
    MESSAGE_TYPES = (
        ('SMS', 'SMS'),
        ('WhatsApp', 'WhatsApp'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message_content = models.TextField()
    schedule_date = models.DateTimeField()
    message_type = models.CharField(choices=MESSAGE_TYPES, max_length=10)
    is_sent = models.BooleanField(default=False)
    is_reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Message to {self.customer.name} at {self.schedule_date}"
