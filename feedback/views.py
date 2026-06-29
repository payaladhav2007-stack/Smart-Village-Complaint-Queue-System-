from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from .serializers import FeedbackSubmitSerializer
from .models import Feedback


class SubmitFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeedbackSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        target = serializer.validated_data['_target']
        model = serializer.validated_data['_model']
        content_type = ContentType.objects.get_for_model(model)

        already_submitted = Feedback.objects.filter(
            content_type=content_type,
            target_object_id=target.id,
            submitted_by=request.user,
        ).exists()

        if already_submitted:
            return Response(
                {"error": "You have already submitted feedback for this item."},
                status=status.HTTP_409_CONFLICT
            )

        try:
            feedback = Feedback.objects.create(
                content_type=content_type,
                target_object_id=target.id,
                submitted_by=request.user,
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data['comment'],
            )
        except IntegrityError:
            return Response(
                {"error": "You have already submitted feedback for this item."},
                status=status.HTTP_409_CONFLICT
            )

        return Response({
            "message": "Feedback submitted successfully.",
            "feedback": {
                "id": feedback.id,
                "target_type": serializer.validated_data['target_type'],
                "target_id": target.id,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "created_at": feedback.created_at.isoformat(),
            }
        }, status=status.HTTP_201_CREATED)