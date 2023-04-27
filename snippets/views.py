from django.shortcuts import get_object_or_404
from django_fsm import can_proceed, has_transition_perm
from snippets.models import Issue, IssueWorkflow, IssueWorkflowStage, IssueWorkflowStageApproval, Workflow
from snippets.serializers import IssueSerializer, IssueWorkflowSerializer, IssueWorkflowStageApprovalSerializer, IssueWorkflowStageSerializer, WorkflowSerializer

from rest_framework.response import Response

from rest_framework import viewsets

from rest_framework.decorators import action
from rest_framework.response import Response


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    
    def perform_create(self, serializer):
        serializer.save(issuer=self.request.user)

class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    
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
    def approve(self, request, issue_pk, pk):
        workflow = get_object_or_404(Workflow, pk=pk)
        return self.perform_transition(workflow, workflow.approve)
    
    @action(detail=True, methods=['post'])
    def review(self, request, issue_pk, pk):
        workflow = get_object_or_404(Workflow, pk=pk)
        return self.perform_transition(workflow, workflow.review)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, issue_pk, pk):
        workflow = get_object_or_404(Workflow, pk=pk)
        return self.perform_transition(workflow, workflow.reject)
    
    def get_queryset(self):
        issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        return issue.workflow_set.all()
    
    def perform_create(self, serializer):
        issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        serializer.save(issue=issue)
        


# Workflow Type C (ステージ順の制限をつけれるようにしたもの)
class IssueWorkflowViewSet(viewsets.ModelViewSet):
    queryset = IssueWorkflow.objects.all()
    serializer_class = IssueWorkflowSerializer


class IssueWorkflowStageViewSet(viewsets.ModelViewSet):
    queryset = IssueWorkflowStage.objects.all()
    serializer_class = IssueWorkflowStageSerializer


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
        workflow = get_object_or_404(IssueWorkflowStageApproval, pk=pk)
        return self.perform_transition(workflow, workflow.approve)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk):
        workflow = get_object_or_404(IssueWorkflowStageApproval, pk=pk)
        return self.perform_transition(workflow, workflow.review)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk):
        workflow = get_object_or_404(IssueWorkflowStageApproval, pk=pk)
        return self.perform_transition(workflow, workflow.reject)
# Workflow Type C (ステージ順の制限をつけれるようにしたもの) ここまで