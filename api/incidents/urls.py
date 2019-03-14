from django.urls import path, include
from rest_framework import routers
from .views import RedflagView


router = routers.DefaultRouter()
router.register('redflags', RedflagView)

urlpatterns = [
    path('', include(router.urls)),
]

