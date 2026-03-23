from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from axes.models import AccessAttempt
from rest_framework.permissions import IsAdminUser

from admin_honeypot.models import LoginAttempt
from axes.models import AccessAttempt

@api_view(['POST'])
def admin_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request=request, username=username, password=password)

    if user is not None:
        if not user.is_staff: # Ensure only admin/staff can login to the panel
            return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)
            
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user.username
        })

    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist() # Requires 'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_security_logs(request):
    attempts = AccessAttempt.objects.all().order_by('-attempt_time')[:10]
    data = [{
        "ip": a.ip_address,
        "username": a.username,
        "time": a.attempt_time,
        "failures": a.failures_count
    } for a in attempts]
    return Response(data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_overview(request):
    # Bots hitting the fake /admin/ path
    honeypot = LoginAttempt.objects.all().order_by('-timestamp')[:10]
    
    # Real login failures on your portal
    brute_force = AccessAttempt.objects.all().order_by('-attempt_time')[:10]
    
    return Response({
        "honeypot_logs": [{
            "ip": log.ip_address, 
            "user": log.username, 
            "time": log.timestamp
        } for log in honeypot],
        "lockout_logs": [{
            "ip": log.ip_address, 
            "failures": log.failures_count, 
            "time": log.attempt_time
        } for log in brute_force]
    })