from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('page/<slug:slug>/', views.static_page_view, name='static_page'),
]