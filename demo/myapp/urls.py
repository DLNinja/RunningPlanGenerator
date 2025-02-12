from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("generate-training-plan/", views.generate_training_plan, name="generate"),
    path('training-plan-result/<int:training_plan_id>/', views.training_plan_result, name='training_plan_result'),
    path('training-plans/', views.all_training_plans, name='all_training_plans'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("update-title/<int:training_plan_id>/", views.update_plan_title, name="update_plan_title"),
    path('delete-training-plan/<int:training_plan_id>/', views.delete_training_plan, name='delete_training_plan'),
]