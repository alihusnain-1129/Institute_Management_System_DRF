from rest_framework import serializers
from .models import Course, Enrollment
from teachers.models import Teacher
from teachers.serializers import TeacherListSerializer
from students.models import Student
from students.serializers import StudentListSerializer

class CourseSerializer(serializers.ModelSerializer):
    teacher_details = TeacherListSerializer(source='teacher', read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'course_code', 'name', 'description', 'credits', 
                 'teacher', 'teacher_details', 'institute', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'institute')
    
    def validate_course_code(self, value):
        request = self.context.get('request')
        if not request:
            return value
            
        institute = request.user.institute
        
        # For create operation
        if not self.instance:
            if Course.objects.filter(institute=institute, course_code=value).exists():
                raise serializers.ValidationError("Course code must be unique within institute")
        
        # For update operation - only validate if course_code is being changed
        else:
            if value != self.instance.course_code:
                if Course.objects.filter(institute=institute, course_code=value).exists():
                    raise serializers.ValidationError("Course code must be unique within institute")
        
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data
            
        institute = request.user.institute
        
        # Validate teacher if provided
        if 'teacher' in data and data['teacher']:
            teacher = data['teacher']
            if teacher.institute != institute:
                raise serializers.ValidationError({"teacher": "Teacher must belong to your institute"})
        
        # For create operation - required fields
        if not self.instance:
            required_fields = ['course_code', 'name']
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError({field: "This field is required."})
        
        return data
    
    def update(self, instance, validated_data):
        # Only update fields that are provided
        instance.course_code = validated_data.get('course_code', instance.course_code)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.credits = validated_data.get('credits', instance.credits)
        instance.teacher = validated_data.get('teacher', instance.teacher)
        instance.save()
        return instance

class EnrollmentSerializer(serializers.ModelSerializer):
    student_details = StudentListSerializer(source='student', read_only=True)
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'enrollment_date', 'student_details', 'course_details')
        read_only_fields = ('id', 'enrollment_date')
    
    def validate(self, data):
        institute = self.context['request'].user.institute
        if data['student'].institute != institute:
            raise serializers.ValidationError("Student must belong to your institute")
        if data['course'].institute != institute:
            raise serializers.ValidationError("Course must belong to your institute")
        
        # Check for duplicate enrollment
        if not self.instance:  # Only for create
            if Enrollment.objects.filter(student=data['student'], course=data['course']).exists():
                raise serializers.ValidationError("Student already enrolled in this course")
        
        return data