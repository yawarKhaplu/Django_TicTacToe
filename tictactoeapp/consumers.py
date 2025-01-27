import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game import *
import uuid


boxvalues = {"one": 0, "two": 1, "three": 2, "four": 3, "five": 4, "six": 5, "seven": 6, "eight": 7, "nine": 8}

class MyConsumer(AsyncWebsocketConsumer):
    TURN = "O"
    players = []
    game_state = {"current_turn": None}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        # Accept the WebSocket connection
        player_id = uuid.uuid4()
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Connecccted',
            "turn": MyConsumer.TURN,
        }))
        MyConsumer.players.append({"id": player_id, "ws": self})
        if len(MyConsumer.players) == 2:
            MyConsumer.game_state["current_turn"] = MyConsumer.players[0]["id"]
        await self.channel_layer.group_add(f"active_game", self.channel_name)


    async def disconnect(self, close_code):
        # Handle WebSocket disconnection
        await self.channel_layer.group_discard(f"active_game", self.channel_name)
        pass

    async def receive(self, text_data):
        # Handle received WebSocket messages
        data = json.loads(text_data)
        # print(data)
        which_box = data["clicked"]
        MyConsumer.TURN = "O" if MyConsumer.TURN == "X" else "X"
        update_dashboard(self.TURN, boxvalues[which_box])
        draw = check_draw()
        win = check_win()
        # Send a message to the group
        await self.channel_layer.group_send(
            f"active_game",
            {
                'type': 'game.message',
                'message': "Game state updated",
                'turn': MyConsumer.TURN,
                'id': which_box,
                'win': win,
                'draw': draw,
            }
        )

    async def game_message(self, event):
        # print(f"Game status: {message}, win: {win}, draw: {draw}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'hi': "hi there",
            'turn': event['turn'],
            'id': event['id'],
            'draw': event['draw'],
            'win': event['win'],
        }))
