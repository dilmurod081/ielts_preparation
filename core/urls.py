from django.urls import path
from . import views

urlpatterns = [
    # General pages
    path('', views.home, name='home'),

    # Specific admin/user pages
    path('add-user/', views.add_user, name='add_user'),
    path('user-statistics/', views.user_statistics, name='user_statistics'),
    path('user-statistics/<int:user_id>/', views.user_detail, name='user_detail'),

    # The specific 'blocked' page URL must come before the general slug pattern
    path('blocked/', views.blocked_page, name='blocked_page'),

    # The general "catch-all" slug pattern for static pages must be last
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]
