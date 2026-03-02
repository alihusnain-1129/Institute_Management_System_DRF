from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Student
from authentication.serializers import UserSerializer

User = get_user_model()

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = ('id', 'user', 'username', 'password', 'email', 'first_name', 'last_name',
                 'phone', 'roll_number', 'enrollment_date', 'date_of_birth', 
                 'address', 'parent_name', 'parent_phone', 'institute')
        read_only_fields = ('id', 'enrollment_date', 'institute', 'roll_number')
    
    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        
        institute = request.user.institute
        if not institute:
            raise serializers.ValidationError("Your account is not associated with any institute")
        
        # For create operation
        if not self.instance:  # This is a create operation
            # Check if roll number is unique within the institute
            if Student.objects.filter(institute=institute, roll_number=data.get('roll_number')).exists():
                raise serializers.ValidationError({"roll_number": "Roll number must be unique within institute"})
            
            # Check if username is unique
            if User.objects.filter(username=data.get('username')).exists():
                raise serializers.ValidationError({"username": "Username already exists"})
            
            # Check if email is unique
            if User.objects.filter(email=data.get('email')).exists():
                raise serializers.ValidationError({"email": "Email already exists"})
            
            # Required fields for create
            required_fields = ['username', 'password', 'email', 'first_name', 'last_name', 
                             'phone', 'roll_number', 'date_of_birth', 'address', 
                             'parent_name', 'parent_phone']
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError({field: "This field is required."})
        
        # For update operation - only validate if fields are present
        else:
            # Check if roll number is being changed (should not be allowed)
            if 'roll_number' in data and data['roll_number'] != self.instance.roll_number:
                raise serializers.ValidationError({"roll_number": "Roll number cannot be changed after creation"})
            
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
            'role': 'student',
            'institute': institute,
            'is_approved': True
        }
        
        # Create user
        user = User.objects.create_user(**user_data)
        
        # Create student
        student = Student.objects.create(
            user=user,
            institute=institute,
            **validated_data
        )
        return student
    
    def update(self, instance, validated_data):
        # Update student fields
        instance.address = validated_data.get('address', instance.address)
        instance.parent_name = validated_data.get('parent_name', instance.parent_name)
        instance.parent_phone = validated_data.get('parent_phone', instance.parent_phone)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.save()
        
        # Update user fields if provided
        user = instance.user
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.email = validated_data.get('email', user.email)
        user.phone = validated_data.get('phone', user.phone)
        
        # Update username if provided
        if 'username' in validated_data:
            user.username = validated_data['username']
        
        # Update password if provided
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        
        user.save()
        
        return instance

class StudentListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ('id', 'roll_number', 'user', 'enrollment_date', 'institute', 'institute_name')