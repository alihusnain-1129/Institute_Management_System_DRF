from rest_framework import serializers
from .models import Exam, Result
from courses.serializers import CourseSerializer
from students.serializers import StudentListSerializer

class ExamSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = Exam
        fields = ('id', 'course', 'course_details', 'title', 'exam_type', 
                 'total_marks', 'pass_marks', 'exam_date', 'duration_minutes', 
                 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data
        
        # For create operation - validate required fields
        if not self.instance:
            required_fields = ['title', 'exam_type', 'exam_date', 'course']
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError({field: "This field is required."})
        
        # Validate marks relationship if both are provided
        if 'total_marks' in data and 'pass_marks' in data:
            if data['pass_marks'] > data['total_marks']:
                raise serializers.ValidationError("Pass marks cannot exceed total marks")
        elif 'pass_marks' in data and self.instance:
            if data['pass_marks'] > self.instance.total_marks:
                raise serializers.ValidationError("Pass marks cannot exceed total marks")
        elif 'total_marks' in data and self.instance:
            if self.instance.pass_marks > data['total_marks']:
                raise serializers.ValidationError("Total marks cannot be less than pass marks")
        
        # Validate course belongs to institute
        if 'course' in data:
            institute = request.user.institute
            if data['course'].institute != institute:
                raise serializers.ValidationError({"course": "Course must belong to your institute"})
        
        return data
    
    def update(self, instance, validated_data):
        # Only update fields that are provided
        instance.title = validated_data.get('title', instance.title)
        instance.exam_type = validated_data.get('exam_type', instance.exam_type)
        instance.total_marks = validated_data.get('total_marks', instance.total_marks)
        instance.pass_marks = validated_data.get('pass_marks', instance.pass_marks)
        instance.exam_date = validated_data.get('exam_date', instance.exam_date)
        instance.duration_minutes = validated_data.get('duration_minutes', instance.duration_minutes)
        instance.course = validated_data.get('course', instance.course)
        instance.save()
        return instance

class ResultSerializer(serializers.ModelSerializer):
    student_details = StudentListSerializer(source='student', read_only=True)
    exam_details = ExamSerializer(source='exam', read_only=True)
    
    class Meta:
        model = Result
        fields = ('id', 'exam', 'exam_details', 'student', 'student_details', 
                 'marks_obtained', 'grade', 'remarks', 'entered_by', 'entered_at')
        read_only_fields = ('id', 'entered_at', 'entered_by', 'grade')
    
    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data
            
        institute = request.user.institute
        
        # For create operation
        if not self.instance:
            # Check if student belongs to institute
            if data['student'].institute != institute:
                raise serializers.ValidationError("Student must belong to your institute")
            
            # Check if exam belongs to institute
            if data['exam'].course.institute != institute:
                raise serializers.ValidationError("Exam must belong to your institute")
            
            # Check if marks exceed total
            if data['marks_obtained'] > data['exam'].total_marks:
                raise serializers.ValidationError("Marks obtained cannot exceed total marks")
            
            # Check for duplicate result
            if Result.objects.filter(exam=data['exam'], student=data['student']).exists():
                raise serializers.ValidationError("Result already exists for this student in this exam")
        
        # For update operation
        else:
            if 'marks_obtained' in data:
                exam = data.get('exam', self.instance.exam)
                if data['marks_obtained'] > exam.total_marks:
                    raise serializers.ValidationError("Marks obtained cannot exceed total marks")
        
        return data

class ResultUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('marks_obtained', 'remarks')