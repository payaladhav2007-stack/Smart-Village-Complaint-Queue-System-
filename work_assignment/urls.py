from .views import update_task_status_form
from django.urls import path
from .views import (
    CreateAssignmentView,
    SarpanchAssignmentListView,
    StaffAssignmentListView,
    StaffUpdateAssignmentStatusView,
    ListApprovedStaffView,
    sarpanch_dashboard,
    staff_dashboard,
)

urlpatterns = [
    # API endpoints
    path('assign/', CreateAssignmentView.as_view(), name='create_assignment'),
    path('my-assignments/', SarpanchAssignmentListView.as_view(), name='sarpanch_assignments'),
    path('my-tasks/', StaffAssignmentListView.as_view(), name='staff_tasks'),
    path('tasks/<int:pk>/update-status/', StaffUpdateAssignmentStatusView.as_view(), name='update_task_status'),
    path('available-staff/', ListApprovedStaffView.as_view(), name='available_staff'),

    # Frontend dashboard views
    path('dashboard/sarpanch/', sarpanch_dashboard, name='sarpanch_dashboard'),
    path('dashboard/staff/', staff_dashboard, name='staff_dashboard'),
    path('tasks/<int:pk>/update-status/', update_task_status_form, name='update_task_status_form'),
]
