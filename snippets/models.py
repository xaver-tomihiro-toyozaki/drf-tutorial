from django.db import models
from django_fsm import FSMField, transition

# 基本のIssue機能
class Issue(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    key = models.CharField(max_length=255, null=True)
    json = models.TextField(null=True)
    author = models.ForeignKey('auth.User', related_name="issue_author", on_delete=models.CASCADE)
    assignee = models.ForeignKey('auth.User', related_name="issue_assignee", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
# その他Issueの機能
class IssueThread(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    resoleved = models.BooleanField(default=False)
    user = models.ForeignKey('auth.User', related_name='issue_thread_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class IssueComment(models.Model):
    issue_thread = models.ForeignKey(IssueThread, on_delete=models.CASCADE)
    content = models.TextField()
    user = models.ForeignKey('auth.User', related_name='issue_thread_comment_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

# Issue Type B (順番関係ないもの)
class Workflow(models.Model):
    REVIEWING = 'reviewing'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATE_CHOICES = [
        (REVIEWING, 'reviewing'),
        (APPROVED, 'approved'),
        (REJECTED, 'rejected')
    ]
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    STAGE_CHOICES = [
        ('intermediate', 'intermediate'),
        ('final', 'final')
    ]
    stage = models.CharField(choices=STAGE_CHOICES, default='intermediate', max_length=100)
    approver = models.ForeignKey('auth.User', related_name="final_approver", on_delete=models.CASCADE)
    state = FSMField(default=REVIEWING, choices=STATE_CHOICES, protected=True)
    comment = models.TextField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def can_review(self):
        return True
    
    def same_approver(self, user):
        return user == self.approver
    
    @transition(field=state, source=REVIEWING, target=APPROVED, conditions=[can_review], permission=same_approver)
    def approve(self):
        pass

    @transition(field=state, source=REVIEWING, target=REJECTED, conditions=[can_review], permission=same_approver)
    def reject(self):
        pass

    @transition(field=state, source=[APPROVED, REJECTED], target=REVIEWING, permission=same_approver)
    def review(self):
        pass


# Workflow Type C (ステージ順の制限をつけれるようにしたもの) (↑のIssueは使ってる)
class IssueWorkflow(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    STRICT = 'strict'
    OPEN = 'open'
    TYPE_CHOICES = [
        (STRICT, 'strict'), # 前のステージが承認ステータスでないと承認できない
        (OPEN, 'open') # ほかの承認状況関係なく承認できる
    ]
    issue_workflow_type = models.CharField(choices=TYPE_CHOICES, default='open', max_length=10)
    
    def is_order_strict(self):
        print('issue workflow id: ', self)
        print('issue_workflow_type:', self.issue_workflow_type)
        return self.issue_workflow_type == self.STRICT
    
    def is_approved(self):
        this_wf_stages = IssueWorkflowStage.objects.filter(issue_workflow=self)
        unreferenced_set = set(this_wf_stages.values_list('id', flat=True)) - set(this_wf_stages.values_list('previous_stage', flat=True))
        last_stage = this_wf_stages.filter(id__in=unreferenced_set)
        if len(last_stage) < 1:
            return False
        return last_stage[0].is_approved()
    
class IssueWorkflowStage(models.Model):
    issue_workflow = models.ForeignKey(IssueWorkflow, on_delete=models.CASCADE)
    ALL = 'all'
    ONE = 'one'
    TYPE_CHOICES = [
        (ALL, 'all'),
        (ONE, 'one')
    ]
    issue_workflow_stage_type = models.CharField(choices=TYPE_CHOICES, default=ALL, max_length=5)
    previous_stage = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    def needs_all_approvals(self):
        return self.issue_workflow_stage_type == self.ALL
    
    def is_approved(self):
        this_stage_approvals = IssueWorkflowStageApproval.objects.filter(issue_workflow_stage=self)
        if self.needs_all_approvals():
            print('needs all approvals')
            for an_approval in this_stage_approvals:
                if not an_approval.is_approved():
                    print('found a user has yet to approve on the stage.')
                    return False
            print('all users have approved on the stage.')
            return True
        else:
            for an_approval in this_stage_approvals:
                if an_approval.is_approved():
                    print('found a user has approved on the stage.')
                    return True
        print('this stage is not approved.')
        return False
    

class IssueWorkflowStageApproval(models.Model):
    issue_workflow_stage = models.ForeignKey(IssueWorkflowStage, on_delete=models.CASCADE)
    REVIEWING = 'reviewing'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATE_CHOICES = [
        (REVIEWING, 'reviewing'),
        (APPROVED, 'approved'),
        (REJECTED, 'rejected')
    ]
    approver = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    state = FSMField(default=REVIEWING, choices=STATE_CHOICES, protected=True)
    comment = models.TextField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_approved(self):
        return self.state == self.APPROVED
    
    def can_review(self):
        return True
    
    def same_approver(self, login_user):
        return login_user == self.approver
    
    def can_approve(self, login_user):
        if not self.same_approver(login_user):
            print('not an assigned user')
            return False
        print('assigned user')
        
        if not self.issue_workflow_stage.issue_workflow.is_order_strict():
            print('no setting to approve in order.')
            return True
        print('is set up to approve in order.')
        
        previous_stage = self.issue_workflow_stage.previous_stage
        if previous_stage is None:
            print('first stage')
            return True
        print('not first stage')
        
        return previous_stage.is_approved()
    
    @transition(field=state, source=REVIEWING, target=APPROVED, conditions=[can_review], permission=can_approve)
    def approve(self):
        pass

    @transition(field=state, source=REVIEWING, target=REJECTED, conditions=[can_review], permission=same_approver)
    def reject(self):
        pass

    @transition(field=state, source=[APPROVED, REJECTED], target=REVIEWING, permission=same_approver)
    def review(self):
        pass
# Workflow Type C (ステージ順の制限をつけれるようにしたもの) ここまで