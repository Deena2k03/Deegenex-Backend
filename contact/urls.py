from django.urls import path
from .views import contact_us

urlpatterns = [
    # This creates the endpoint: /api/contact-us/
    path('contact-us/', contact_us, name='contact_us'),
]