# urls.py

from django.urls import path
from .views import TodoItemListCreateView, CategoryListCreateDeleteView, TodoRetrieveDeleteUpdateView, \
    TodoChangesApprovalView, TodoShareWithUserView

urlpatterns = [
    path('api/category/', CategoryListCreateDeleteView.as_view(), name='category-list-create'),
    path('api/category/<int:id>/', CategoryListCreateDeleteView.as_view(), name='category-delete'),
    path('api/todo/', TodoItemListCreateView.as_view(), name='todo-list-create'),
    path('api/todo/<int:id>/', TodoRetrieveDeleteUpdateView.as_view(), name='todo-retrieve-update-delete'),
    path('api/todo_changes/<int:id>/', TodoChangesApprovalView.as_view(), name='todo-changes-approval'),
    path('api/todo_share/', TodoShareWithUserView.as_view(), name='todo-share'),
]
