from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pets/<int:id>/', views.pet_detail, name='pet_detail'),
    path('adoption-request/<int:id>/', views.adoption_request, name='adoption_request'),
    path('my-adoption-requests/', views.my_adoption_requests, name='my_adoption_requests'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/pets/', views.admin_pets, name='admin_pets'),
    path('admin/requests/', views.admin_requests, name='admin_requests'),
    path('admin/pets/<int:id>/adopted/', views.mark_adopted, name='mark_adopted'),
    path('admin/pets/<int:id>/delete/', views.delete_pet, name='delete_pet'),
    path('admin/requests/<int:id>/approve/', views.approve_request, name='approve_request'),
    path('admin/requests/<int:id>/reject/', views.reject_request, name='reject_request'),
    path('admin/requests/<int:id>/delete/', views.delete_request, name='delete_request'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
]