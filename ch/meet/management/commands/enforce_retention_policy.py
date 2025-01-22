import time
import schedule
import logging
from datetime import datetime, timedelta
from django.db import transaction
from organization_channels.models import RetentionPolicy, Channel, Message, Link
from django.core.management import call_command

# Set up logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("retention_policy.log"), logging.StreamHandler()],
)


def delete_old_messages_and_links(channel, retention_period, custom_days=None):
    try:
      
        if retention_period == 0 and custom_days:
            retention_cutoff_date = datetime.now() - timedelta(days=custom_days)
        else:
            retention_cutoff_date = datetime.now() - timedelta(days=retention_period)

        
        old_messages = Message.objects.filter(channel=channel, timestamp__lt=retention_cutoff_date)
        old_links = Link.objects.filter(channel=channel, timestamp__lt=retention_cutoff_date)

        
        with transaction.atomic():
            deleted_message_count, _ = old_messages.delete()
            deleted_link_count, _ = old_links.delete()

            
            logging.info(f"Deleted {deleted_message_count} messages and {deleted_link_count} links from channel '{channel.name}'.")

       
            old_messages.delete() 
            old_links.delete()
    except Exception as e:
        logging.error(f"Error deleting old messages and links from channel '{channel.name}': {str(e)}")
     



def enforce_retention():
    try:
   
        retention_policies = RetentionPolicy.objects.all()

        if not retention_policies:
            logging.warning("No retention policies found.")
            return

        for policy in retention_policies:
      
            retention_period = policy.retention_period
            custom_days = policy.custom_days if retention_period == 0 else None

         
            channel = policy.channel

      
            delete_old_messages_and_links(channel, retention_period, custom_days)
    except Exception as e:
        logging.error(f"Error enforcing retention policies: {str(e)}")



def job():
    try:
        logging.info("Running retention policy task...")
        enforce_retention()
        logging.info("Retention policy enforcement completed.")
    except Exception as e:
        logging.error(f"Error running retention policy task: {str(e)}")



def run_schedule():
    try:
     
        schedule.every(1).minute.do(job)
        logging.info("Scheduled retention policy job to run every minute.")


        while True:
            schedule.run_pending()
            time.sleep(1)  
    except Exception as e:
        logging.error(f"Error in the scheduler: {str(e)}")


if __name__ == "__main__":
    run_schedule()
