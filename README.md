# Lawyer Office Management System

A comprehensive law office management system with frontend and backend components.

## Project Structure

```
lawyer_office_management/
├── backend/           # Django backend
│   ├── api/           # API endpoints
│   ├── apps/          # Django apps
│   └── config/        # Project configuration
├── frontend/          # Flet frontend
│   ├── components/    # Reusable UI components
│   ├── pages/         # Application pages
│   └── services/      # API services
└── shared/            # Shared code between frontend and backend
```

## Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- Node.js (for frontend assets if needed)

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update with your settings:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration.

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flet application:
   ```bash
   python run.py
   ```

## Development

- Backend API will be available at `http://localhost:8000`
- Frontend application will be available at `http://localhost:8550`

## Environment Variables

See `.env.example` for the list of required environment variables.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
