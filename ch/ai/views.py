from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from django.views import View
import google.generativeai as genai
import google.generativeai as genai
import pyttsx3
from meet.models import Meeting
from datetime import datetime, timedelta
import dateutil.parser  
genai.configure(api_key="AIzaSyDJ7MgCTe2nst6-jjmJdaSgMP1qnIBXMxE")  

class AIIntro(View):
    template='ai/ai_intro.html'

    def get(self, request):
        return render(request, self.template)
    


class GeminiView(View):
    template = 'ai/chat_with_ai.html'

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        prompt = request.POST.get('prompt')
        user = request.user
        response_text = None

      
        if "meeting" in prompt.lower():
            if "tomorrow" in prompt.lower():
                tomorrow = datetime.now().date() + timedelta(days=1)
                meetings = Meeting.objects.filter(user=user, date=tomorrow)
                response_text = self.format_meetings_response(meetings, "tomorrow")
            
            elif "today" in prompt.lower():
                today = datetime.now().date()
                meetings = Meeting.objects.filter(user=user, date=today)
                response_text = self.format_meetings_response(meetings, "today")
            
            elif "this week" in prompt.lower():
                today = datetime.now().date()
                end_of_week = today + timedelta(days=(6 - today.weekday()))
                meetings = Meeting.objects.filter(user=user, date__range=[today, end_of_week])
                response_text = self.format_meetings_response(meetings, "this week")
            
            elif "first meeting" in prompt.lower():
                today = datetime.now().date()
                meeting = Meeting.objects.filter(user=user, date=today).order_by("time").first()
                response_text = self.format_single_meeting(meeting, "first meeting today")
            
            elif "last meeting" in prompt.lower():
                today = datetime.now().date()
                meeting = Meeting.objects.filter(user=user, date=today).order_by("-time").first()
                response_text = self.format_single_meeting(meeting, "last meeting today")
            
            elif "team meeting" in prompt.lower():
                meetings = Meeting.objects.filter(user=user, meeting_type="Team")
                response_text = self.format_meetings_response(meetings, "team meetings")
            
            elif "count of meetings" in prompt.lower() or "how many" in prompt.lower():
                today = datetime.now().date()
                end_of_week = today + timedelta(days=(6 - today.weekday()))
                count = Meeting.objects.filter(user=user, date__range=[today, end_of_week]).count()
                response_text = f"You have {count} meetings scheduled this week."

            elif "meeting details" in prompt.lower():
                title = prompt.split("titled")[-1].strip().strip('"')
                meeting = Meeting.objects.filter(user=user, title__icontains=title).first()
                response_text = self.format_single_meeting(meeting, f"meeting titled '{title}'")
            
            elif "specific date" in prompt.lower():
                try:
                    date_str = prompt.split("on")[-1].strip()
                    specific_date = self.parse_date(date_str)
                    meetings = Meeting.objects.filter(user=user, date=specific_date)
                    response_text = self.format_meetings_response(meetings, f"on {specific_date}")
                except:
                    response_text = "I couldn't understand the date format. Please provide a valid date."

        if not response_text:
            generation_config = {
                "temperature": 2,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config,
            )
            response = model.generate_content([prompt])
            response_text = response.text

        
        self.speak_response(response_text)

        return render(request, self.template, {'response': response_text})

    @staticmethod
    def format_meetings_response(meetings, timeframe):
        if not meetings.exists():
            return f"You have no meetings scheduled {timeframe}."
        response = f"Here are your meetings {timeframe}:\n"
        for meeting in meetings:
            response += f"- {meeting.title}\n at {meeting.time}\n, link: {meeting.meeting_link or 'N/A'}\n User: {meeting.user}\n Admin:{meeting.admin}"
        return response

    @staticmethod
    def format_single_meeting(meeting, description):
        if not meeting:
            return f"No {description} found."
        return (
            f"{description.capitalize()}:\n"
            f"Title: {meeting.title}\n"
            f"Date: {meeting.date}\n"
            f"Time: {meeting.time}\n"
            f"Link: {meeting.meeting_link or 'N/A'}"
        )

    @staticmethod
    def speak_response(response_text):
        engine = pyttsx3.init()
        engine.say(response_text)
        engine.runAndWait()