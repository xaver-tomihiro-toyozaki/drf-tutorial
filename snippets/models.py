from django.db import models
from django.db.models import Max

from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()

    class Meta:
        ordering = ['created']
        
    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super().save(*args, **kwargs)
        
        
import datetime
from django_fsm import RETURN_VALUE, FSMField, transition
from django_fsm import can_proceed
from django.shortcuts import get_object_or_404

class BlogPost(models.Model):
    state = FSMField(default='new', protected=True)

    def can_publish(instance):
        # No publishing after 17 hours
        if datetime.datetime.now().hour > 17:
            return False
        print(True)
        return True

    def can_destroy(self):
        return self.is_under_investigation()

    @transition(field=state, source='new', target='published', conditions=[can_publish], on_error="failed")
    def publish(self):
        """
        Side effects galore
        """

    @transition(field=state, source='*', target='destroyed', conditions=[can_destroy])
    def destroy(self):
        """
        Side effects galore
        """
        
# Issue Type A (不採用の設計らしい)
# class Issue(models.Model):
#     title = models.CharField(max_length=255)
#     workflow_state = FSMField(default=0, protected=True)
#     approved = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def can_approve(self):
#         return True
    
#     def get_now_state(self):
#         return self.workflow_state
    
#     def get_next_state(self):
#         workflow_list = Workflow.objects.filter(issue=self.id).order_by('step')
#         next_step = int(self.workflow_state)
#         for wf in workflow_list:
#             if wf.step > next_step:
#                 next_step = wf.step
#                 break
        
#         if next_step is None:
#             return -1.0
        
#         return next_step
    
#     @transition(field=workflow_state, source='*', target=RETURN_VALUE(0, 1, 2, 3, 4), conditions=[can_approve])
#     def approve(self):
#         step_to_move = self.get_next_state()
#         print(step_to_move)
#         return step_to_move


# class Workflow(models.Model):
#     issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
#     step = models.IntegerField(default=1)
#     reviewer = models.CharField(max_length=255)
#     text = models.TextField(default='')
#     approved = models.BooleanField(default=False)
#     approved_at = models.DateTimeField(null=True, blank=True)
    
#     class Meta:
#         unique_together = ('issue', 'step')
        
#     def save(self, *args, **kwargs):
        
#         last_step = Workflow.objects.filter(issue=self.issue).aggregate(Max('step'))['step__max']
#         if last_step != None:
#             self.step = last_step+1
#         super().save(*args, **kwargs)
# Issue Type A ここまで



# Issue Type B (順番関係ないもの)
class Issue(models.Model):
    title = models.CharField(max_length=255)
    issuer = models.ForeignKey('auth.User', related_name="issuer", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class IssueComment():
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    comment = models.TextField()

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


# Workflow Type C(込み込みのやつ)
class IssueWorkflow(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    STRICT = 'strict'
    OPEN = 'open'
    TYPE_CHOICES = [
        (STRICT, 'strict'),
        (OPEN, 'open')
    ]
    issue_workflow_type = models.CharField(choices=TYPE_CHOICES, default='open', max_length=10)
    
    def is_strict_order(self):
        print('issue workflow id: ', self)
        print('issue_workflow_type:', self.issue_workflow_type)
        return self.issue_workflow_type == self.STRICT
    
class IssueWorkflowStage(models.Model):
    issue_workflow = models.ForeignKey(IssueWorkflow, on_delete=models.CASCADE)
    ALL = 'all'
    ONE = 'one'
    TYPE_CHOICES = [
        (ALL, 'all'),
        (ONE, 'one')
    ]
    issue_workflow_stage_type = models.CharField(choices=TYPE_CHOICES, default=ALL, max_length=5)
    # parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
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
            print('all user have approved on the stage.')
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
    
    def same_approver(self, user):
        return user == self.approver
    
    def can_approve(self, user):
        if not self.same_approver(user):
            print('not assigned user')
            return False
        print('assigned user')
        
        if not self.issue_workflow_stage.issue_workflow.is_strict_order():
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
