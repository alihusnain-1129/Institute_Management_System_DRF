from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Exam, Result
from .serializers import ExamSerializer, ResultSerializer, ResultUpdateSerializer
from authentication.permissions import IsInstituteAdmin, IsTeacher

class ExamListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['exam_type', 'course', 'exam_date']
    search_fields = ['title', 'course__name']
    ordering_fields = ['exam_date', 'created_at']
    
    def get_serializer_class(self):
        return ExamSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Exam.objects.all()
        return Exam.objects.filter(course__institute=user.institute)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsInstituteAdmin()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Exam created successfully", "exam": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Exam.objects.all()
        return Exam.objects.filter(course__institute=user.institute)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Always allow partial updates
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            {"message": "Exam updated successfully", "exam": serializer.data},
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        exam_title = instance.title
        course_name = instance.course.name
        instance.delete()
        
        return Response(
            {
                "message": f"Exam '{exam_title}' for course '{course_name}' deleted successfully",
                "deleted_exam_id": kwargs.get('pk'),
                "deleted_exam_title": exam_title
            },
            status=status.HTTP_200_OK
        )

class ResultListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['exam', 'student', 'grade']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__roll_number']
    ordering_fields = ['entered_at', 'marks_obtained']
    
    def get_serializer_class(self):
        return ResultSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Result.objects.all()
        return Result.objects.filter(
            Q(exam__course__institute=user.institute) |
            Q(student__institute=user.institute)
        )
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), (IsInstituteAdmin | IsTeacher)()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Result entered successfully", "result": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class ResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Result.objects.all()
        return Result.objects.filter(
            Q(exam__course__institute=user.institute) |
            Q(student__institute=user.institute)
        )
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ResultUpdateSerializer
        return ResultSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full data after update
        full_serializer = ResultSerializer(instance, context=self.get_serializer_context())
        return Response(
            {"message": "Result updated successfully", "result": full_serializer.data},
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        student_name = instance.student.user.get_full_name()
        exam_title = instance.exam.title
        instance.delete()
        
        return Response(
            {
                "message": f"Result for {student_name} in '{exam_title}' deleted successfully",
                "deleted_result_id": kwargs.get('pk')
            },
            status=status.HTTP_200_OK
        )

class StudentResultsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        student_id = self.kwargs['student_id']
        user = self.request.user
        
        if user.role == 'super_admin':
            return Result.objects.filter(student_id=student_id)
        return Result.objects.filter(
            student_id=student_id,
            exam__course__institute=user.institute
        )