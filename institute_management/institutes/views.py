from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Institute
from .serializers import InstituteSerializer, InstituteApprovalSerializer
from authentication.permissions import IsSuperAdmin, IsInstituteAdmin

class InstituteListView(generics.ListAPIView):
    serializer_class = InstituteSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get_queryset(self):
        return Institute.objects.all()

class InstituteDetailView(generics.RetrieveAPIView):
    serializer_class = InstituteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Institute.objects.all()
        return Institute.objects.filter(id=user.institute.id)

class InstituteUpdateView(generics.UpdateAPIView):
    serializer_class = InstituteSerializer
    permission_classes = [IsAuthenticated, IsInstituteAdmin]
    
    def get_queryset(self):
        return Institute.objects.filter(id=self.request.user.institute.id)

class PendingInstitutesView(generics.ListAPIView):
    serializer_class = InstituteSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        return Institute.objects.filter(is_approved=False)

class ApproveInstituteView(generics.GenericAPIView):
    serializer_class = InstituteApprovalSerializer
    permission_classes = [IsSuperAdmin]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        institute = get_object_or_404(Institute, id=serializer.validated_data['institute_id'])
        institute.is_approved = serializer.validated_data['approve']
        institute.save()
        
        return Response({"message": f"Institute {'approved' if serializer.validated_data['approve'] else 'rejected'} successfully"})