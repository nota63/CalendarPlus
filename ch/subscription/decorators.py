from django.shortcuts import redirect
from .models import Payment

def payment_required(view_func):
    def wrapper(request, *args, **kwargs):
        has_paid = Payment.objects.filter(user=request.user, is_paid=True).exists()
        if not has_paid:
            return redirect('pay')
        return view_func(request, *args, **kwargs)
    return wrapper
