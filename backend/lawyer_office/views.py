from django.http import HttpResponse
from django.shortcuts import redirect

def home(request):
    # Redirect to the admin interface for now
    # You can replace this with your actual home page view later
    return redirect('admin:index')
