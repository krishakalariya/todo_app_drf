from datetime import timezone

from django.db import models

from users.models import User


# Create your models here.
class TodoItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_todos')
    shared_with = models.ManyToManyField(User, through='TodoItemAccess')

    def __str__(self):
        return self.title


class TodoItemAccess(models.Model):
    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    needs_approval = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.todo_item.title} - {self.user.username}'


class AccessLog(models.Model):
    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    activity = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.todo_item.title} - {self.user.username} - {self.timestamp}'
