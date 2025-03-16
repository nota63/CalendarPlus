from django.shortcuts import render,redirect, get_object_or_404
from group_tasks.models import Task, SubTask, MeetingTaskQuery
from groups.models import Group
from accounts.models import Organization, Profile
from openai import OpenAI,OpenAIError
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import time
import logging
# Create your views here.

# START THE AI CONVERSATION
# Configure logging
logging.basicConfig(level=logging.WARNING)

def generate_ai_response(task, subtasks, organization, group, user_question):
    """
    Generates AI response with retry handling for rate limits.
    """
    api_key =None # Use environment variable for security
    if not api_key:
        logging.error("❌ Error: OpenAI API key is missing.")
        return "❌ Error: AI service is unavailable."

    client = OpenAI(api_key=api_key)

    task_details = f"Task: {task.title}\nDescription: {task.description}\nPriority: {task.priority}\nStatus: {task.status}\nDeadline: {task.deadline}\n"
    subtask_details = "\n".join([f"SubTask: {s.title} | Status: {s.status} | Deadline: {s.deadline}" for s in subtasks])
    org_group_details = f"Organization: {organization.name}\nGroup: {group.name}"

    prompt = (
        f"You are CalAI, an AI assistant for task management. Help the user with task-related questions.\n"
        f"{task_details}\n{subtask_details}\n{org_group_details}\n\n"
        f"User Question: {user_question}\n\n"
        "Give a detailed, professional, and actionable response."
    )

    retries = 3  # Maximum retries
    base_wait_time = 5  # Initial wait time for backoff

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an AI task assistant named CalAI."},
                    {"role": "user", "content": prompt},
                ]
            )
            return response.choices[0].message.content

        except OpenAIError as e:
            error_msg = str(e).lower()

            if "429" in error_msg or "rate limit" in error_msg:
                wait_time = base_wait_time * (2 ** attempt)  # Exponential backoff (5s, 10s, 20s)
                logging.warning(f"⚠️ Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logging.error(f"❌ Error generating AI response: {e}")
                return f"❌ AI service error: {e}"

    return "❌ Error: OpenAI API rate limit exceeded. Try again later."




@login_required
@csrf_exempt  # Use this only if handling CSRF manually in the frontend
def calai_task_analysis(request, org_id, group_id, task_id):
    """
    View to fetch task, subtask, organization, and group details and send them to AI.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    try:
        data = json.loads(request.body)
        user_question = data.get("question", "")

        # Fetch relevant data
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id)
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
        subtasks = SubTask.objects.filter(task=task)
        
        # Generate AI response
        ai_response = generate_ai_response(task, subtasks, organization, group, user_question)
        
        return JsonResponse({"response": ai_response})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)