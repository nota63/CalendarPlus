from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Profile,Organization
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


# Create your views here.


# FETCH MEMBERS TO DM 
@login_required
def organization_members(request, org_id):
    
    organization = get_object_or_404(Organization, id=org_id)
    
    
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return HttpResponseForbidden("You do not have permission to view this organization's members.")
    

    members = Profile.objects.filter(organization=organization).select_related("user")

    context = {
        "organization": organization,
        "members": members,
    }
    return render(request, "direct_messages/fetch_members/members_list.html", context)





