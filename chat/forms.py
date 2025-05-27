# Añadir al archivo forms.py existente

from django import forms
from django.contrib.auth.models import User


class SearchUserForm(forms.Form):
    """
    Formulario para buscar usuarios por nombre de usuario o correo electrónico
    """
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar usuarios...'})
    )


class MessageForm(forms.Form):
    """
    Formulario para enviar mensajes
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Escribe un mensaje...',
            'id': 'message-input'
        }),
        label=''
    )