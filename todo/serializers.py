from rest_framework import serializers

from users.models import User
from .models import TodoItem, AccessLog, Category, TodoShareWithAccess


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class TodoItemAccessSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TodoShareWithAccess
        fields = ['user', 'can_edit', 'needs_approval']


class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = ['id', 'title', 'description', 'status', 'category', 'due_date']


class AccessLogSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    todo_item = TodoItemSerializer()

    class Meta:
        model = AccessLog
        fields = ['user', 'todo_item', 'timestamp', 'activity']


class TodoShareWithSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoShareWithAccess
        fields = ['id', 'todo_item', 'user', 'access_status']
