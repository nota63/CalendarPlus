# Calendar App

## Overview:
  description: |
    A comprehensive Calendar App designed to manage personal and professional events. The app allows users to create, manage, and track events with multiple calendar views, recurring event support, and email notifications. Administrators have full control to create and manage events for users through a secure API.

  features:
    - Event Management
    - Recurring Events
    - Multiple Calendar Views (Daily, Weekly, Monthly)
    - Color-coded Events
    - Email Notifications for Event Reminders
    - Admin API to Create/Manage Events for Users
    - User Invitations via Email

## Features:

### User Features:
  event_management: |
    - Create, update, view, and delete events with customizable details such as title, description, date, time, and location.
  
  recurring_events: |
    - Set recurring events (e.g., daily, weekly, monthly) to automatically repeat on specified intervals.
  
  calendar_views: |
    - Choose between daily, weekly, and monthly views to manage and view your events.
  
  color_coding: |
    - Use color-coding to visually categorize events by type (e.g., work, personal, appointments).

  notifications_reminders: |
    - Receive email and in-app notifications/reminders for upcoming events.

  email_notifications: |
    - Users can update their email address to receive event-related notifications directly in their inbox.

### Admin Features:
  admin_event_management_api: |
    - Admin users can create, update, or delete events for individual users through the Django Rest Framework API, making it easier for team leads or managers to schedule events on behalf of others.
  
  user_invitations: |
    - Admins can send event invitations to users via email directly from the admin interface.

### API Features:
  public_api: |
    - Users can interact with the calendar app's API to create, update, and manage events.
  
  api_endpoints: |
    - **GET /api/events/**: List all events.
    - **POST /api/events/**: Create an event (Admin Only).
    - **PUT /api/events/{id}/**: Update an event (Admin Only).
    - **DELETE /api/events/{id}/**: Delete an event (Admin Only).
    - **POST /api/notifications/send/**: Send event reminders and notifications.

## Installation

### Prerequisites:
  python_version: "Python 3.8+"
  database: "PostgreSQL (or configure for SQLite)"
  django_version: "Django 4.2+"
  dependencies:
    - djangorestframework
    - django-channels
    - django-cors-headers
    - celery

### Steps to Install:
  - Clone the repository:
      command: |
        git clone https://github.com/your-username/calendar-app.git
        cd calendar-app
  - Create a virtual environment:
      command: |
        python -m venv venv
        source venv/bin/activate  # For Windows: venv\Scripts\activate
  - Install the required dependencies:
      command: |
        pip install -r requirements.txt
  - Apply migrations:
      command: |
        python manage.py migrate
  - Create a superuser:
      command: |
        python manage.py createsuperuser
  - Run the server:
      command: |
        python manage.py runserver
  - Access the app at: 
      url: "http://127.0.0.1:8000/"
  
## Configuration

### Environment Variables:
  description: |
    The app supports configuration via environment variables using the `django-environ` package. Create a `.env` file in the root directory for environment-specific settings.

  example .env file:
    - DJANGO_SECRET_KEY: "your-secret-key"
    - DEBUG: "True"
    - DATABASE_URL: "postgres://username:password@localhost/dbname"
    - EMAIL_HOST: "smtp.example.com"
    - EMAIL_PORT: "587"
    - EMAIL_HOST_USER: "your-email@example.com"
    - EMAIL_HOST_PASSWORD: "your-email-password"

### API Configuration:
  - **API Base URL**: `http://127.0.0.1:8000/api/`
  - **Authentication**: Rest framework token based authentication
## Running the Project

### Steps to Start the App:
  - After setup, run the Django server:
      command: |
        python manage.py runserver
  - Visit the application at `http://127.0.0.1:8000/`.
  - API will be accessible at `http://127.0.0.1:8000/api/`.

## Testing

### Run Tests:
  description: |
    You can run the test suite to ensure everything is working as expected.

  command: |
    python manage.py test

### Testing Setup:
  - Ensure that all dependencies are installed and configured before running tests.

## Contributing

### How to Contribute:
  steps:
    - Fork the repository.
    - Create a new branch:
        command: |
          git checkout -b feature-branch
    - Commit your changes:
        command: |
          git commit -am 'Add new feature'
    - Push your changes:
        command: |
          git push origin feature-branch
    - Submit a pull request to the main repository.

## License

  license: |
    This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

  dependencies:
    - Django: The main framework for building the app.
    - Django Rest Framework: For building the API.
    - APSchedular: For handling background tasks like notifications.
    - django-cors-headers: To handle cross-origin resource sharing.
    - PostgreSQL/Sqlite3: Database management system (optional for SQLite).

## Contact

  - **Name**: Harshad
  - **Email**: vishaldudhabarve105@gmail.com
  - **GitHub**: [https://github.com/nota63](https://github.com/nota63)
