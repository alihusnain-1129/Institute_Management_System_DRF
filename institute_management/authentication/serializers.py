from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from institutes.models import Institute

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    institute_name = serializers.CharField(write_only=True, required=False)
    institute_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 
                 'role', 'phone', 'institute_name', 'institute_id')
    
    def validate(self, data):
        role = data.get('role')
        institute_name = data.get('institute_name')
        institute_id = data.get('institute_id')
        
        # Prevent registration as super_admin through API
        if role == 'super_admin':
            raise serializers.ValidationError({"role": "Cannot register as super admin through API"})
        
        # Institute admin must provide institute name (new institute)
        if role == 'institute_admin':
            if not institute_name:
                raise serializers.ValidationError({"institute_name": "Institute name is required for institute admin"})
            if institute_id:
                raise serializers.ValidationError({"institute_id": "Institute admins cannot provide institute_id, they create new institute"})
        
        # Teachers and students must belong to an existing institute
        elif role in ['teacher', 'student']:
            if not institute_id:
                raise serializers.ValidationError({"institute_id": f"Institute ID is required for {role} registration"})
            
            # Verify institute exists and is approved
            try:
                institute = Institute.objects.get(id=institute_id)
                if not institute.is_approved:
                    raise serializers.ValidationError({"institute_id": "Institute is not yet approved by super admin"})
                data['institute'] = institute
            except Institute.DoesNotExist:
                raise serializers.ValidationError({"institute_id": "Institute with this ID does not exist"})
            
            if institute_name:
                raise serializers.ValidationError({"institute_name": f"{role} cannot provide institute_name, use institute_id instead"})
        
        return data
    
    def create(self, validated_data):
        institute_name = validated_data.pop('institute_name', None)
        institute_id = validated_data.pop('institute_id', None)
        institute = validated_data.pop('institute', None)
        password = validated_data.pop('password')
        
        # Handle different registration types
        if validated_data['role'] == 'institute_admin':
            # Create new institute for institute admin
            new_institute = Institute.objects.create(
                name=institute_name,
                is_approved=False
            )
            validated_data['institute'] = new_institute
            validated_data['is_approved'] = False  # Institute admin needs approval
            
        else:
            # Teacher or student - use existing institute
            validated_data['institute'] = institute
            validated_data['is_approved'] = True  # Auto-approved once institute is approved
        
        user = User.objects.create_user(**validated_data, password=password)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                # Superusers are always approved
                if user.is_superuser:
                    data['user'] = user
                    return data
                
                # Check approval for non-superusers
                if not user.is_approved:
                    raise serializers.ValidationError("Account not approved by super admin")
                
                if user.role == 'student' and not user.is_active:
                    raise serializers.ValidationError("Student account is not active")
                
                data['user'] = user
            else:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include username and password")
        
        return data

class UserSerializer(serializers.ModelSerializer):
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                 'phone', 'is_approved', 'institute', 'institute_name')
        read_only_fields = ('id', 'is_approved', 'institute_name')

class UserApprovalSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    approve = serializers.BooleanField()
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this ID does not exist")
        return value