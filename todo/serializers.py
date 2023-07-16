from rest_framework import serializers

from users.models import User
from .models import TodoItem, TodoItemAccess, AccessLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class TodoItemAccessSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TodoItemAccess
        fields = ['user', 'can_edit', 'needs_approval']


class TodoItemSerializer(serializers.ModelSerializer):
    shared_with = TodoItemAccessSerializer(many=True, read_only=True)

    class Meta:
        model = TodoItem
        fields = '__all__'

    def create(self, validated_data):
        shared_with_data = validated_data.pop('shared_with')
        todo_item = TodoItem.objects.create(**validated_data)
        for access_data in shared_with_data:
            user_data = access_data.pop('user')
            user = User.objects.get(id=user_data['id'])
            TodoItemAccess.objects.create(todo_item=todo_item, user=user, **access_data)
        return todo_item

    def update(self, instance, validated_data):
        shared_with_data = validated_data.pop('shared_with')
        TodoItemAccess.objects.filter(todo_item=instance).delete()
        for access_data in shared_with_data:
            user_data = access_data.pop('user')
            user = User.objects.get(id=user_data['id'])
            TodoItemAccess.objects.create(todo_item=instance, user=user, **access_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AccessLogSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    todo_item = TodoItemSerializer()

    class Meta:
        model = AccessLog
        fields = ['user', 'todo_item', 'timestamp', 'activity']
