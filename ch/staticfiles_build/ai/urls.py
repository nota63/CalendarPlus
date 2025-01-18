from django.urls import path
from .import views

urlpatterns=[
    path('gemini/',views.GeminiView.as_view(), name='gemini'),
    path('ai_intro/',views.AIIntro.as_view(), name='ai_intro')
]