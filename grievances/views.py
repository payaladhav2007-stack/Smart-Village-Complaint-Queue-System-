from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Complaint
from .serializers import ComplaintSerializer

class SubmitComplaintView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ComplaintSerializer(data=request.data)
        if serializer.is_valid():
            complaint = serializer.save(user=request.user)
            return Response({
                "message": "Grievance submitted successfully.",
                "complaint": {
                    "id": complaint.id,
                    "category": complaint.category,
                    "description": complaint.description,
                    "status": complaint.status,
                    "latitude": str(complaint.latitude),
                    "longitude": str(complaint.longitude),
                    "created_at": str(complaint.created_at)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
