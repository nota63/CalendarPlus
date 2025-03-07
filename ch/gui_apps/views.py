from django.shortcuts import render,redirect,get_object_or_404
from app_marketplace.models import MiniApp,InstalledMiniApp
from accounts.models import Profile, Organization
from django.http import JsonResponse, HttpResponse, HttpRequest,HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from app_marketplace.check_org_membership import check_org_membership
from .models import AutoSchedule



# Create your views here.
@check_org_membership
@login_required
def automate_scheduling(request,org_id,app_id):
    organization = get_object_or_404(Organization,id=org_id)
    app=get_object_or_404(InstalledMiniApp,id=app_id,organization=organization)
    if not app:
        return JsonResponse({'error:':'App not Found!'},status=401)
    
    user_check=get_object_or_404(InstalledMiniApp,id=app_id,user=request.user)
    if not user_check.mini_app.name == "Automate Scheduling":
        return HttpResponseBadRequest("Bad request or app is not installed")
    
    return render(request,'gui_apps/automate_scheduling/automate_scheduling.html')
