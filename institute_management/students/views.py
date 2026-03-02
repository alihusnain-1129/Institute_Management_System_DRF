from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentSerializer, StudentListSerializer
from authentication.permissions import IsInstituteAdmin

class StudentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['enrollment_date']
    search_fields = ['user__first_name', 'user__last_name', 'roll_number', 'user__email']
    ordering_fields = ['roll_number', 'enrollment_date']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StudentListSerializer
        return StudentSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Student.objects.all()
        return Student.objects.filter(institute=user.institute)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Student created successfully", "student": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StudentListSerializer
        return StudentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Student.objects.all()
        return Student.objects.filter(institute=user.institute)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Always allow partial updates
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Get the updated data with user details
        response_serializer = StudentListSerializer(instance, context={'request': request})
        return Response(
            {"message": "Student updated successfully", "student": response_serializer.data},
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        
        # Delete the student and associated user
        student_id = instance.id
        username = user.username
        
        # This will delete both student and user (due to CASCADE)
        instance.delete()
        
        return Response(
            {
                "message": f"Student {username} (ID: {student_id}) deleted successfully",
                "deleted_student_id": student_id,
                "deleted_username": username
            },
            status=status.HTTP_200_OK
        )