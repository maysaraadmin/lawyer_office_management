import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # App Config
    APP_NAME = os.getenv('APP_NAME', 'Lawyer Office Management')
    APP_THEME = os.getenv('APP_THEME', 'light')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api/v1/')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))  # seconds
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_LIFETIME = int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', '14400'))
    JWT_REFRESH_TOKEN_LIFETIME = int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', '2592000'))
    
    # Colors
    COLORS = {
        'primary': os.getenv('PRIMARY_COLOR', '#4f46e5'),
        'secondary': os.getenv('SECONDARY_COLOR', '#7c3aed'),
        'error': os.getenv('ERROR_COLOR', '#dc2626'),
        'success': os.getenv('SUCCESS_COLOR', '#059669'),
        'warning': os.getenv('WARNING_COLOR', '#d97706'),
        'info': os.getenv('INFO_COLOR', '#0284c7'),
        'white': '#ffffff',
        'black': '#000000',
        'gray': {
            '50': '#f9fafb',
            '100': '#f3f4f6',
            '200': '#e5e7eb',
            '300': '#d1d5db',
            '400': '#9ca3af',
            '500': '#6b7280',
            '600': '#4b5563',
            '700': '#374151',
            '800': '#1f2937',
            '900': '#111827',
        }
    }
    
    # Typography
    FONT_FAMILY = 'Roboto, Arial, sans-serif'
    FONT_SIZES = {
        'xs': 12,
        'sm': 14,
        'base': 16,
        'lg': 18,
        'xl': 20,
        '2xl': 24,
        '3xl': 30,
        '4xl': 36,
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        '2xl': 48,
        '3xl': 64,
    }
    
    # Border Radius
    BORDER_RADIUS = {
        'none': 0,
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16,
        'full': 9999,
    }
    
    # Shadows
    SHADOWS = {
        'none': 'none',
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    }
    
    # Breakpoints
    BREAKPOINTS = {
        'sm': 640,
        'md': 768,
        'lg': 1024,
        'xl': 1280,
        '2xl': 1536,
    }
    
    # Animation
    TRANSITION_DURATION = 200  # ms
    
    @classmethod
    def get_theme(cls):
        return {
            'light': {
                'primary': cls.COLORS['primary'],
                'on_primary': cls.COLORS['white'],
                'secondary': cls.COLORS['secondary'],
                'on_secondary': cls.COLORS['white'],
                'background': cls.COLORS['white'],
                'on_background': cls.COLORS['gray']['900'],
                'surface': cls.COLORS['white'],
                'on_surface': cls.COLORS['gray']['900'],
                'error': cls.COLORS['error'],
                'on_error': cls.COLORS['white'],
                'success': cls.COLORS['success'],
                'warning': cls.COLORS['warning'],
                'info': cls.COLORS['info'],
                'border': cls.COLORS['gray']['200'],
                'divider': f"1px solid {cls.COLORS['gray']['200']}",
                'hover': {
                    'primary': '#4338ca',  # Darker indigo
                    'secondary': '#6d28d9',  # Darker indigo 600
                },
                'elevation': {
                    '0': 'none',
                    '1': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                    '2': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    '3': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                    '4': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                },
            },
            'dark': {
                'primary': cls.COLORS['primary'],
                'on_primary': cls.COLORS['white'],
                'secondary': cls.COLORS['secondary'],
                'on_secondary': cls.COLORS['white'],
                'background': cls.COLORS['gray']['900'],
                'on_background': cls.COLORS['white'],
                'surface': cls.COLORS['gray']['800'],
                'on_surface': cls.COLORS['white'],
                'error': cls.COLORS['error'],
                'on_error': cls.COLORS['white'],
                'success': cls.COLORS['success'],
                'warning': cls.COLORS['warning'],
                'info': cls.COLORS['info'],
                'border': cls.COLORS['gray']['700'],
                'divider': f"1px solid {cls.COLORS['gray']['700']}",
                'hover': {
                    'primary': '#6366f1',  # Lighter indigo
                    'secondary': '#8b5cf6',  # Lighter indigo 600
                },
                'elevation': {
                    '0': 'none',
                    '1': '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
                    '2': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
                    '3': '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
                    '4': '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
                },
            }
        }.get(cls.APP_THEME, 'light')
