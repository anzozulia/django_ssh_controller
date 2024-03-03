from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'app'

urlpatterns = [
    path('', login_required(views.dashboard), name='dashboard'),

    path('add_server/', login_required(views.ServerCreateView.as_view()), name='add_server'),
    path('server_inspect/<int:pk>/', login_required(views.server_inspect), name='server_inspect'),
    path('server_edit/<int:pk>/', login_required(views.ServerSettingsView.as_view()), name='server_settings'),
    path('server_delete/<int:pk>/', login_required(views.delete_server), name='delete_server'),
    path('server_switch/<int:pk>/', login_required(views.server_switch), name='server_switch'),

    path('add_alert/<int:server_pk>/', login_required(views.AlertSettingsCreateView.as_view()), name='add_alert'),
    path('delete_alert/', login_required(views.delete_alert), name='delete_alert'),

    path('settings/', login_required(views.SettingsView.as_view()), name='settings'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]