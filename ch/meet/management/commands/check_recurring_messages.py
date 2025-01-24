import schedule
import threading
import time
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from organization_channels.models import RecurringMessage, Message, Channel, RecurrenceHistory
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def send_recurring_messages():
    """
    Fetch recurring messages and send them if conditions match.
    Includes robust error handling and logging.
    """
    try:
        now = datetime.now()
        today = now.strftime('%A').lower()  

        recurring_messages = RecurringMessage.objects.filter(is_active=True)
        logger.info(f"Processing {len(recurring_messages)} recurring messages.")

        for recurring in recurring_messages:
            try:
                if recurring.recurrence_type == "daily":
                    send_message(recurring)

                elif recurring.recurrence_type == "weekly" and today in recurring.recurrence_days:
                    send_message(recurring)

                elif recurring.recurrence_type == "monthly" and now.day == recurring.start_date.day:
                    send_message(recurring)

                elif recurring.recurrence_type == "custom" and today in recurring.recurrence_days:
                    send_message(recurring)

            except Exception as e:
                logger.error(f"Error processing recurring message ID {recurring.id}: {e}")

    except Exception as e:
        logger.error(f"Error in send_recurring_messages: {e}")

def send_message(recurring):
    """
    Send the recurring message and log it.
    Includes error handling for message creation and recurrence history.
    """
    try:
        if recurring.end_date and recurring.end_date < datetime.now().date():
            recurring.is_active = False
            recurring.save()
            logger.info(f"Recurring message ID {recurring.id} is expired and deactivated.")
            return

  
        message = Message.objects.create(
            organization=recurring.organization,
            channel=recurring.channel,
            content=recurring.text,
            created_by=recurring.user, 
            is_recurring=True,
        )


        RecurrenceHistory.objects.create(
            recurring_message=recurring,
            organization=recurring.organization,
            channel=recurring.channel,
            user=recurring.user,  
            sent_at=datetime.now(),
            recurrence_type=recurring.recurrence_type,
        )

        logger.info(f"Sent recurring message: {recurring.text} in channel {recurring.channel.name}")

    except Exception as e:
      
        logger.error(f"Error sending recurring message ID {recurring.id}: {e}")
        
        try:
            RecurrenceHistory.objects.create(
                recurring_message=recurring,
                organization=recurring.organization,
                channel=recurring.channel,
                user=recurring.created_by,  
                sent_at=datetime.now(),
                recurrence_type=recurring.recurrence_type,
            )
        except Exception as history_error:
            logger.error(f"Failed to log RecurrenceHistory for recurring message ID {recurring.id}: {history_error}")

def run_scheduler():
    """
    Runs the scheduler every minute to check for recurring messages.
    """
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error in scheduler loop: {e}")
        time.sleep(5)  

class Command(BaseCommand):
    help = "Run the recurring message scheduler"

    def handle(self, *args, **kwargs):
        try:
            schedule.every(1).minute.do(send_recurring_messages)

            threading.Thread(target=run_scheduler, daemon=True).start()

            self.stdout.write(self.style.SUCCESS("Recurring message scheduler is running..."))
            logger.info("Recurring message scheduler started successfully.")

            while True:
                time.sleep(10)  

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Scheduler stopped."))
            logger.warning("Recurring message scheduler stopped.")
        except Exception as e:
            logger.error(f"Error in handle method: {e}")
            self.stdout.write(self.style.ERROR("An error occurred while running the scheduler."))
