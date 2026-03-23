from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from contact.views import contact_us
from meetings.views import dashboard_stats
from accounts.views import security_overview

urlpatterns = [
    # 1. SECURITY: Honeypot traps bots at the standard /admin/ address
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),

    # 2. SECURITY: Your REAL admin panel is moved to a secret path
    path('secret-portal-manager/', admin.site.urls),

    # 3. API ROUTES (Organized with unique prefixes)
    path('api/accounts/', include('accounts.urls')),
    path('api/', include('jobs.urls')),
    path('api/', include('careers.urls')),
    path('api/meetings/', include('meetings.urls')),
    path('api/', include('meetings.urls')),
    path('api/client-meetings/', include('client_meetings.urls')),
    path('api/', include('contact.urls')),
    path('api/', dashboard_stats),
    path('api/security-overview/', security_overview),
]

# Serve Media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)