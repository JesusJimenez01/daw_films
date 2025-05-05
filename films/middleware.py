from django.shortcuts import redirect
from django.contrib import messages


class RedirectIfAuthenticated:
    """
    Middleware para redirigir usuarios autenticados desde páginas como login/registro
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Lista de rutas a las que un usuario autenticado no debería acceder
            protected_routes = ['/login/', '/register/']

            # Comprobar si el usuario está en una ruta protegida
            if request.path in protected_routes:
                messages.info(request, 'Ya has iniciado sesión.')
                return redirect('index')

        response = self.get_response(request)
        return response