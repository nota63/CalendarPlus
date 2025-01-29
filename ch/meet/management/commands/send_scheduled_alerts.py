import schedule
import time
import threading
from datetime import datetime,timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from organization_channels.models import AlertNotification, Channel
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

# Function to send the alert (simulated)

def send_alert_message(alert):
    try:
  
        channel = Channel.objects.get(id=alert.channel.id)

     
        print(f"Sending message: '{alert.message}' to channel {channel.name} in {channel.organization.name}")

        
        alert.is_read = True
        alert.save()

        print(f"Alert sent: {alert.message} for channel {channel.name}")

    except ObjectDoesNotExist:
        print(f"Channel {alert.channel.id} not found. Skipping alert.")
    except Exception as e:
        print(f"An error occurred while sending alert: {e}")


def send_scheduled_alerts():
    print(f"Checking scheduled alerts at {timezone.now()}")

    current_time = timezone.now()

 
    alerts_to_send = AlertNotification.objects.filter(
        scheduled_for__lte=current_time,
        is_active=True,
        is_read=False
    )

    if alerts_to_send.exists():
        for alert in alerts_to_send:
           
            send_alert_message(alert)


            new_alert = AlertNotification.objects.create(
                organization=alert.organization,
                channel=alert.channel,
                created_by=alert.created_by,
                message=alert.message,
                is_active=True,
                schedule_type=alert.schedule_type,
                scheduled_for=timezone.now() + timedelta(days=alert.schedule_days), 
                schedule_days=alert.schedule_days
            )

            print(f"Created new scheduled alert: {new_alert.message} for {new_alert.channel.name}")
    else:
        print("No scheduled alerts to send.")


def run_schedule():

    schedule.every(1).minute.do(send_scheduled_alerts)

    while True:
        schedule.run_pending()
        time.sleep(1)  


class Command(BaseCommand):
    help = "Schedules and sends scheduled alerts every minute."

    def handle(self, *args, **kwargs):
        print("Starting scheduled alert checking...")

  
        threading.Thread(target=run_schedule, daemon=True).start()

        
        while True:
            time.sleep(60)  