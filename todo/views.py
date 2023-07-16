from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from .models import TodoItem, TodoItemAccess, AccessLog
from .serializers import TodoItemSerializer, AccessLogSerializer


class TodoItemListView(APIView):
    def get(self, request):
        todo_items = TodoItem.objects.filter(shared_with=request.user) | TodoItem.objects.filter(owner=request.user)
        serializer = TodoItemSerializer(todo_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TodoItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoItemDetailView(APIView):
    def get_object(self, pk):
        try:
            return TodoItem.objects.get(pk=pk)
        except TodoItem.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        todo_item = self.get_object(pk)
        serializer = TodoItemSerializer(todo_item)
        return Response(serializer.data)

    def put(self, request, pk):
        todo_item = self.get_object(pk)

        if not TodoItemAccess.objects.filter(todo_item=todo_item, user=request.user).exists():
            return Response({'error': 'You do not have access to modify this TODO item'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = TodoItemSerializer(todo_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        todo_item = self.get_object(pk)

        if not TodoItemAccess.objects.filter(todo_item=todo_item, user=request.user).exists():
            return Response({'error': 'You do not have access to delete this TODO item'},
                            status=status.HTTP_403_FORBIDDEN)

        todo_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TodoItemShareView(APIView):
    def post(self, request, pk):
        todo_item = TodoItem.objects.get(pk=pk)
        user_ids = request.data.get('user_ids', [])
        access_level = request.data.get('access_level', 'RO')

        if not user_ids:
            return Response({'error': 'Please provide at least one user ID'}, status=status.HTTP_400_BAD_REQUEST)

        for user_id in user_ids:
            user = User.objects.get(pk=user_id)
            can_edit = access_level == 'RW'
            needs_approval = access_level == 'AP'

            TodoItemAccess.objects.get_or_create(todo_item=todo_item, user=user,
                                                 defaults={'can_edit': can_edit, 'needs_approval': needs_approval})

        serializer = TodoItemSerializer(todo_item)
        return Response(serializer.data)


class TodoItemApproveView(APIView):
    def post(self, request, pk):
        todo_item = TodoItem.objects.get(pk=pk)

        if not TodoItemAccess.objects.filter(todo_item=todo_item, user=request.user, can_edit=True).exists():
            return Response({'error': 'You do not have permission to approve or reject changes'},
                            status=status.HTTP_403_FORBIDDEN)

        approval_status = request.data.get('approval_status')

        if approval_status not in ['A', 'R']:
            return Response({'error': 'Invalid approval status'}, status=status.HTTP_400_BAD_REQUEST)

        todo_item.approval_status = approval_status
        todo_item.save()

        serializer = TodoItemSerializer(todo_item)
        return Response(serializer.data)


class AccessLogView(APIView):
    def get(self, request):
        access_logs = AccessLog.objects.filter(user=request.user)
        serializer = AccessLogSerializer(access_logs, many=True)
        return Response(serializer.data)

    def log_activity(self, user, todo_item, activity):
        AccessLog.objects.create(user=user, todo_item=todo_item, activity=activity)

    def put(self, request, pk):
        todo_item = self.get_object(pk)

        if not TodoItemAccess.objects.filter(todo_item=todo_item, user=request.user).exists():
            return Response({'error': 'You do not have access to modify this TODO item'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TodoItemSerializer(todo_item, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Log the activity
            self.log_activity(request.user, todo_item, 'TODO item updated')

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        todo_item = self.get_object(pk)

        if not TodoItemAccess.objects.filter(todo_item=todo_item, user=request.user).exists():
            return Response({'error': 'You do not have access to delete this TODO item'}, status=status.HTTP_403_FORBIDDEN)

        todo_item.delete()

        # Log the activity
        self.log_activity(request.user, todo_item, 'TODO item deleted')

        return Response(status=status.HTTP_204_NO_CONTENT)
