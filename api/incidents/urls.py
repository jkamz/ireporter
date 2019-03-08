from django.urls import path, include
from rest_framework import routers
from .views import CreateIncidentView

router = routers.DefaultRouter()
router.register('redflags', CreateIncidentView)
router.register('interventions', CreateIncidentView)

urlpatterns = [
    path('', include(router.urls)),
]
