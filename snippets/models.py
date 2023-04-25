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



# Issue Type B (設計予定のものらしい)
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
    
    @transition(field=state, source=REVIEWING, target=APPROVED, conditions=[can_review])
    def approve(self):
        pass

    @transition(field=state, source=REVIEWING, target=REJECTED, conditions=[can_review])
    def reject(self):
        pass

    @transition(field=state, source=[APPROVED, REJECTED], target=REVIEWING)
    def review(self):
        pass


