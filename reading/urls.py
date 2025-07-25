from django.urls import path
from . import views

urlpatterns = [
    # Path for the list of all reading tests
    path('', views.reading_list, name='reading_list'),

    # Path for adding a new reading test
    path('add/', views.add_reading_test, name='add_reading_test'),

    # NEW: Path for the rules page before starting a test
    path('<int:test_id>/rules/', views.reading_rules, name='reading_rules'),

    # Path for viewing a single reading test
    path('<int:test_id>/', views.reading_test_detail, name='reading_test_detail'),

    # Path to handle the submission of a reading test
    path('<int:test_id>/submit/', views.submit_reading_test, name='submit_reading_test'),

    # Path for the anti-cheating block mechanism
    path('block-user/', views.block_user_view, name='block_user'),
]
