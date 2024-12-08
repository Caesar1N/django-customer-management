from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Customer, Invoice, MessageSchedule
from .forms import CustomerForm, InvoiceForm, MessageScheduleForm
from threading import Timer
from datetime import timedelta
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib import messages
from PIL import Image
import os
from django.core.files.base import ContentFile
from io import BytesIO

# 1. Customer Create View (Updated to Include Message Scheduling)
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            
            # Check if the user wants to schedule a message for this customer
            if form.cleaned_data.get('schedule_message'):
                message_content = form.cleaned_data.get('message_content')
                days_from_today = form.cleaned_data.get('days_from_today')
                message_type = form.cleaned_data.get('message_type')

                # Only create a message if all the required fields are provided
                if message_content and days_from_today and message_type:
                    schedule_date = timezone.now() + timedelta(days=days_from_today)
                    # Create and save the message schedule
                    MessageSchedule.objects.create(
                        customer=customer,
                        message_content=message_content,
                        schedule_date=schedule_date,
                        message_type=message_type,
                        is_sent=False,
                        is_reminder_sent=False
                    )
            
            # Add a success message after saving the customer
            messages.success(request, f"Customer '{customer.name}' added successfully!")

            # Handle AJAX request success
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Customer added successfully!'})

            # If the request is not an AJAX request, redirect to customer list
            return redirect('customer_list')
        else:
            # Handle form validation errors for both AJAX and non-AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})

    else:
        # If GET request, display an empty form
        form = CustomerForm()

    # Render the customer creation form
    return render(request, 'crm/form.html', {'form': form, 'title': 'Add Customer'})

# 2. Invoice Create View (Updated for Modern AJAX Handling)
def invoice_create(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.customer = customer

            # Handle the receipt file - convert image to PDF if needed
            uploaded_file = form.cleaned_data['receipt']
            if uploaded_file.content_type.startswith('image'):
                # Convert image to PDF using Pillow
                try:
                    image = Image.open(uploaded_file)
                    pdf_file = BytesIO()
                    image.convert('RGB').save(pdf_file, format='PDF')

                    # Construct a new ContentFile for the PDF
                    pdf_file.seek(0)
                    invoice.receipt.save(
                        f"invoice_{invoice.customer.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf",
                        ContentFile(pdf_file.read()),
                        save=False
                    )
                except Exception as e:
                    form.add_error('receipt', f"Error converting image to PDF: {str(e)}")
                    return render(request, 'crm/form.html', {'form': form, 'customer': customer, 'title': 'Add Invoice'})
            else:
                # Save the original PDF file if it's already a PDF
                invoice.receipt = uploaded_file

            invoice.save()  # Save the invoice to the database
            # Handle AJAX request success
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Invoice created successfully!'})
            return redirect('customer_detail', customer_id=customer.id)
        else:
            # Handle form validation errors for both AJAX and non-AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # Pre-populate the form with the customer ID, although it's hidden in the form
        form = InvoiceForm(initial={'customer': customer})

    # Render the invoice form for adding a new invoice to a specific customer
    return render(request, 'crm/form.html', {
        'form': form,
        'customer': customer,
        'title': f'Add Invoice for {customer.name}'
    })

# 3. Message Schedule View (For Scheduling Message after Customer is Created)
def message_schedule(request, customer_id):
    # Fetch the customer instance or return a 404 if not found
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        form = MessageScheduleForm(request.POST)
        if form.is_valid():
            # Save the form and schedule the message
            message = form.save(commit=False)
            days_from_today = form.cleaned_data['days_from_today']
            message.schedule_date = timezone.now() + timedelta(days=days_from_today)
            message.customer = customer  # Set the customer relationship
            message.save()  # Save the message schedule to the database

            # Schedule the message to be sent
            schedule_message_send(message)

            # Handle AJAX request success response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Message scheduled successfully!'})

            # For non-AJAX request: Redirect back to customer list
            messages.success(request, 'Message scheduled successfully!')
            return redirect('customer_list')

        else:
            # Handle form validation errors for AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})

            # If non-AJAX request, re-render the form with validation errors
            return render(request, 'crm/form.html', {
                'form': form,
                'customer': customer,
                'title': f'Schedule New Message for {customer.name}'
            })

    # GET request to render the form for scheduling a message
    else:
        form = MessageScheduleForm(initial={'customer': customer})

    # Determine the action URL for the form submission
    form_action_url = reverse('message_schedule', args=[customer.id])

    # Render the form page or modal content
    return render(request, 'crm/form.html', {
        'form': form,
        'customer': customer,
        'title': f'Schedule New Message for {customer.name}',
        'form_action_url': form_action_url,
    })

# Function to Schedule Message Sending
def schedule_message_send(message):
    delay = (message.schedule_date - timezone.now()).total_seconds()
    Timer(delay, send_message, [message]).start()

# Function to Simulate Sending a Message
def send_message(message):
    # Simulating message sending
    print(f"Sending {message.message_type} to {message.customer.phone_number}: {message.message_content}")
    message.is_sent = True
    message.save()

# 4. Mark Reminder Sent (Updated for Modern AJAX Handling)
def mark_reminder_sent(request, message_id):
    message = get_object_or_404(MessageSchedule, id=message_id)
    if request.method == 'POST':
        message.is_reminder_sent = True
        message.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Reminder marked as sent!'})
    return redirect('customer_list')

# Customer List Function
def customer_list(request):
    customers = Customer.objects.all()
    # Get messages that are due and haven't been acknowledged
    now = timezone.now()
    due_messages = MessageSchedule.objects.filter(schedule_date__lte=now, is_reminder_sent=False, is_sent=False)
    return render(request, 'crm/customer_list.html', {
        'customers': customers,
        'due_messages': due_messages
    })

# Customer Detail
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    invoices = Invoice.objects.filter(customer=customer)
    messages = MessageSchedule.objects.filter(customer=customer, is_sent=False)  # Fetch unsent messages
    return render(request, 'crm/customer_detail.html', {
        'customer': customer,
        'invoices': invoices,
        'messages': messages,
    })

# Send Invoice via WhatsApp
def send_invoice_whatsapp(request, customer_id, invoice_id):
    customer = get_object_or_404(Customer, id=customer_id)
    invoice = get_object_or_404(Invoice, id=invoice_id, customer=customer)

    # Mockup for sending WhatsApp
    phone_number = customer.phone_number
    if len(phone_number) >= 10:
        print(f"Sending WhatsApp message to {phone_number} with invoice details.")
        # Here you would integrate with a WhatsApp API like Twilio or WhatsApp Business API.
        message = f"Invoice #{invoice.id} Amount: ${invoice.amount} has been sent to you. Please find the receipt attached."
        print(f"WhatsApp message content: {message}")
        return JsonResponse({'success': True, 'message': 'Invoice sent via WhatsApp successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid phone number.'})

# Send Invoice via Email
def send_invoice_email(request, customer_id, invoice_id):
    customer = get_object_or_404(Customer, id=customer_id)
    invoice = get_object_or_404(Invoice, id=invoice_id, customer=customer)

    # Sending Email using Django's send_mail function
    subject = f"Invoice #{invoice.id} from Customer Management App"
    message = f"Dear {customer.name},\n\nPlease find the details of your invoice.\n\nInvoice Amount: ${invoice.amount}\nDate: {invoice.date_created}\n\nThank you."
    recipient_list = [customer.email]

    try:
        send_mail(subject, message, 'noreply@example.com', recipient_list)
        return JsonResponse({'success': True, 'message': 'Invoice sent via email successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})