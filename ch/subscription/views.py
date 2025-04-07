from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import razorpay
from .models import Payment,PremiumPlan
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from accounts.models import Organization, Profile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import HelpRequest
from django.contrib.auth import login, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


# Rzorpay client setup
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# initiate payment for subscrption plans 
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
# rdirect after payment success
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


# Help Request set-up
@csrf_exempt
@login_required
def raise_help_request(request, org_id):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')
        organization = Organization.objects.get(id=org_id)

        is_member = Profile.objects.filter(user=request.user, organization_id=organization).exists()
        if not is_member:
            return JsonResponse({'success': False, 'error': 'You are not a member of this organization.'}, status=403)


        HelpRequest.objects.create(
            organization=organization,
            user=request.user,
            title=title,
            description=description,
            attachment=attachment
        )
        return JsonResponse({'success': True, 'message': 'Help request raised successfully!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# Fetch help requests for the user 
# Set up a logger for this module
logger = logging.getLogger(__name__)

# Fetch help requests for the user
@login_required
def fetch_user_help_requests(request, org_id):
    if request.method != 'GET':
        logger.warning(f"[HelpRequest] Invalid request method: {request.method} by user {request.user.id}")
        return JsonResponse({'success': False, 'error': 'Invalid request method. Only GET is allowed.'}, status=405)

    try:
        organization = get_object_or_404(Organization, id=org_id)

        is_member = Profile.objects.filter(user=request.user, organization=organization).exists()
        if not is_member:
            return JsonResponse({'success': False, 'error': 'You are not a member of this organization.'}, status=403)


        help_requests = HelpRequest.objects.filter(
            organization=organization,
            user=request.user
        ).order_by('-created_at')

    
        data = []
        for help in help_requests:
            data.append({
                'uuid': str(help.id),
                'title': help.title,
                'description': help.description,
                'status': help.status,
                'created_at': help.created_at.strftime("%Y-%m-%d %H:%M"),
                'attachment_url': help.attachment.url if help.attachment else None
            })

        logger.info(f"[HelpRequest] Fetched {len(data)} requests for user {request.user.id} in org {org_id}")
        return JsonResponse({'success': True, 'requests': data})

    except Exception as e:
        logger.exception(f"[HelpRequest] Error fetching help requests for user {request.user.id} in org {org_id}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred while fetching help requests.',
            'details': str(e)
        }, status=500)
    

# Admin Side Features - User Impersonation System

# 1) fetch all help requests for the organiztion


@login_required
def fetch_all_help_requests_by_org(request, org_id):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Only GET method allowed.'}, status=405)

    try:
        organization = get_object_or_404(Organization, id=org_id)

        help_requests = HelpRequest.objects.filter(organization=organization).select_related('user').order_by('-created_at')

        data = []
        for help in help_requests:
            profile = Profile.objects.filter(user=help.user, organization=organization).first()
            data.append({
                'uuid': help.id,
                'title': help.title,
                'user_full_name': profile.full_name if profile else help.user.username,
                'profile_picture': profile.profile_picture.url if profile and profile.profile_picture else None
            })

        return JsonResponse({'success': True, 'requests': data})

    except Exception as e:
        logger.exception(f"[AdminHelpView] Failed to fetch help requests for org {org_id}")
        return JsonResponse({'success': False, 'error': 'Server error occurred.', 'details': str(e)}, status=500)
    
# Get Help requests detail    
@login_required
def fetch_help_request_detail(request, uuid):
    user = request.user
    method = request.method
    ip = request.META.get('REMOTE_ADDR')

    logger.info(f"[HELP REQUEST DETAIL] Request received — Method: {method}, UUID: {uuid}, User: {user.username}, IP: {ip}")

    if method != 'GET':
        logger.warning(f"[HELP REQUEST DETAIL] Invalid method used — {method} by {user.username}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method. Only GET allowed.'
        }, status=405)

    try:
        help_request = get_object_or_404(HelpRequest, id=uuid)
        organization = help_request.organization

        logger.debug(f"[HELP REQUEST DETAIL] Found HelpRequest for UUID: {uuid}, Org: {organization.name}")

        # Check if user is a member of the organization
        is_member = Profile.objects.filter(user=user, organization=organization).exists()

        if not is_member:
            logger.warning(f"[HELP REQUEST DETAIL] Access denied — User '{user.username}' is not a member of org '{organization.name}'")
            return JsonResponse({
                'success': False,
                'error': 'Access denied. You do not have permission to view this help request.'
            }, status=403)

        data = {
            'uuid': str(help_request.id),
            'organization': organization.name,
            'user': {
                'id': help_request.user.id,
                'full_name': help_request.user.get_full_name(),
                'username': help_request.user.username,
            },
            'title': help_request.title,
            'description': help_request.description,
            'status': help_request.status,
            'created_at': help_request.created_at.strftime('%Y-%m-%d %H:%M'),
            'attachment': help_request.attachment.url if help_request.attachment else None,
            "help_user_id":help_request.user.id,
        }

        logger.info(f"[HELP REQUEST DETAIL] Help request {uuid} served successfully to {user.username}")

        return JsonResponse({'success': True, 'data': data})

    except HelpRequest.DoesNotExist:
        logger.error(f"[HELP REQUEST DETAIL] Help request not found for UUID: {uuid}")
        return JsonResponse({
            'success': False,
            'error': 'Help request not found.'
        }, status=404)

    except Exception as e:
        logger.exception(f"[HELP REQUEST DETAIL] Unexpected error while fetching help request {uuid} for user {user.username}")
        return JsonResponse({
            'success': False,
            'error': 'Something went wrong while fetching the help request.',
            'details': str(e)
        }, status=500)
    


