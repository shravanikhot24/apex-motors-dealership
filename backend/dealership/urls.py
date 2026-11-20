from django.urls import path
from . import views

urlpatterns = [
    path('auth/register', views.register, name='register'),
    path('auth/login', views.login_view, name='login'),
    path('auth/logout', views.logout_view, name='logout'),
    path('auth/user', views.current_user, name='current-user'),
    path('dealers', views.dealers, name='dealers'),
    path('dealers/<str:dealer_id>', views.dealer_detail, name='dealer-detail'),
    path('reviews', views.reviews, name='reviews'),
    path('makes', views.makes, name='makes'),
]
