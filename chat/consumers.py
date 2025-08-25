# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Project, ChatSession, Message
from .utils import fetch_sheet_data, alternating_workflow, export_to_sheet

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.project = Project.objects.filter(user=self.user).order_by('-id').first()
        if not self.project:
            self.project = Project.objects.create(user=self.user, name="Default Project")
            ChatSession.objects.get_or_create(project=self.project, status='active')
        self.room_group_name = f'chat_{self.project.id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        chat_session = self.project.chatsession_set.first()
        Message.objects.create(chat_session=chat_session, sender='user', content=message)

        if message.startswith('start analysis:'):
            parts = message.split('sheet ')[1].split(', prices ')
            sheet_link = parts[0].strip()
            price_str = parts[1].strip()
            price_list = json.loads(price_str)

            self.project.input_sheet_link = sheet_link
            self.project.price_list_json = price_list
            self.project.save()

            await self.send_bot_message("Starting analysis... Fetching sheet data.")
            sheet_data = fetch_sheet_data(sheet_link)

            await self.send_bot_message("Running AI+Code workflow with explanations...")
            final_df, summary = alternating_workflow(self.project, sheet_data, price_list)

            steps = self.project.analysisstep_set.all().order_by('timestamp')
            for step in steps:
                explanation = f"{step.step_type.upper()} Step: Input was '{step.input_data[:100]}...'. Output: {step.output_data[:200]}..."
                await self.send_bot_message(explanation)

            await self.send_bot_message(f"Full Summary: {summary}")
            await self.send_bot_message(f"Total Cost Estimation: ${final_df['optimized_cost'].sum():.2f} (optimized from base ${final_df['total_cost'].sum():.2f})")

            output_link = export_to_sheet(final_df)
            self.project.output_sheet_link = output_link
            self.project.save()

            await self.send_bot_message(f"Final Optimized Sheet: {output_link}")
        else:
            await self.send_bot_message(f"Message received: {message}. Use 'start analysis: sheet <link>, prices <json>' to begin.")

    async def send_bot_message(self, content):
        chat_session = self.project.chatsession_set.first()
        Message.objects.create(chat_session=chat_session, sender='bot', content=content)
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': content
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'message': event['message']}))