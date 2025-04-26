from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'incidents', views.IncidentViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('incident/<int:pk>/', views.incident_detail, name='incident_detail'),
    path('api/', include(router.urls)),
] 