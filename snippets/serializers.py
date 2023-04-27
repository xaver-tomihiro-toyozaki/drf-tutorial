from django.contrib.auth.models import User
from rest_framework import serializers
from snippets.models import BlogPost, Issue, IssueWorkflow, IssueWorkflowStage, IssueWorkflowStageApproval, Snippet, LANGUAGE_CHOICES, STYLE_CHOICES, Workflow


# class SnippetSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(required=False, allow_blank=True, max_length=100)
#     code = serializers.CharField(style={'base_template': 'textarea.html'})
#     linenos = serializers.BooleanField(required=False)
#     language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
#     style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')

#     def create(self, validated_data):
#         """
#         Create and return a new `Snippet` instance, given the validated data.
#         """
#         return Snippet.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Snippet` instance, given the validated data.
#         """
#         instance.title = validated_data.get('title', instance.title)
#         instance.code = validated_data.get('code', instance.code)
#         instance.linenos = validated_data.get('linenos', instance.linenos)
#         instance.language = validated_data.get('language', instance.language)
#         instance.style = validated_data.get('style', instance.style)
#         instance.save()
#         return instance

class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')
    
    class Meta:
        model = Snippet
        fields = ['url', 'id', 'highlight', 'title', 'code', 'linenos', 'language', 'style', 'owner']
        
class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'snippets']
    
class BlogPostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['url', 'id', 'state']

# Issue Type A　ここから
# class IssueSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Issue
#         fields = ['url', 'id', 'title', 'workflow_state', 'approved']
        
# class WorkflowSerializer(serializers.ModelSerializer):
#     issue = serializers.ReadOnlyField(source='issue.id')
#     class Meta:
#         model = Workflow
#         fields = ['issue', 'step', 'reviewer', 'text', 'approved', 'approved_at']
# Issue Type A　ここまで

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


# Workflow Type C(込み込みのやつ)
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
