from django import forms
from .models import Customer, Treatment, Invoice, MessageSchedule
from datetime import timedelta
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import imghdr

def validate_file_type(value):
    allowed_mime_types = ['application/pdf', 'image/jpeg', 'image/png']
    if value.content_type not in allowed_mime_types:
        raise ValidationError("Only PDF or image files (jpeg, png) are allowed.")

def validate_phone_number(value):
    if len(value) < 10 or not value.isdigit():
        raise ValidationError("Phone number must be at least 10 digits and numeric.")

class CustomerForm(forms.ModelForm):

    email = forms.EmailField(
        required=True,
        validators=[validate_email],
        label="Email",
    )
    phone_number = forms.CharField(
        required=True,
        validators=[validate_phone_number],
        label="Phone Number",
    )

    # New fields for message scheduling
    schedule_message = forms.BooleanField(
        required=False, initial=False, label="Schedule a Message for This Customer?"
    )
    message_content = forms.CharField(
        required=False, widget=forms.Textarea, label="Message Content"
    )
    days_from_today = forms.IntegerField(
        min_value=1,
        required=False,
        label="Days from Today",
        help_text="Enter the number of days from today after which the message should be scheduled." 
    )
    message_type = forms.ChoiceField(
        required=False,
        choices=MessageSchedule.MESSAGE_TYPES,
        label="Message Type"
    )

    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'treatment': forms.CheckboxSelectMultiple(),  # Using checkboxes to allow multiple selections
        }

    problem = forms.CharField(widget=forms.Textarea, required=True, label="Patient's Problem")
    age = forms.IntegerField(min_value=0, required=True, label="Age")
    sex = forms.ChoiceField(choices=Customer.SEX_CHOICES, required=True, label="Sex")
    treatment = forms.ModelMultipleChoiceField(
        queryset=Treatment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Treatment",
    )

class InvoiceForm(forms.ModelForm):
    receipt = forms.FileField(validators=[validate_file_type], required=True)

    class Meta:
        model = Invoice
        fields = ['customer', 'amount', 'receipt']
        widgets = {
            'customer': forms.HiddenInput()  # Make the customer field hidden
        }

class MessageScheduleForm(forms.ModelForm):
    days_from_today = forms.IntegerField(
        min_value=1,
        required=True,
        label="Days from Today",
        help_text="Enter the number of days from today after which the message should be scheduled."
    )

    class Meta:
        model = MessageSchedule
        exclude = ['schedule_date']  # Remove 'schedule_date' from form fields

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calculate the actual schedule_date based on days_from_today
        days_offset = self.cleaned_data['days_from_today']
        instance.schedule_date = timezone.now() + timedelta(days=days_offset)
        if commit:
            instance.save()
        return instance
