from rest_framework import serializers
from snippets.models import Issue, IssueComment, IssueThread, IssueWorkflow, IssueWorkflowStage, IssueWorkflowStageApproval, Workflow

# Issue機能
class IssueSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.id')
    class Meta:
        model = Issue
        fields = ['id', 'title', 'content', 'key', 'json', 'author', 'assignee']
        
class IssueThreadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = IssueThread
        fields = ['id', 'issue', 'title', 'resoleved', 'user']
        
class IssueCommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = IssueComment
        fields = ['id', 'issue_thread', 'content', 'user']

# Issue Type B
class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ['id', 'stage', 'approver', 'state', 'comment', 'approved_at']


# Workflow Type C (ステージ順の制限をつけれるようにしたもの)
class IssueWorkflowSerializer(serializers.ModelSerializer):
    approved = serializers.SerializerMethodField()
    class Meta:
        model = IssueWorkflow
        fields = ['id', 'issue', 'issue_workflow_type', 'approved']
        
    def get_approved(self, obj):
        return obj.is_approved()
        
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