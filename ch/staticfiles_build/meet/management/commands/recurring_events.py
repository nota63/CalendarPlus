

import time
import schedule
import threading
from django.core.management.base import BaseCommand
from django.utils import timezone
from groups.models import GroupEvent
from datetime import datetime, timedelta
import calendar

def calculate_next_occurrence(event):
    """
    Calculate the next occurrence for an event based on its recurrence type, interval, and recurrence days.
    """
    current_date = event.date
    interval = event.interval
    recurrence_type = event.recurrence_type
    recurrence_end_date = event.recurrence_end_date
    recurrence_days = event.recurrence_days.split(', ') if event.recurrence_days else []


    if recurrence_end_date and current_date > recurrence_end_date:
        return None  

    if recurrence_type == 'daily':
        next_event_date = current_date + timedelta(days=interval)

    elif recurrence_type == 'weekly':
        next_event_date = current_date
        while next_event_date.weekday() not in [calendar.day_name.index(day) for day in recurrence_days]:
            next_event_date += timedelta(days=1)
        next_event_date += timedelta(weeks=interval)

    elif recurrence_type == 'monthly':
        try:
            next_event_date = current_date.replace(month=current_date.month + interval)
        except ValueError: 
            next_event_date = current_date.replace(month=current_date.month + interval, day=28)

    elif recurrence_type == 'yearly':
        try:
            next_event_date = current_date.replace(year=current_date.year + interval)
        except ValueError:  
            next_event_date = current_date.replace(year=current_date.year + interval, month=2, day=28)

    else:
        return None

    
    if recurrence_end_date and next_event_date > recurrence_end_date:
        return None  

    return next_event_date

def create_recurring_event(event, next_event_date):
    """
    Create a new GroupEvent for the next occurrence.
    """
    event_copy = GroupEvent.objects.create(
        group=event.group,
        organization=event.organization,
        created_by=event.created_by,
        title=event.title,
        description=event.description,
        date=next_event_date,
        start_time=event.start_time,
        end_time=event.end_time,
        meeting_link=event.meeting_link,
        location=event.location,
        slots=event.slots,
        recurrence_type=event.recurrence_type,
        recurrence_end_date=event.recurrence_end_date,
        recurrence_days=event.recurrence_days
    )
    return event_copy

def check_recurring_events():
    """
    Check for all events with recurrence set and create new events based on their recurrence settings.
    """
    while True:
      
        events = GroupEvent.objects.filter(recurrence_type__ne='none', recurrence_end_date__gte=datetime.today().date())

        for event in events:
            
            next_event_date = calculate_next_occurrence(event)
            if next_event_date:
              
                create_recurring_event(event, next_event_date)

        
        time.sleep(60)

class Command(BaseCommand):
    help = 'Check for recurring events every minute and create new instances if necessary'

    def handle(self, *args, **kwargs):
        
        thread = threading.Thread(target=check_recurring_events)
        thread.start()
        self.stdout.write(self.style.SUCCESS('Recurring event checker started successfully!'))
