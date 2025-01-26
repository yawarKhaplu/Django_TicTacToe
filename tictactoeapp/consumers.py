import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game import *
boxvalues = {"one": 0, "two": 1, "three": 2, "four": 3, "five": 4, "six": 5, "seven": 6, "eight": 7, "nine": 8}

class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TURN = "O"

    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Connecccted'
        }))

        # Add the WebSocket connection to a group
        await self.channel_layer.group_add(f"active_game", self.channel_name)


    async def disconnect(self, close_code):
        # Handle WebSocket disconnection
        await self.channel_layer.group_discard(f"active_game", self.channel_name)
        pass

    async def receive(self, text_data):
        # Handle received WebSocket messages
        print(f"Message received: {text_data}")

        draw = check_draw()
        win = check_win()
        data = json.loads(text_data)
        print(data)
        which_box = data["clicked"]
        print(boxvalues[which_box])

        self.TURN = "O" if self.TURN == "X" else "X"
        update_dashboard(self.TURN, boxvalues[which_box])
        await self.send(text_data=json.dumps({
            'draw': draw,
            'win': win,
            'turn': self.TURN,
            'id': which_box,
        }))

        # Send a message to the group
        await self.channel_layer.group_send(
            f"active_game",
            {
                'type': 'game.message',
                'message': "Game state updated",
                'turn': self.TURN,
                'id': which_box,
                'draw': draw,
                'win': win,
            }
        )

    async def game_message(self, event):
        # Handle messages sent to the group
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'hi': "hi there",
            'turn': event['turn'],
            'id': event['id'],
            'draw': event['draw'],
            'win': event['win'],
        }))
