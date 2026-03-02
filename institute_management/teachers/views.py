from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Teacher
from .serializers import TeacherSerializer, TeacherListSerializer
from authentication.permissions import IsInstituteAdmin

class TeacherListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'joining_date']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email', 'department']
    ordering_fields = ['employee_id', 'joining_date', 'department']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeacherListSerializer
        return TeacherSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Teacher.objects.all()
        return Teacher.objects.filter(institute=user.institute)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Teacher created successfully", "teacher": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeacherListSerializer
        return TeacherSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Teacher.objects.all()
        return Teacher.objects.filter(institute=user.institute)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        response_serializer = TeacherListSerializer(instance, context={'request': request})
        return Response(
            {"message": "Teacher updated successfully", "teacher": response_serializer.data},
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        
        teacher_id = instance.id
        employee_id = instance.employee_id
        username = user.username
        
        instance.delete()
        
        return Response(
            {
                "message": f"Teacher {username} (Employee ID: {employee_id}) deleted successfully",
                "deleted_teacher_id": teacher_id,
                "deleted_employee_id": employee_id,
                "deleted_username": username
            },
            status=status.HTTP_200_OK
        )