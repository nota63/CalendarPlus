from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import MiniApp
from accounts.models import Organization, Profile

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

def mini_app_detail(request, app_id,org_id):
    organization=get_object_or_404(Organization,id=org_id)
    app = get_object_or_404(MiniApp, id=app_id)  
    return render(request, "mini_apps/install/detail.html", {"app": app,'organization':organization})