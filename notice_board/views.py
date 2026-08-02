from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Notice
from .serializers import NoticeSerializer, NoticeUpdateSerializer
from .permissions import NoticePermission


class NoticeListCreateView(APIView):
    """
    GS-REG-110:
    GET  /api/notices/ — List notices scoped to user's village_city
    POST /api/notices/ — Create notice (staff/sarpanch only)
    """
    permission_classes = [IsAuthenticated, NoticePermission]

    def get(self, request):
        if not request.user.village_city:
            return Response({
                'success': False,
                'message': 'Your account is not linked to a village/city.'
            }, status=status.HTTP_400_BAD_REQUEST)

        notices = Notice.objects.filter(
            village_city=request.user.village_city
        ).select_related('posted_by', 'village_city')

        serializer = NoticeSerializer(notices, many=True)
        return Response({
            'village_city': str(request.user.village_city),
            'count': notices.count(),
            'notices': serializer.data
        })

    def post(self, request):
        if not request.user.village_city:
            return Response({
                'success': False,
                'message': 'Your account must be linked to a village/city to post notices.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = NoticeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            notice = serializer.save()
            return Response({
                'success': True,
                'message': 'Notice posted successfully.',
                'notice': NoticeSerializer(notice).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class NoticeDetailView(APIView):
    """
    GS-REG-110:
    GET    /api/notices/<id>/ — Get single notice
    PATCH  /api/notices/<id>/ — Edit notice (role-scoped)
    DELETE /api/notices/<id>/ — Delete notice (role-scoped)
    """
    permission_classes = [IsAuthenticated, NoticePermission]

    def get_notice(self, pk, request):
        notice = get_object_or_404(Notice, pk=pk)
        self.check_object_permissions(request, notice)
        return notice

    def get(self, request, pk):
        notice = self.get_notice(pk, request)
        serializer = NoticeSerializer(notice)
        return Response(serializer.data)

    def patch(self, request, pk):
        notice = self.get_notice(pk, request)
        serializer = NoticeUpdateSerializer(
            notice, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Notice updated successfully.',
                'notice': NoticeSerializer(notice).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        notice = self.get_notice(pk, request)
        title = notice.title
        notice.delete()
        return Response({
            'success': True,
            'message': f'Notice "{title}" deleted successfully.'
        }, status=status.HTTP_200_OK)