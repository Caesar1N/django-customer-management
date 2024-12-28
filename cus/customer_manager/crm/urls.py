from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('customer/create/', views.customer_create, name='customer_create'),
    path('customer/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customer/update/<int:customer_id>/', views.customer_update, name='customer_update'),
    path('customer/delete/<int:customer_id>/', views.customer_delete, name='customer_delete'), 
    path('invoice/create/<int:customer_id>/', views.invoice_create, name='invoice_create'),
    path('invoice/send_whatsapp/<int:customer_id>/<int:invoice_id>/', views.send_invoice_whatsapp, name='send_invoice_whatsapp'),
    path('invoice/send_email/<int:customer_id>/<int:invoice_id>/', views.send_invoice_email, name='send_invoice_email'),
    path('message/schedule/<int:customer_id>/', views.message_schedule, name='message_schedule'),
    path('mark-reminder-sent/<int:message_id>/', views.mark_reminder_sent, name='mark_reminder_sent'),
]
