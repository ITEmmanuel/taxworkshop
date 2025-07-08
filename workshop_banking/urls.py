"""
URL configuration for workshop_banking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from workshop_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/<int:pk>/', views.dashboard_edit, name='dashboard_edit'),
    path('dashboard/delete/<int:pk>/', views.dashboard_delete, name='dashboard_delete'),
    path('dashboard/payment_action/<int:pk>/', views.dashboard_payment_action, name='dashboard_payment_action'),
    path('profile/', views.profile_view, name='profile'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('password_change/done/', views.password_change_done_view, name='password_change_done'),
    path('register/', views.register, name='register'),
    path('admin/', admin.site.urls),
]

# Add media file serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, add a dedicated URL pattern to serve proof files
    urlpatterns += [
        path('proofs/<str:filename>', views.serve_proof_file, name='serve_proof_file'),
    ]
