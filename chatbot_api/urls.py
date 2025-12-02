from django.urls import path
from . import views

urlpatterns = [
    path('init/', views.initialize_data, name='initialize_data'),
    path('analyze/', views.analyze_area, name='analyze_area'),
    path('upload/', views.upload_file, name='upload_file'),
    path('areas/', views.get_areas, name='get_areas'),
    path('test/', views.test_connection, name='test_connection'),
]