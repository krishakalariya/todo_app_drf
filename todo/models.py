from django.utils import timezone

from django.db import models

from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Create your models here.
class TodoItem(models.Model):
    status_choice = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=status_choice, default='IN_PROGRESS')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    due_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_todos')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class TodoShareWithAccess(models.Model):
    todo_access = [
        ('ReadOnly', 'ReadOnly'),
        ('ReadWriteOnly', 'ReadWriteOnly'),
    ]

    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='todos_viewers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_todo')
    access_status = models.CharField(max_length=20, choices=todo_access, default='ReadOnly')

    class Meta:
        unique_together = ('todo_item', 'user')


class TodoChangesApproval(models.Model):
    change_status = [
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Pending', 'Pending')
    ]

    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='todo_changes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_changes')
    changes = models.JSONField()
    status = models.CharField(max_length=20, choices=change_status, default='Pending')


class AccessLog(models.Model):
    log_status = [
        ('Created', 'Created'),
        ('Updated', 'Updated'),
        ('Deleted', 'Deleted')
    ]
    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    changes = models.JSONField()
    status = models.CharField(max_length=20, choices=log_status, default='Updated')

    def __str__(self):
        return f'{self.todo_item.title} - {self.user.username} - {self.timestamp}'
