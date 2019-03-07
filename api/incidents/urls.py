from django.urls import path
from .views import CreateRedflagAPIView


urlpatterns = [
    path('redflags/', CreateRedflagAPIView.as_view(), name='create'),
]
