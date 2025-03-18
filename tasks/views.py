import heapq
from django.core.cache import cache
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task
from .serializers import TaskSerializer, UserSerializer

# Min-Heap for Task Scheduling
class TaskScheduler:
    def __init__(self):
        self.heap = []
    
    def add_task(self, task):
        heapq.heappush(self.heap, (self.priority_value(task.priority), task.created_at, task))
    
    def priority_value(self, priority):
        return {'high': 1, 'medium': 2, 'low': 3}.get(priority, 3)

scheduler = TaskScheduler()

# Task List & Create View
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        priority = self.request.query_params.get('priority')
        status = self.request.query_params.get('status')
        if priority:
            queryset = queryset.filter(priority=priority)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        scheduler.add_task(task)
        cache.set(f'{self.request.user.id}:{task.id}', task, timeout=300)

# Task Retrieve, Update, Destroy View
class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.set(f'{self.request.user.id}:{instance.id}', instance, timeout=300)
        return instance

    def retrieve(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        cache_key = f"{request.user.id}:{task_id}"
        task = cache.get(cache_key)
        if not task:
            task = self.get_object()
            cache.set(cache_key, task, timeout=300)
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        cache.delete(f'{self.request.user.id}:{instance.id}')
        instance.delete()

# JWT Token Generation
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}

# User Registration
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User registered successfully", "tokens": get_tokens_for_user(user)}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    user = authenticate(request, username=request.data.get("username"), password=request.data.get("password"))
    if user:
        return Response({"message": "Login successful", "tokens": get_tokens_for_user(user)}, status=status.HTTP_200_OK)
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# User Logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
