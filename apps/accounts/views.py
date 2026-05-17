from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog:product_list')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    # If already logged in, redirect appropriately
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '')
        if next_url:
            return redirect(next_url)
        elif request.user.is_admin:
            return redirect('/dashboard/')
        else:
            return redirect('/')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error = 'Silakan isi username dan password.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect admin users to dashboard, customers to home
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                elif user.is_admin:
                    return redirect('/dashboard/')
                else:
                    return redirect('/')
            else:
                error = 'Username atau password salah. Silakan coba lagi.'

    return render(request, 'accounts/login.html', {
        'error': error,
        'username_value': request.POST.get('username', ''),
    })


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
