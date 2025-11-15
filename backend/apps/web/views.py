from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from apps.appointments.models import Appointment
from apps.clients.models import Client
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.utils import timezone


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomAuthenticationForm
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password.')
        return super().form_invalid(form)


@login_required
def dashboard(request):
    # Get statistics
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    stats = {
        'total_clients': Client.objects.filter(created_by=request.user).count(),
        'today_appointments': Appointment.objects.filter(
            user=request.user,
            start_time__gte=today_start,
            start_time__lte=today_end
        ).count(),
        'upcoming_appointments': Appointment.objects.filter(
            user=request.user,
            start_time__gt=timezone.now()
        ).count(),
        'total_cases': Client.objects.filter(created_by=request.user).count(),  # Using clients as cases for now
    }
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(
        user=request.user
    ).order_by('-start_time')[:5]
    
    # Get recent clients
    recent_clients = Client.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_appointments': recent_appointments,
        'recent_clients': recent_clients,
    }
    return render(request, 'web/dashboard.html', context)


@login_required
def appointments(request):
    appointments_list = Appointment.objects.filter(
        user=request.user
    ).order_by('-start_time')
    
    # Get clients for dropdown
    clients = Client.objects.filter(created_by=request.user)
    
    context = {
        'appointments': appointments_list,
        'clients': clients,
    }
    return render(request, 'web/appointments.html', context)


@login_required
def clients(request):
    clients_list = Client.objects.filter(
        created_by=request.user
    ).order_by('-created_at')
    
    context = {
        'clients': clients_list,
    }
    return render(request, 'web/clients.html', context)


@login_required
def profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'web/profile.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


class RegisterView(View):
    template_name = 'registration/register.html'
    
    def get(self, request):
        form = CustomUserCreationForm()
        print(f"Form fields: {list(form.fields.keys())}")  # Debug output
        print(f"Form is valid: {form.is_valid()}")  # Debug output
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_appointment_status(request, appointment_id, status):
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
        
        if status == 'confirm':
            appointment.status = Appointment.Status.CONFIRMED
        elif status == 'cancel':
            appointment.status = Appointment.Status.CANCELLED
        elif status == 'complete':
            appointment.status = Appointment.Status.COMPLETED
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        appointment.save()
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def toggle_client_status(request, client_id, is_active):
    try:
        client = get_object_or_404(Client, id=client_id, created_by=request.user)
        client.is_active = is_active.lower() == 'true'
        client.save()
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
