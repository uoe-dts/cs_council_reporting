# Chalkstone Council Issue Reporting System

A comprehensive issue reporting and management system for Chalkstone Council, designed to streamline the process of logging, tracking, and resolving community issues.

## Features

- **Issue Reporting**
  - Public and staff issue submission
  - Image upload support
  - Priority and category classification
  - Status tracking

- **Issue Management**
  - Staff assignment
  - Status updates
  - Resolution tracking
  - Cost estimation and tracking
  - Related issues linking

- **Analytics Dashboard**
  - Real-time issue statistics
  - Cost analysis
  - Resolution time tracking
  - Category and priority analysis

- **User Management**
  - Public user registration
  - Staff user management
  - Role-based access control
  - User activity tracking

## Technology Stack

- **Backend**
  - Django 4.2.20
  - SQLite3
  - Django REST Framework
  - Celery for background tasks

- **Frontend**
  - Bootstrap 5
  - Chart.js for analytics
  - Font Awesome icons

- **Development Tools**
  - Black for code formatting
  - Flake8 for linting
  - Pytest for testing
  - Coverage for test coverage

## Prerequisites

- Python 3.8+
- SQLite3
- Redis (for Celery)
- Node.js (for frontend assets)

## Installation

1. Clone the repository:
   ```cmd
   git clone https://github.com/yourusername/cs_council_reporting.git
   cd cs_council_reporting
   ```

2. Create and activate a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the project root:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   REDIS_URL=redis://localhost:6379/0
   ```

5. Run migrations:
   ```cmd
   python manage.py migrate
   ```

6. Create a superuser:
   ```cmd
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```cmd
   python manage.py runserver
   ```

## Development Setup

1. Install development dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

2. Set up pre-commit hooks:
   ```cmd
   pre-commit install
   ```

3. Run tests:
   ```cmd
   pytest
   ```

4. Check code coverage:
   ```cmd
   coverage run -m pytest
   coverage report
   ``` 