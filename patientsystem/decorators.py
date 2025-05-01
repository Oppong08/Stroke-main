from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def role_required(role):
    def check_role(user):
        try:
            return user.userprofile.role == role
        except:
            return False
    
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not check_role(request.user):
                messages.error(request, f'Only {role}s can access this page.')
                return redirect('patientsystem:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def technician_required(view_func):
    return role_required('technician')(view_func)

def neurologist_required(view_func):
    return role_required('neurologist')(view_func) 