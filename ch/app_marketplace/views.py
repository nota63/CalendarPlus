from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import MiniApp,InstalledMiniApp
from accounts.models import Organization, Profile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# Create your views here.

# Display Miniapps 
def mini_apps_list(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    
    # Fetch all apps once
    apps_queryset = MiniApp.objects.order_by('-install_count')

    # Explicitly create separate querysets to avoid duplicates
    categories = {
        "All": list(apps_queryset),  # Convert to list to prevent shared references
        "Productivity": list(apps_queryset.filter(category="productivity")),
        "Communication": list(apps_queryset.filter(category="communication")),
        "Task Management": list(apps_queryset.filter(category="task_management")),
        "Entertainment": list(apps_queryset.filter(category="entertainment")),
        "Utility": list(apps_queryset.filter(category="utility")),
        "Other": list(apps_queryset.filter(category="other")),
    }

    return render(request, "mini_apps/purchase/dashboard.html", {
        "categories": categories,
        "organization": organization
    })


# INSTALLATION PAGE
def mini_app_detail(request, app_id, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    app = get_object_or_404(MiniApp, id=app_id)

    # Check if the app is already installed for this organization
    is_installed = InstalledMiniApp.objects.filter(organization=organization, mini_app=app).exists()

    return render(request, "mini_apps/install/detail.html", {
        "app": app,
        "organization": organization,
        "is_installed": is_installed  
    })


# INSTALL MINI-APP
@csrf_exempt  
@login_required
def install_mini_app(request):
    if request.method == "POST":
        org_id = request.POST.get("org_id")
        app_id = request.POST.get("app_id")

        if not org_id or not app_id:
            return JsonResponse({"success": False, "message": "Missing organization or app ID"}, status=400)

        organization = get_object_or_404(Organization, id=org_id)
        mini_app = get_object_or_404(MiniApp, id=app_id)
        user = request.user

        # Check if already installed
        if InstalledMiniApp.objects.filter(user=user, organization=organization, mini_app=mini_app).exists():
            return JsonResponse({"success": False, "message": "App already installed"}, status=400)

        # Install the app
        InstalledMiniApp.objects.create(user=user, organization=organization, mini_app=mini_app)
        mini_app.install_count+=1
        mini_app.save()
        return JsonResponse({"success": True, "message": "App installed successfully"})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



# LAUNCH APP
@login_required
def launch_app(request,org_id,app_id):
    organization = get_object_or_404(Organization,id=org_id)
    app=get_object_or_404(InstalledMiniApp,id=app_id)
    if not app:
        return JsonResponse({'error:':'App not Found!'},status=401)
    
    profile = get_object_or_404(Profile,organization=organization,user=request.user)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to launch the app'},status=400)
    
    context = {
        "app":app,
        "organization":organization
    }
    
    return render(request,'mini_apps/launch/launch.html',context)

