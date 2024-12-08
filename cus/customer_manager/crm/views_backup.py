from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Invoice, MessageSchedule, Treatment
from .forms import CustomerForm, InvoiceForm, MessageScheduleForm
from threading import Timer
from django.utils import timezone
import time

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    invoices = Invoice.objects.filter(customer=customer)
    scheduled_messages = MessageSchedule.objects.filter(customer=customer)
    return render(request, 'crm/customer_detail.html', {
        'customer': customer,
        'invoices': invoices,
        'scheduled_messages': scheduled_messages,
    })

def customer_list(request):
    customers = Customer.objects.all()
    now = timezone.now()
    due_messages = MessageSchedule.objects.filter(schedule_date__lte=now, is_reminder_sent=False, is_sent=False)

    return render(request, 'crm/customer_list.html', {
        'customers': customers,
        'due_messages': due_messages
    })

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'crm/form.html', {'form': form,'title': 'Add New Customer'})

def invoice_create(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.customer = customer
            invoice.save()
            return redirect('customer_list')
    else:
        form = InvoiceForm()
    return render(request, 'crm/form.html', {'form': form, 'customer': customer,'title': 'Add New Invoice'})

def message_schedule(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        form = MessageScheduleForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.customer = customer
            message.save()
            schedule_message_send(message)  # Schedule message sending
            return redirect('customer_list')
    else:
        form = MessageScheduleForm()
    return render(request, 'crm/form.html', {'form': form, 'customer': customer,'title': 'Schedule New Message'})

def schedule_message_send(message):
    delay = (message.schedule_date - timezone.now()).total_seconds()
    Timer(delay, send_message, [message]).start()

def send_message(message):
    # Simulating message sending
    print(f"Sending {message.message_type} to {message.customer.phone_number}: {message.message_content}")
    message.is_sent = True
    message.save()

def mark_reminder_sent(request, message_id):
    message = get_object_or_404(MessageSchedule, id=message_id)
    if request.method == 'POST':
        message.is_reminder_sent = True
        message.save()
    return redirect('customer_list')
