# urls.py

from django.urls import path
from .views import TodoItemListView, TodoItemDetailView, TodoItemShareView, TodoItemApproveView, AccessLogView

urlpatterns = [
    path('api/todo/', TodoItemListView.as_view(), name='todo-list'),
    path('api/todo/<int:pk>/', TodoItemDetailView.as_view(), name='todo-detail'),
    path('api/todo/<int:pk>/share/', TodoItemShareView.as_view(), name='todo-share'),
    path('api/todo/<int:pk>/approve/', TodoItemApproveView.as_view(), name='todo-approve'),
    path('api/access-log/', AccessLogView.as_view(), name='access-log'),
]
