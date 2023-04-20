from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from api.views import UserViewSet

router_api = DefaultRouter()
router_api.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router_api.urls))
]
