from django.urls import path
from . import views

urlpatterns = [
    path('', views.listening_list, name='listening_list'),
    path('add/', views.add_listening_test, name='add_listening_test'),

    # NEW: URL for the rules page
    path('<int:test_id>/rules/', views.listening_rules, name='listening_rules'),

    path('<int:test_id>/', views.listening_test_detail, name='listening_test_detail'),
    path('<int:test_id>/submit/', views.submit_listening_test, name='submit_listening_test'),
    path('block-user/', views.block_user_view, name='listening_block_user'),
]
