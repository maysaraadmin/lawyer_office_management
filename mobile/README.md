# Lawyer Office Mobile App

A Flet-based mobile application that mirrors the design and functionality of the Django web application for lawyer office management.

## Features

### 📱 Mobile-First Design
- Responsive layout optimized for mobile devices
- Touch-friendly interface with appropriate tap targets
- Consistent design language matching the Django web app

### 🏠 Dashboard
- Overview statistics cards
- Recent appointments list
- Quick action buttons
- Real-time data loading

### 📅 Appointments
- Filter appointments by status (upcoming, today, past, all)
- Search functionality
- Grouped by date
- Status indicators and time display

### 👥 Clients & Cases
- Tab-based navigation between clients and cases
- Client profiles with contact information
- Case management with status tracking
- Search and filter capabilities

### 🎨 Design System
- Consistent color palette matching Django design
- Material Design 3 components
- Proper typography hierarchy
- Smooth transitions and micro-interactions

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
# Create a .env file
API_BASE_URL=http://localhost:8000/api
AUTH_TOKEN=your_token_here
```

3. Run the mobile app:
```bash
python main.py
```

## Architecture

```
mobile/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/
    ├── lib/
    │   └── api/
    │       └── client.py   # API client for backend communication
    └── views/
        ├── __init__.py
        ├── dashboard.py    # Dashboard view
        ├── appointments.py # Appointments view
        └── clients.py      # Clients & Cases view
```

## API Integration

The mobile app communicates with the Django backend through the `APIClient` class:

- **Authentication**: Bearer token authentication
- **Endpoints**: 
  - `/api/appointments/` - Appointments data
  - `/api/clients/` - Clients data  
  - `/api/cases/` - Cases data
  - `/api/dashboard/stats/` - Dashboard statistics

## Navigation

The app uses a bottom navigation bar with three main sections:

1. **Dashboard** - Home screen with overview and quick actions
2. **Appointments** - View and manage appointments
3. **Clients** - Browse clients and cases

## Mobile-Specific Features

- **Responsive Layout**: Adapts to different screen sizes
- **Touch Gestures**: Optimized for touch interaction
- **Pull-to-Refresh**: Refresh data with gesture
- **Offline Support**: Basic caching for offline viewing (future enhancement)

## Development

### Running in Development Mode

```bash
# Run with hot reload (if supported)
flet run main.py

# Or standard Python execution
python main.py
```

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/
```

### Building for Production

```bash
# Build standalone executable
flet pack main.py
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `http://localhost:8000/api` |
| `AUTH_TOKEN` | Authentication token | `None` |

### Mobile Settings

The app is configured with mobile-friendly defaults:
- Window size: 390x844 (iPhone-like dimensions)
- Minimum size: 360x640
- Resizable window for desktop testing

## Contributing

1. Follow the existing code style and patterns
2. Ensure mobile responsiveness
3. Test on different screen sizes
4. Maintain consistency with Django web app design

## License

This project is part of the Lawyer Office Management System.
