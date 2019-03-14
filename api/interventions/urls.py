from django.urls import path, include
from rest_framework import routers
from .views import InterventionsView


router = routers.DefaultRouter()
router.register('interventions', InterventionsView)

urlpatterns = [
    path('', include(router.urls)),
]
