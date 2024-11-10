# CalendarPlus - A Professional Calendar and Meeting Management Application

## Project Overview:
  description: |
    CalendarPlus is a feature-rich, professional calendar and meeting management web application
    designed to help users organize, schedule, and track their meetings, tasks, and system analytics.
    With an easy-to-use interface and a variety of built-in tools, users can manage their work and meetings
    efficiently while gaining insights from a detailed analytics dashboard. This project incorporates real-time 
    calendar management with user profiles, task management systems, system information tracking, and more.

## Features:

  - **User Profile with Detailed Information**:
      description: |
        Users have access to a detailed profile where they can view:
        - **Permissions**: See the permissions they have within the system.
        - **Meetings**: View a list of meetings they are part of.
        - **Account Info**:
          - **Last Login**: View the time and date of their last login.
          - **Join Date**: See when their account was created.
          - **Is Staff**: Whether the user has staff privileges (e.g., admin or manager).
          - **Is Active**: Whether the account is currently active or deactivated.
          - **More Info**: Additional profile details for complete user insight.

  - **Professional Task Manager**:
      description: |
        A built-in **Task Manager** for users to:
        - Set tasks specifically related to meetings or events.
        - Store and organize important documents (e.g., meeting agendas, presentations, etc.).
        - Upload and manage media such as images and files.
        - Assign due dates and priorities to each task for easy tracking and completion.
        - Seamlessly organize meeting materials for smooth and efficient sessions.
        benefits:
          - Organizes meeting-related tasks effectively.
          - Helps users prepare for meetings in advance by storing essential materials.
          - Increases productivity with a clear task and document management system.

  - **Comprehensive Analytics Dashboard**:
      description: |
        The application includes a **detailed analytics dashboard** where users can:
        - View real-time data and metrics related to meetings, tasks, and user activities.
        - Access reports on user participation, task completion rates, meeting frequency, and more.
        - Visualize the data using charts and graphs for better insight into meeting trends and performance.
        - Create custom reports to gain a better understanding of user or team performance.
        use_cases:
          - Ideal for managers who need to track their team's activity.
          - Helps users understand the overall performance and participation in meetings.
          - Offers metrics for improving work efficiency.

  - **System Info Tracker**:
      description: |
        Users can view detailed **system information** for the device they are using, including:
        - **Device Name**: The name of the user's device (e.g., laptop, smartphone).
        - **Battery Info**:
          - Battery percentage
          - Whether the device is plugged in or running on battery
          - Estimated time remaining on the battery
        - **Network Information**:
          - Total data usage (sent and received)
          - Network speed and bandwidth
        - **Disk Usage**:
          - Total disk space
          - Used and free disk space
        - **Memory Usage**:
          - Total memory (RAM) available
          - Used memory and memory usage percentage
        - **CPU Usage**: Real-time tracking of CPU usage percentage.
        use_cases:
          - Provides users with an overview of their device’s health and performance.
          - Helps users manage resources by tracking system performance metrics.
          - Ideal for identifying performance issues and optimizing system use.

  - **Database for Meetings**:
      description: |
        The application uses a **comprehensive database** to manage all meetings and associated data.
        - Users can schedule, create, and update meetings.
        - Each meeting is stored with important metadata such as participants, time, and agenda.
        - Attach tasks, documents, images, and system-generated data (like network statistics, device info) to each meeting.
        - Database supports scalable handling of meetings and user data for large teams or organizations.
        benefits:
          - Stores and organizes meeting-related data in a secure and efficient manner.
          - Allows easy retrieval of past meeting details.
          - Helps track meeting resources and attendance in real-time.

## Installation Instructions:

  prerequisites:
    - Python 3.x or higher
    - Django 4.x or higher
    - Django Rest Framework (for API)
    - Celery (for task scheduling)
    - Redis (for Celery backend)
    - PostgreSQL (recommended) or SQLite (for development)

  setup_steps:
    1. **Clone the repository**:
        command: |
          git clone https://github.com/yourusername/CalendarPlus.git
          cd CalendarPlus

    2. **Create a virtual environment**:
        command: |
          python3 -m venv venv

    3. **Activate the virtual environment**:
        - On Windows:
          command: |
            venv\Scripts\activate
        - On macOS/Linux:
          command: |
            source venv/bin/activate

    4. **Install dependencies**:
        command: |
          pip install -r requirements.txt

    5. **Apply database migrations**:
        command: |
          python manage.py migrate

    6. **Create a superuser for accessing the Django Admin panel**:
        command: |
          python manage.py createsuperuser
        note: |
          Follow the prompt to set up the admin account.

    7. **Run the development server**:
        command: |
          python manage.py runserver
        note: |
          The app will be accessible at http://127.0.0.1:8000/.

## API Endpoints:

  - **User Profile**:
      endpoint: `/api/profile/`
      description: |
        - Fetch or update user profile information including permissions, meetings, and account info.
        methods:
          - GET: Fetch user profile data.
          - PUT/PATCH: Update profile details.
      authentication_required: true

  - **Task Management**:
      endpoint: `/api/tasks/`
      description: |
        - Create, update, and retrieve tasks related to meetings.
        - Upload documents, images, and other resources to tasks.
        methods:
          - POST: Create new tasks.
          - GET: Retrieve tasks.
          - PUT/PATCH: Update tasks.
          - DELETE: Remove tasks.
      authentication_required: true

  - **Meeting Management**:
      endpoint: `/api/meetings/`
      description: |
        - Schedule, update, or delete meetings.
        - Attach tasks, documents, and images to meetings.
        methods:
          - POST: Create a meeting.
          - GET: Retrieve meeting details.
          - PUT/PATCH: Update meeting details.
          - DELETE: Delete meetings.
      authentication_required: true

  - **System Info**:
      endpoint: `/api/system_info/`
      description: |
        - Retrieve real-time device and system information including CPU, memory, battery, and disk stats.
        methods:
          - GET: Fetch system information for the current user.
      authentication_required: true

## Technologies Used:

  backend:
    - **Django**: Framework for building the web application.
    - **Django Rest Framework**: To build the REST API for interacting with the app.
    - **APSchedular**: For task scheduling (handling background jobs like sending reminders).

    - **Sqlite3**: Database for storing application data. SQLite can be used in development.
    - **Chart.js**: For visualizing analytics data.

  frontend:
    - **HTML/CSS/JS**: Basic structure, styles, and interactivity.
    - **Bootstrap** (or custom CSS framework): For responsive design and layout.
    - **Axios/Fetch**: For making API requests.

## License:
  description: |
    This project is licensed under the MIT License. You are free to use, modify, and distribute the code.
    Please refer to the [LICENSE](LICENSE) file for more details.

## Contributing:
  instructions: |
    1. Fork the repository.
    2. Create a new branch (`git checkout -b feature-branch`).
    3. Make your changes.
    4. Commit your changes (`git commit -am 'Add new feature'`).
    5. Push to the branch (`git push origin feature-branch`).
    6. Open a Pull Request.
