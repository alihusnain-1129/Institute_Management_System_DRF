from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Teacher
from authentication.serializers import UserSerializer

User = get_user_model()

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    
    class Meta:
        model = Teacher
        fields = ('id', 'user', 'username', 'password', 'email', 'first_name', 'last_name',
                 'phone', 'employee_id', 'department', 'qualification', 'joining_date',
                 'specialization', 'address', 'emergency_contact', 'institute')
        read_only_fields = ('id', 'joining_date', 'institute')
    
    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        institute = request.user.institute
        if not institute:
            raise serializers.ValidationError("Your account is not associated with any institute")
        
        # For create operation
        if not self.instance:
            # Check if employee_id is unique within the institute
            if Teacher.objects.filter(institute=institute, employee_id=data['employee_id']).exists():
                raise serializers.ValidationError({"employee_id": "Employee ID must be unique within institute"})
            
            # Check if username is unique
            if User.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError({"username": "Username already exists"})
            
            # Check if email is unique
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError({"email": "Email already exists"})
        
        # For update operation
        else:
            # Check if employee_id is being changed
            if 'employee_id' in data and data['employee_id'] != self.instance.employee_id:
                if Teacher.objects.filter(institute=institute, employee_id=data['employee_id']).exists():
                    raise serializers.ValidationError({"employee_id": "Employee ID already exists"})
            
            # Check username uniqueness if being updated
            if 'username' in data and data['username'] != self.instance.user.username:
                if User.objects.filter(username=data['username']).exists():
                    raise serializers.ValidationError({"username": "Username already exists"})
            
            # Check email uniqueness if being updated
            if 'email' in data and data['email'] != self.instance.user.email:
                if User.objects.filter(email=data['email']).exists():
                    raise serializers.ValidationError({"email": "Email already exists"})
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        institute = request.user.institute
        
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'phone': validated_data.pop('phone'),
            'role': 'teacher',
            'institute': institute,
            'is_approved': True
        }
        
        # Create user
        user = User.objects.create_user(**user_data)
        
        # Create teacher
        teacher = Teacher.objects.create(
            user=user,
            institute=institute,
            **validated_data
        )
        return teacher
    
    def update(self, instance, validated_data):
        # Update teacher fields
        instance.employee_id = validated_data.get('employee_id', instance.employee_id)
        instance.department = validated_data.get('department', instance.department)
        instance.qualification = validated_data.get('qualification', instance.qualification)
        instance.specialization = validated_data.get('specialization', instance.specialization)
        instance.address = validated_data.get('address', instance.address)
        instance.emergency_contact = validated_data.get('emergency_contact', instance.emergency_contact)
        instance.save()
        
        # Update user fields if provided
        user = instance.user
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.email = validated_data.get('email', user.email)
        user.phone = validated_data.get('phone', user.phone)
        
        if 'username' in validated_data:
            user.username = validated_data['username']
        
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        
        user.save()
        
        return instance

class TeacherListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ('id', 'employee_id', 'user', 'department', 'qualification', 
                 'joining_date', 'institute', 'institute_name')