from rest_framework import serializers
from snippets.models import Issue, IssueWorkflow, IssueWorkflowStage, IssueWorkflowStageApproval, Workflow


# Issue Type B
class IssueSerializer(serializers.HyperlinkedModelSerializer):
    issuer = serializers.ReadOnlyField(source='issuer.username')
    class Meta:
        model = Issue
        fields = ['url', 'id', 'title', 'issuer']

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ['id', 'stage', 'approver', 'state', 'comment', 'approved_at']


# Workflow Type C (ステージ順の制限をつけれるようにしたもの)
class IssueWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueWorkflow
        fields = ['id', 'issue', 'issue_workflow_type']
        
class IssueWorkflowStageSerializer(serializers.ModelSerializer):
    approved = serializers.SerializerMethodField()
    class Meta:
        model = IssueWorkflowStage
        fields = ['id', 'issue_workflow', 'issue_workflow_stage_type', 'previous_stage', 'approved']
        
    def get_approved(self, obj):
        return obj.is_approved()
        

class IssueWorkflowStageApprovalSerializer(serializers.ModelSerializer):
    state = serializers.ReadOnlyField()
    approved_at = serializers.ReadOnlyField()
    class Meta:
        model = IssueWorkflowStageApproval
        fields = ['id', 'issue_workflow_stage', 'approver', 'state', 'comment', 'approved_at']
# Workflow Type C (ステージ順の制限をつけれるようにしたもの) ここまで