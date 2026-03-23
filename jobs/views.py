from rest_framework.decorators import api_view, permission_classes # Added
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser           # Added

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Job
from .serializers import JobSerializer


@api_view(['GET'])
@permission_classes([AllowAny]) # HIGH SECURITY
def get_jobs(request):
    jobs = Job.objects.all().order_by('-created_at')
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_job(request, id=None, slug=None):

    if id:
        job = get_object_or_404(Job, id=id)

    elif slug:
        job = get_object_or_404(Job, slug=slug)

    serializer = JobSerializer(job)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) # HIGH SECURITY
def create_job(request):
    serializer = JobSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated]) # HIGH SECURITY
def update_job(request, id):
    job = get_object_or_404(Job, id=id)

    serializer = JobSerializer(job, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated]) # HIGH SECURITY
def delete_job(request, id):
    job = get_object_or_404(Job, id=id)
    job.delete()

    return Response({"message": "deleted"}, status=status.HTTP_200_OK)