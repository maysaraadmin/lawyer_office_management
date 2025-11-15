from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from apps.users.models import User
from apps.clients.models import Client, ClientNote
from apps.appointments.models import Appointment


class Command(BaseCommand):
    help = 'Create sample data for the lawyer office management system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample users
        self.create_users()
        
        # Create sample clients
        self.create_clients()
        
        # Create sample appointments
        self.create_appointments()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_users(self):
        """Create sample users"""
        users_data = [
            {
                'email': 'john.doe@lawfirm.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'LAWYER',
                'is_staff': True,
                'password': 'password123'
            },
            {
                'email': 'jane.smith@lawfirm.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'user_type': 'PARALEGAL',
                'is_staff': True,
                'password': 'password123'
            },
            {
                'email': 'admin@lawfirm.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
                'password': 'admin123'
            }
        ]
        
        for user_data in users_data:
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'  Created user: {user.email}')
            else:
                self.stdout.write(f'  User already exists: {user.email}')

    def create_clients(self):
        """Create sample clients"""
        clients_data = [
            {
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'email': 'michael.j@email.com',
                'phone': '+1-555-0101',
                'address': '123 Main St, New York, NY 10001',
                'date_of_birth': '1980-05-15'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'email': 'sarah.w@email.com',
                'phone': '+1-555-0102',
                'address': '456 Oak Ave, Los Angeles, CA 90001',
                'date_of_birth': '1985-08-22'
            },
            {
                'first_name': 'Robert',
                'last_name': 'Brown',
                'email': 'robert.b@email.com',
                'phone': '+1-555-0103',
                'address': '789 Pine Rd, Chicago, IL 60007',
                'date_of_birth': '1975-03-10'
            },
            {
                'first_name': 'Emily',
                'last_name': 'Davis',
                'email': 'emily.d@email.com',
                'phone': '+1-555-0104',
                'address': '321 Elm St, Houston, TX 77001',
                'date_of_birth': '1990-12-05'
            },
            {
                'first_name': 'James',
                'last_name': 'Miller',
                'email': 'james.m@email.com',
                'phone': '+1-555-0105',
                'address': '654 Maple Dr, Phoenix, AZ 85001',
                'date_of_birth': '1982-07-18'
            }
        ]
        
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            if created:
                self.stdout.write(f'  Created client: {client.first_name} {client.last_name}')
                
                # Create a note for each client
                ClientNote.objects.create(
                    client=client,
                    title='Initial Consultation',
                    content=f'Initial consultation with {client.first_name} {client.last_name}.',
                    created_by=User.objects.filter(user_type='LAWYER').first()
                )
            else:
                self.stdout.write(f'  Client already exists: {client.first_name} {client.last_name}')

    def create_appointments(self):
        """Create sample appointments"""
        users = User.objects.all()
        
        if not users:
            self.stdout.write(self.style.WARNING('  No users found. Skipping appointments creation.'))
            return
        
        appointments_data = []
        
        # Create appointments for the next 30 days
        for i in range(20):
            user = random.choice(users)
            
            # Random date in the next 30 days
            days_ahead = random.randint(1, 30)
            appointment_date = timezone.now() + timedelta(days=days_ahead)
            
            # Random time between 9 AM and 5 PM
            hour = random.randint(9, 16)  # 16 to allow for 1-hour appointments
            minute = random.choice([0, 15, 30, 45])
            start_time = appointment_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
            
            statuses = ['scheduled', 'confirmed', 'completed', 'cancelled']
            # Past appointments are more likely to be completed
            if appointment_date < timezone.now():
                status = random.choice(['completed', 'completed', 'completed', 'cancelled'])
            else:
                status = random.choice(['scheduled', 'confirmed'])
            
            appointments_data.append({
                'user': user,
                'title': f'Consultation with {user.first_name} {user.last_name}',
                'description': f'Appointment for {user.first_name} {user.last_name}.',
                'start_time': start_time,
                'end_time': end_time,
                'status': status
            })
        
        for appt_data in appointments_data:
            appointment, created = Appointment.objects.get_or_create(
                user=appt_data['user'],
                start_time=appt_data['start_time'],
                defaults=appt_data
            )
            if created:
                self.stdout.write(f'  Created appointment: {appointment.title} on {appointment.start_time.date()}')
            else:
                self.stdout.write(f'  Appointment already exists: {appointment.title}')
