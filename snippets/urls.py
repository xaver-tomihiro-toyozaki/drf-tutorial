from django.urls import path, include
from rest_framework.routers import DefaultRouter
from snippets import views

# Create a router and register our viewsets with it.

router = DefaultRouter()

router.register(r'issue', views.IssueViewSet, basename='issue')
router.register(r'issue/(?P<issue_pk>[^/.]+)/workflow', views.WorkflowViewSet, basename='workflow')

# workflow_list = views.WorkflowViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# workflow_detail = views.WorkflowViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'delete': 'destroy'
# })

router.register(r'issue-workflows', views.IssueWorkflowViewSet)
router.register(r'issue-workflow-stages', views.IssueWorkflowStageViewSet)
router.register(r'issue-workflow-stage-approvals', views.IssueWorkflowStageApprovalViewSet)

urlpatterns = [
    path('', include(router.urls))
]