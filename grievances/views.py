from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Complaint
from .serializers import ComplaintSerializer


class SubmitComplaintView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

    def post(self, request):
        media_file = request.data.get('media_path')
        serializer = ComplaintSerializer(data=request.data)
        if serializer.is_valid():
            complaint = serializer.save(user=request.user, media_path=None)
            if media_file:
                complaint.media_path = media_file
                complaint.save()
            return Response({
                "message": "Grievance submitted successfully.",
                "complaint": {
                    "id": complaint.id,
                    "category": complaint.category,
                    "description": complaint.description,
                    "status": complaint.status,
                    "latitude": str(complaint.latitude),
                    "longitude": str(complaint.longitude),
                    "media_path": complaint.media_path.url if complaint.media_path else None,
                    "created_at": str(complaint.created_at)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListComplaintsView(ListAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Complaint.objects.all() if user.role in ('admin', 'staff') else Complaint.objects.filter(user=user)
        category = self.request.query_params.get('category')
        status_param = self.request.query_params.get('status')
        if category:
            queryset = queryset.filter(category=category)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset
