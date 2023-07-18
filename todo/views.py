import copy

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from .models import TodoItem, TodoShareWithAccess, AccessLog, Category, TodoChangesApproval
from .serializers import TodoItemSerializer, AccessLogSerializer, CategorySerializer, TodoShareWithSerializer, \
    TodoLogsSerializers
from rest_framework import generics
from django.core.serializers import serialize


class CategoryListCreateDeleteView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


class TodoItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TodoItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        if self.request.method == "GET":
            if due_date := self.request.GET.get('due_date'):
                return TodoItem.objects.filter(todos_viewers__user=self.request.user,
                                               due_date__gte=due_date) | TodoItem.objects.filter(
                    owner=self.request.user, due_date__gte=due_date)
            else:
                return TodoItem.objects.filter(todos_viewers__user=self.request.user) | TodoItem.objects.filter(
                    owner=self.request.user)
        return TodoItem.objects.all()

    def post(self, request):
        serializer = TodoItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        todo_instance = serializer.save(owner=request.user)
        AccessLog.objects.create(todo_item=todo_instance, user=request.user, status='Created', changes={
            'old_data': {},
            'new_data': serializer.data
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TodoRetrieveDeleteUpdateView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = TodoItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.method == 'GET':
            return TodoItem.objects.filter(todos_viewers__user=self.request.user,
                                           todos_viewers__access_status='ReadOnly') | TodoItem.objects.filter(
                owner=self.request.user)
        elif self.request.method == 'PUT':
            return TodoItem.objects.filter(todos_viewers__user=self.request.user,
                                           todos_viewers__access_status='ReadWriteOnly') | TodoItem.objects.filter(
                owner=self.request.user)
        else:
            return TodoItem.objects.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner == request.user:
            serializer = self.serializer_class(instance=instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            old_data = copy.copy(serialize('json', [instance]))
            serializer.save()
            AccessLog.objects.create(todo_item=instance, user=request.user, changes={
                'old_data': old_data,
                'new_data': serializer.data
            })
            return Response('Todo has been updated sucessfully !', status=status.HTTP_200_OK)
        else:
            updated_fileds = ['title', 'description', 'status', 'category', 'due_date']
            updated_data = {}
            for field, value in request.data.items():
                if field in updated_fileds:
                    updated_data[field] = value

            TodoChangesApproval.objects.create(todo_item=instance, user=request.user, changes=updated_data)
            return Response('Request for update todo has been submitted ! Please wait for owner approval.',
                            status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            AccessLog.objects.create(todo_item=instance, user=request.user, changes={
                'old_data': {'is_active': True},
                'new_data': {'is_active': False}
            })
            instance.is_active = False
            instance.save()
            return Response('Todo has been In-activated !',
                            status=status.HTTP_200_OK)
        else:
            AccessLog.objects.create(todo_item=instance, user=request.user, changes={
                'old_data': {'is_active': False},
                'new_data': {'is_active': True}
            })
            instance.is_active = True
            return Response('Todo has been activated !',
                            status=status.HTTP_200_OK)


class TodoChangesApprovalView(generics.UpdateAPIView):
    serializer_class = TodoItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return TodoChangesApproval.objects.filter(todo_item__owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == "Pending":
            if request.data.get('status', None) == 'Approved':
                serializer = self.serializer_class(instance=instance.todo_item, data=instance.changes)
                serializer.is_valid(raise_exception=True)
                old_data = copy.copy(serialize('json', [instance]))
                serializer.save()
                AccessLog.objects.create(todo_item=instance.todo_item, user=request.user, changes={
                    'old_data': old_data,
                    'new_data': serializer.data
                })
                instance.status = 'Approved'
                instance.save()
                return Response('Changes has been approved and reflected in Todo.', status=status.HTTP_200_OK)
            elif request.data.get('status', None) == 'Rejected':
                instance.status = 'Rejected'
                instance.save()
                return Response('Changes has been rejected.', status=status.HTTP_200_OK)
            else:
                raise ValidationError('Please pass valid status !')
        else:
            raise ValidationError('Changes are not in pending state !')


class TodoShareWithUserView(generics.UpdateAPIView):
    serializer_class = TodoShareWithSerializer
    permission_classes = [IsAuthenticated]
    queryset = TodoShareWithAccess.objects.all()

    def update(self, request, *args, **kwargs):
        if TodoItem.objects.filter(id=request.data.get('todo_item'), owner=self.request.user).exists():
            if instance := TodoShareWithAccess.objects.filter(todo_item=request.data.get('todo_item'),
                                                              user_id=request.data.get('user')):
                serializer = self.serializer_class(instance=instance.first(), data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response('Update successfully !', status=status.HTTP_200_OK)
            else:
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response('Created successfully !', status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied


class TodoLogsView(generics.ListAPIView):
    serializer_class = TodoLogsSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AccessLog.objects.filter(todo_item=self.kwargs.get('todo_item'), todo_item__owner=self.request.user)
