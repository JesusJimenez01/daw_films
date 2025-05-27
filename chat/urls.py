from django.urls import path
from . import views

urlpatterns = [
    # Rutas para gestión de amigos
    path('friends/', views.FriendsListView.as_view(), name='friends_list'),
    path('friends/search/', views.SearchUsersView.as_view(), name='search_users'),
    path('friends/request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/request/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/remove/<int:friend_id>/', views.remove_friend, name='remove_friend'),

    # Rutas para chat
    path('<str:username>/', views.ChatView.as_view(), name='chat'),
    path('unread/count/', views.unread_messages_count, name='unread_messages_count'),
]