# Final step - User  Impersonation System ( Login As User)
@login_required
def login_as_user(request, org_id, uuid, user_id):
    organization = get_object_or_404(Organization, id=org_id)
    help_request = get_object_or_404(HelpRequest, id=uuid, organization_id=org_id)

    is_org_admin = Profile.objects.filter(
        user=request.user,
        organization_id=org_id,
        is_admin=True
    ).exists()

    if not is_org_admin:
        return HttpResponseForbidden("You must be an admin of this organization.")

    target_user = get_object_or_404(get_user_model(), id=user_id)


    # 🔐 Save impersonator details temporarily (NOT in session yet)
    impersonator_id = request.user.id
    impersonator_name = request.user.username
    organization_id=organization.id

    # Send email and notify the user about impersonation
    subject = "🔐 Impersonation Session Started on Calendar Plus"

    message = f"""
    Hi {target_user.first_name or target_user.username},

    We wanted to inform you that an impersonation session has been initiated on your account in the organization: "{organization.name}".

    🔍 Details:
    - Help Request ID: {help_request.id}
    -Help Request Title: {help_request.title}
    - 👤 Admin: {request.user.username}
    - 🏢 Organization: {organization.name}
    - 📅 Date & Time: {timezone.now().strftime('%A, %d %B %Y at %I:%M %p')}
    - 🛡️ Purpose: This impersonation is typically used for support, troubleshooting, or administrative guidance.

    Please note:
    - ✅ The impersonator cannot access your password or private credentials.
    - ✅ All actions are securely logged and monitored.
    - ✅ You can contact your admin for more context.

    If you feel this session was unauthorized, please report it to our support team immediately.

    Thank you for trusting Calendar Plus.

    — The Calendar Plus Team
    """
    from_email=settings.DEFAULT_FROM_EMAIL

    # send_mail() or your preferred method
    send_mail(subject, message, from_email, [target_user.email])


    # 🔁 Login as target user
    login(request, target_user)

    # ✅ Now restore impersonation details in session
    request.session['impersonator_id'] = impersonator_id
    request.session['impersonator_name'] = impersonator_name
    request.session['organization_id'] = organization_id

   
    # return redirect('org_detail', org_id=organization.id)
    return redirect('start_impersonation',org_id=organization.id, uuid=help_request.id, user_id=target_user.id)


# start impersonation
@login_required
def start_impersonation(request, org_id,uuid, user_id):
    organization = get_object_or_404(Organization, id=org_id)
    help_request=get_object_or_404(HelpRequest, id=uuid,organization_id=org_id)
    target_user=get_object_or_404(get_user_model(), id=user_id)
    profile_picture=Profile.objects.filter(user=target_user, organization=organization).first()

    context = {
        "organization":organization,
        'help_request':help_request,
        'target_user':target_user,
        'profile_picture':profile_picture.profile_picture.url if profile_picture and profile_picture.profile_picture else None,
    }
    help_request.status='resolved'


    return render(request,'subscription/impersonate/impersonate.html',context)




# stop impersonation
@login_required
def stop_impersonation(request):
    impersonator_id = request.session.pop('impersonator_id', None)
    request.session.pop('impersonator_name', None)
    org_id=request.session.pop("organization_id", None)

    if impersonator_id:
        impersonator = get_object_or_404(get_user_model(), id=impersonator_id)
        login(request, impersonator)

    return redirect('org_detail',org_id=org_id)  



