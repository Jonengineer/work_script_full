import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        # Добавляем текущего клиента в группу "notifications_group"
        self.group_name = "notifications_group"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Удаляем клиента из группы "notifications_group"
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def send_notification(self, event):
        # Отправляем сообщение клиенту
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))