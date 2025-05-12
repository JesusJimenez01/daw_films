from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from .forms import UserRegisterForm, CustomLoginForm, ProfileUpdateForm


class LoginView(View):
    """
    Vista para el inicio de sesión de usuarios
    """
    template_name = 'auth/login.html'
    form_class = CustomLoginForm

    def get(self, request):
        # Si el usuario ya está autenticado, redirigir a la página principal
        if request.user.is_authenticated:
            return redirect('index')

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                # Redirigir a la página solicitada o a la página principal
                next_page = request.GET.get('next', 'index')
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect(next_page)

        # Si falla la autenticación
        messages.error(request, 'Nombre de usuario o contraseña incorrectos')
        return render(request, self.template_name, {'form': form})


class RegisterView(View):
    """
    Vista para el registro de nuevos usuarios
    """
    template_name = 'auth/register.html'
    form_class = UserRegisterForm

    def get(self, request):
        # Si el usuario ya está autenticado, redirigir a la página principal
        if request.user.is_authenticated:
            return redirect('index')

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # Iniciar sesión automáticamente después del registro
            login(request, user)

            messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido, {username}')
            return redirect('profile')

        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """
    Vista para ver y actualizar el perfil de usuario
    """
    template_name = 'auth/profile.html'
    form_class = ProfileUpdateForm

    def get(self, request):
        form = self.form_class(instance=request.user.profile)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente')
            return redirect('profile')

        return render(request, self.template_name, {'form': form})


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('login')