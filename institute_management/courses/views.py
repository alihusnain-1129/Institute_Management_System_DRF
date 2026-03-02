from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from authentication.permissions import IsInstituteAdmin, IsTeacher, CanManageCourse
from students.models import Student

class CourseListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['credits', 'teacher']
    search_fields = ['course_code', 'name']
    ordering_fields = ['course_code', 'name', 'created_at']
    
    def get_serializer_class(self):
        return CourseSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Course.objects.all()
        return Course.objects.filter(institute=user.institute)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsInstituteAdmin()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(institute=self.request.user.institute)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Course created successfully", "course": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CanManageCourse]
    serializer_class = CourseSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Course.objects.all()
        return Course.objects.filter(institute=user.institute)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Always allow partial updates
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            {"message": "Course updated successfully", "course": serializer.data},
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        course_code = instance.course_code
        course_name = instance.name
        instance.delete()
        
        return Response(
            {
                "message": f"Course {course_code} - {course_name} deleted successfully",
                "deleted_course_id": kwargs.get('pk'),
                "deleted_course_code": course_code
            },
            status=status.HTTP_200_OK
        )

class TeacherCoursesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CourseSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        return Course.objects.filter(teacher__user=self.request.user, institute=self.request.user.institute)

class EnrollmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    serializer_class = EnrollmentSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student__institute=self.request.user.institute,
            course__institute=self.request.user.institute
        )
    
    def perform_create(self, serializer):
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Student enrolled successfully", "enrollment": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class EnrollmentDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    serializer_class = EnrollmentSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student__institute=self.request.user.institute,
            course__institute=self.request.user.institute
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        student_name = instance.student.user.get_full_name()
        course_name = instance.course.name
        instance.delete()
        
        return Response(
            {
                "message": f"Student {student_name} removed from course {course_name}",
                "deleted_enrollment_id": kwargs.get('pk')
            },
            status=status.HTTP_200_OK
        )