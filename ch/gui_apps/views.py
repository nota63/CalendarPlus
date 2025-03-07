from django.shortcuts import render,redirect,get_object_or_404
from app_marketplace.models import MiniApp,InstalledMiniApp
from accounts.models import Profile, Organization
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from app_marketplace import check_org_membership




# Create your views here.
