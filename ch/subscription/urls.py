from django.urls import path
from .views import initiate_payment, payment_success

urlpatterns=[
    path('initiate_payment/',initiate_payment, name='initiate_payment'),
    path('payment-success/',payment_success, name='payment_success'),
]
