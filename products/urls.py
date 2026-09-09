from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    
    # Dòng này BẮT BUỘC phải nằm trên dòng <slug:slug> bên dưới
    path('products/search-suggestions/', views.search_suggestions_view, name='search_suggestions'),
    
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('products/<slug:slug>/review/', views.add_review_view, name='add_review'),
    path('products/<slug:slug>/comment/', views.add_comment_view, name='add_comment'),
]