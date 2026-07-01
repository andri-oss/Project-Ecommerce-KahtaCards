from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from .forms import RegisterForm

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            current_site = get_current_site(request)
            mail_subject = 'Aktivasi akun Kahta Grafika Anda'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            
            messages.success(request, 'Pendaftaran berhasil. Silakan cek email Anda untuk mengaktifkan akun.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    # If already logged in, redirect appropriately
    if request.user.is_authenticated:
        next_url = request.GET.get('next', '')
        if next_url:
            return redirect(next_url)
        elif request.user.is_admin or request.user.is_staff_employee:
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
                elif user.is_admin or user.is_staff_employee:
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


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Terima kasih atas konfirmasi email Anda. Akun Anda kini telah aktif, silakan login.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Tautan aktivasi tidak valid!')
        return redirect('accounts:login')


from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})
