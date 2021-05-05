from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('super/', admin.site.urls),
    path('admin/', include('factory.urls', namespace='work')),
    path('', include('extras.urls', namespace='core')),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)