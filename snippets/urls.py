# from django.urls import path, include
# from rest_framework.urlpatterns import format_suffix_patterns
# from snippets import views


# urlpatterns = [
#     path('', views.api_root),
#     path('snippets/', views.SnippetList.as_view(), name='snippet-list'),
#     path('snippets/<int:pk>/', views.SnippetDetail.as_view(), name='snippet-detail'),
#     path('snippets/<int:pk>/highlight/', views.SnippetHighlight.as_view(), name='snippet-highlight'),
#     path('users/', views.UserList.as_view(), name='user-list'),
#     path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
# ]

# urlpatterns = format_suffix_patterns(urlpatterns)


# from snippets.views import SnippetViewSet, UserViewSet, api_root
# from rest_framework import renderers

# snippet_list = SnippetViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })
# snippet_detail = SnippetViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
# snippet_highlight = SnippetViewSet.as_view({
#     'get': 'highlight'
# }, renderer_classes=[renderers.StaticHTMLRenderer])
# user_list = UserViewSet.as_view({
#     'get': 'list'
# })
# user_detail = UserViewSet.as_view({
#     'get': 'retrieve'
# })

# urlpatterns = format_suffix_patterns([
#     path('', api_root),
#     path('snippets/', snippet_list, name='snippet-list'),
#     path('snippets/<int:pk>/', snippet_detail, name='snippet-detail'),
#     path('snippets/<int:pk>/highlight/', snippet_highlight, name='snippet-highlight'),
#     path('users/', user_list, name='user-list'),
#     path('users/<int:pk>/', user_detail, name='user-detail')
# ])


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from snippets import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet,basename="snippet")
router.register(r'users', views.UserViewSet,basename="user")
router.register(r'blogpost', views.BlogPostViewSet, basename="blogpost")
router.register(r'issue', views.IssueViewSet, basename='issue')

workflow_list = views.WorkflowViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

workflow_detail = views.WorkflowViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('issue/<int:issue_pk>/workflow/', workflow_list, name='workflow-list'),
    path('issue/<int:issue_pk>/workflow/<int:pk>/', workflow_detail, name='workflow-detail'),
]