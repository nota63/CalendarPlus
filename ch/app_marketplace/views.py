from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import MiniApp
from accounts.models import Organization, Profile

# Create your views here.

# Display Miniapps 

def mini_apps_list(request,org_id):
    organization=get_object_or_404(Organization, id=org_id)
    apps = MiniApp.objects.all().order_by('-install_count')  # Fetch all apps

    categories = {
        "All": apps,
        "Productivity": apps.filter(category="productivity"),
        "Communication": apps.filter(category="communication"),
        "Task Management": apps.filter(category="task_management"),
        "Entertainment": apps.filter(category="entertainment"),
        "Utility": apps.filter(category="utility"),
        "Other": apps.filter(category="other"),
    }

    return render(request, "mini_apps/purchase/dashboard.html", {"categories": categories,'organization':organization})




