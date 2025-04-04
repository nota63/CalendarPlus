from django.shortcuts import render, redirect
from django.conf import settings
import razorpay
from .models import Payment,PremiumPlan
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponseBadRequest


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def initiate_payment(request):
    plans = PremiumPlan.objects.filter(is_active=True)

    context = {
        'plans': plans,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'user': request.user,
    }

    return render(request, 'subscription/subscribe/payment.html', context)


# step 2 - Initiate payment for plan
# @require_POST
def initiate_payment_for_plan(request):
    plan_id = request.POST.get('plan_id')
    try:
        plan = PremiumPlan.objects.get(id=plan_id, is_active=True)
    except PremiumPlan.DoesNotExist:
        return redirect('subscription:initiate_payment')  # fallback

    amount_paise = int(plan.price * 100)

    order = client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': '1'
    })

    payment = Payment.objects.create(
        user=request.user,
        razorpay_order_id=order['id'],
        amount=amount_paise
    )

    context = {
        'payment': payment,
        'plan': plan,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': amount_paise,
        'user': request.user,
    }

    return render(request, 'subscription/subscribe/checkout.html', context)









logger = logging.getLogger(__name__)  # Setup logger for debug tracking

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        # Debugging Logs
        print("Received POST Data:", data)
        logger.debug("Received POST Data: %s", data)

        if not razorpay_order_id:
            logger.error("Missing razorpay_order_id in POST data")
            return HttpResponseBadRequest("Invalid request: Missing order ID.")

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            logger.error(f"No Payment found for Razorpay Order ID: {razorpay_order_id}")
            return render(request, 'subscription/subscribe/error.html', {
                "message": f"Payment record not found for Order ID: {razorpay_order_id}"
            })

        # Update payment details
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.is_paid = True
        payment.save()

        logger.info(f"Payment successful for order: {razorpay_order_id}")
        return render(request, 'subscription/subscribe/success.html', {
            'payment': payment
        })

    logger.warning("Invalid HTTP method for payment_success view")
    return HttpResponseBadRequest("Invalid request method.")