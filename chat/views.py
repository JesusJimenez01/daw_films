from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, View
from django.utils.decorators import method_decorator

from .forms import SearchUserForm, MessageForm
from .models import Friendship, Message


@method_decorator(login_required, name='dispatch')
class FriendsListView(ListView):
    """
    Vista para mostrar la lista de amigos del usuario
    """
    template_name = 'chat/friends_list.html'
    context_object_name = 'friends'

    def get_queryset(self):
        """
        Obtiene la lista de amigos del usuario
        """
        return Friendship.get_friends(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Añadir solicitudes pendientes
        context['pending_requests'] = Friendship.get_pending_requests(self.request.user)

        # Formulario de búsqueda
        context['search_form'] = SearchUserForm()

        # Contar mensajes no leídos por amigo
        for friend in context['friends']:
            friend.unread_count = Message.get_unread_by_sender(
                receiver=self.request.user,
                sender=friend
            )
        return context


@method_decorator(login_required, name='dispatch')
class SearchUsersView(View):
    """
    Vista para buscar usuarios y enviarles solicitudes de amistad
    """
    template_name = 'chat/search_users.html'
    form_class = SearchUserForm

    def get(self, request):
        form = self.form_class()
        users = []
        return render(request, self.template_name, {'form': form, 'users': users})

    def post(self, request):
        form = self.form_class(request.POST)
        users = []

        if form.is_valid():
            query = form.cleaned_data['query']
            # Buscar usuarios que coincidan con el término de búsqueda
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(id=request.user.id)[:10]  # Limitar a 10 resultados

        # Para cada usuario encontrado, determinar el estado de la amistad
        friendship_status = {}
        for user in users:
            # Verificar si ya son amigos
            if Friendship.are_friends(request.user, user):
                friendship_status[user.id] = 'friends'
            # Verificar si hay una solicitud pendiente enviada por el usuario actual
            elif Friendship.objects.filter(requester=request.user, receiver=user, is_accepted=False).exists():
                friendship_status[user.id] = 'pending_sent'
            # Verificar si hay una solicitud pendiente recibida del otro usuario
            elif Friendship.objects.filter(requester=user, receiver=request.user, is_accepted=False).exists():
                friendship_status[user.id] = 'pending_received'
            else:
                friendship_status[user.id] = 'none'

        return render(request, self.template_name, {
            'form': form,
            'users': users,
            'friendship_status': friendship_status
        })


@login_required
def send_friend_request(request, user_id):
    """
    Envía una solicitud de amistad a otro usuario
    """
    receiver = get_object_or_404(User, id=user_id)

    # Verificar que no se envíe a sí mismo
    if receiver == request.user:
        messages.error(request, 'No puedes enviarte una solicitud a ti mismo')
        return redirect('search_users')

    # Verificar si ya existe una solicitud o son amigos
    if Friendship.are_friends(request.user, receiver):
        messages.info(request, f'Ya eres amigo de {receiver.username}')
        return redirect('friends_list')

    # Verificar si ya hay una solicitud pendiente
    if Friendship.objects.filter(requester=request.user, receiver=receiver).exists():
        messages.info(request, f'Ya has enviado una solicitud a {receiver.username}')
    elif Friendship.objects.filter(requester=receiver, receiver=request.user).exists():
        messages.info(request, f'{receiver.username} ya te ha enviado una solicitud')
    else:
        # Crear nueva solicitud
        Friendship.objects.create(requester=request.user, receiver=receiver)
        messages.success(request, f'Se ha enviado una solicitud de amistad a {receiver.username}')

    # Redirigir según la página anterior
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])
    return redirect('search_users')


@login_required
def accept_friend_request(request, request_id):
    """
    Acepta una solicitud de amistad pendiente
    """
    friendship = get_object_or_404(
        Friendship,
        id=request_id,
        receiver=request.user,
        is_accepted=False
    )

    friendship.is_accepted = True
    friendship.save()

    messages.success(request, f'Has aceptado la solicitud de amistad de {friendship.requester.username}')
    return redirect('friends_list')


@login_required
def reject_friend_request(request, request_id):
    """
    Rechaza una solicitud de amistad pendiente
    """
    friendship = get_object_or_404(
        Friendship,
        id=request_id,
        receiver=request.user,
        is_accepted=False
    )

    requester_name = friendship.requester.username
    friendship.delete()

    messages.info(request, f'Has rechazado la solicitud de amistad de {requester_name}')
    return redirect('friends_list')


@login_required
def remove_friend(request, friend_id):
    """
    Elimina a un usuario de la lista de amigos
    """
    friend = get_object_or_404(User, id=friend_id)

    # Buscar y eliminar la relación de amistad en ambas direcciones
    friendship1 = Friendship.objects.filter(requester=request.user, receiver=friend)
    friendship2 = Friendship.objects.filter(requester=friend, receiver=request.user)

    if friendship1.exists():
        friendship1.delete()

    if friendship2.exists():
        friendship2.delete()

    messages.success(request, f'{friend.username} ha sido eliminado de tus amigos')
    return redirect('friends_list')


@method_decorator(login_required, name='dispatch')
class ChatView(View):
    """
    Vista para el chat entre dos usuarios
    """
    template_name = 'chat/chat.html'
    form_class = MessageForm

    def get(self, request, username):
        try:
            friend = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f'El usuario {username} no existe')
            return redirect('friends_list')

        # Verificar que sean amigos
        if not Friendship.are_friends(request.user, friend):
            messages.error(request, f'No eres amigo de {username}')
            return redirect('friends_list')

        # Obtener historial de mensajes
        conversation = Message.get_conversation(request.user, friend)

        # Obtener lista de todos los amigos para el sidebar
        all_friends = Friendship.get_friends(request.user)

        # Agregar contador de mensajes no leídos por cada amigo
        for friend_item in all_friends:
            friend_item.unread_count = Message.get_unread_by_sender(
                receiver=request.user,
                sender=friend_item
            )

        return render(request, self.template_name, {
            'friend': friend,
            'conversation': conversation,
            'form': self.form_class(),
            'all_friends': all_friends  # Agregamos la lista de amigos
        })

    def post(self, request, username):
        try:
            friend = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f'El usuario {username} no existe')
            return redirect('friends_list')

        # Verificar que sean amigos
        if not Friendship.are_friends(request.user, friend):
            messages.error(request, f'No eres amigo de {username}')
            return redirect('friends_list')

        form = self.form_class(request.POST)

        if form.is_valid():
            content = form.cleaned_data['content']
            # Crear nuevo mensaje
            message = Message.objects.create(
                sender=request.user,
                receiver=friend,
                content=content
            )

            # Si la solicitud es AJAX, devolver JSON con datos del mensaje
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'timestamp': message.timestamp.isoformat(),
                        'sender': message.sender.username
                    }
                })

        # Si la solicitud es AJAX pero el formulario no es válido
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors})

        # Para solicitudes normales, redirigir al chat
        return redirect('chat', username=username)


@login_required
def unread_messages_count(request):
    """
    Retorna el número de mensajes no leídos del usuario
    """
    count = Message.get_unread_count(request.user)
    return JsonResponse({'count': count})