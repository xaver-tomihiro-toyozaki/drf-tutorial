from django.shortcuts import get_object_or_404
from django_fsm import can_proceed, has_transition_perm
from snippets.models import Issue, IssueComment, IssueThread, IssueWorkflow, IssueWorkflowStage, IssueWorkflowStageApproval, Workflow
from snippets.serializers import IssueCommentSerializer, IssueSerializer, IssueThreadSerializer, IssueWorkflowSerializer, IssueWorkflowStageApprovalSerializer, IssueWorkflowStageSerializer, WorkflowSerializer

from rest_framework.response import Response

from rest_framework import viewsets

from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

# Issue機能
class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'assignee']
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
class IssueThreadViewSet(viewsets.ModelViewSet):
    queryset = IssueThread.objects.all()
    serializer_class = IssueThreadSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IssueCommentViewSet(viewsets.ModelViewSet):
    queryset = IssueComment.objects.all()
    serializer_class = IssueCommentSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
# 

# Workflow Type B (並列のみ)
# class WorkflowViewSet(viewsets.ModelViewSet):
#     serializer_class = WorkflowSerializer
    
#     def perform_transition(self, obj, transition_method):
#         try:
#             if not can_proceed(transition_method, obj):
#                 return Response({'status': 'failure', 'error': 'Cannot perform transition'})
#             if not has_transition_perm(transition_method, self.request.user):
#                 return Response({'status': 'failure', 'error': 'don\'t have the permission'})
                
#             transition_method()
#             obj.save()
#             return Response({'status': 'success', 'state': obj.state})
#         except Exception as e:
#             return Response({'status': 'failure', 'error': str(e)})
        
#     @action(detail=True, methods=['post'])
#     def approve(self, request, issue_pk, pk):
#         workflow = get_object_or_404(Workflow, pk=pk)
#         return self.perform_transition(workflow, workflow.approve)
    
#     @action(detail=True, methods=['post'])
#     def review(self, request, issue_pk, pk):
#         workflow = get_object_or_404(Workflow, pk=pk)
#         return self.perform_transition(workflow, workflow.review)
    
#     @action(detail=True, methods=['post'])
#     def reject(self, request, issue_pk, pk):
#         workflow = get_object_or_404(Workflow, pk=pk)
#         return self.perform_transition(workflow, workflow.reject)
    
#     def get_queryset(self):
#         issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
#         return issue.workflow_set.all()
    
#     def perform_create(self, serializer):
#         issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
#         serializer.save(issue=issue)
        


# Workflow Type C (ステージ順の制限をつけれるようにしたもの)
class IssueWorkflowViewSet(viewsets.ModelViewSet):
    queryset = IssueWorkflow.objects.all()
    serializer_class = IssueWorkflowSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        approved = self.request.query_params.get('approved')
        if approved == 'true':
            queryset = queryset.filter(pk__in=[item.pk for item in queryset if item.is_approved()])
        return queryset


class IssueWorkflowStageViewSet(viewsets.ModelViewSet):
    queryset = IssueWorkflowStage.objects.all()
    serializer_class = IssueWorkflowStageSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        approved = self.request.query_params.get('approved')
        if approved == 'true':
            queryset = queryset.filter(pk__in=[item.pk for item in queryset if item.is_approved()])
        return queryset
    

class IssueWorkflowStageApprovalViewSet(viewsets.ModelViewSet):
    queryset = IssueWorkflowStageApproval.objects.all()
    serializer_class = IssueWorkflowStageApprovalSerializer
    
    def perform_transition(self, obj, transition_method):
        try:
            if not can_proceed(transition_method, obj):
                return Response({'status': 'failure', 'error': 'Cannot perform transition'})
            if not has_transition_perm(transition_method, self.request.user):
                return Response({'status': 'failure', 'error': 'don\'t have the permission'})
                
            transition_method()
            obj.save()
            return Response({'status': 'success', 'state': obj.state})
        except Exception as e:
            return Response({'status': 'failure', 'error': str(e)})
        
    @action(detail=True, methods=['post'])
    def approve(self, request, pk):
        approval = get_object_or_404(IssueWorkflowStageApproval, pk=pk)
        approval.comment = request.data['comment']
        return self.perform_transition(approval, approval.approve)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk):
        approval = get_object_or_404(IssueWorkflowStageApproval, pk=pk)
        approval.comment = request.data['comment']
        return self.perform_transition(approval, approval.review)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk):
        approval = get_object_or_404(IssueWorkflowStageApproval, pk=pk)
        approval.comment = request.data['comment']
        return self.perform_transition(approval, approval.reject)
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['approver']
# Workflow Type C (ステージ順の制限をつけれるようにしたもの) ここまで