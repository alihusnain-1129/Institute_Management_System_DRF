from rest_framework import serializers
from .models import Institute

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class InstituteApprovalSerializer(serializers.Serializer):
    institute_id = serializers.IntegerField()
    approve = serializers.BooleanField()