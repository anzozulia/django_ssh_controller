from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.conf.urls.static import static

from main.settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path('', include('app.urls')),
]
urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
)

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)