from django.urls import path
from datos.views import inicio

urlpatterns = [path("", inicio, name="inicio")]
