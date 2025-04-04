from django.urls import path
from .views import initiate_payment, payment_success, initiate_payment_for_plan

urlpatterns=[
    path('initiate_payment/',initiate_payment, name='initiate_payment'),
    path('initiate_payment_for_plan/',initiate_payment_for_plan, name='initiate_payment_for_plan'),
    path('payment-success/',payment_success, name='payment_success'),
]
