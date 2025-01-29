import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game import *
import uuid


boxvalues = {"one": 0, "two": 1, "three": 2, "four": 3, "five": 4, "six": 5, "seven": 6, "eight": 7, "nine": 8}

class MyConsumer(AsyncWebsocketConsumer):
    TURN = "O"
    players = []
    game_state = {"current_turn": None}
    groups = ["active_game", "spectrators"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        # Accept the WebSocket connection
        self.player_id = uuid.uuid4()
        MyConsumer.players.append(self.player_id)
        await self.accept()
        if len(MyConsumer.players)<=2:
            await self.channel_layer.group_add(f"active_game", self.channel_name)
        else:
            await self.channel_layer.group_add(f"spectrators",self.channel_name)

        if self.players[0] == self.player_id:
            # First player gets 'X' turn
            self.turn = "X"
            self.player = "X"
        elif self.players[1] == self.player_id:
            self.turn = "O"
            self.player = "O"
        else:
            self.turn = ""
            self.player = "Spectrator"
            # await self.send(text_data=json.dumps({'player':self.turn}))
        await self.send(text_data=json.dumps({
            'message': 'Connected',
            'turn': self.turn,
            "player":self.player
            # "turn": MyConsumer.TURN,
        }))
        if len(MyConsumer.players) == 2:
            MyConsumer.game_state["current_turn"] = MyConsumer.players[0]


    async def disconnect(self, close_code):
        # Handle WebSocket disconnection
        MyConsumer.players.remove(self.player_id)
        await self.channel_layer.group_discard(f"active_game", self.channel_name)
        pass

    async def receive(self, text_data):
        # Handle received WebSocket messages
        data = json.loads(text_data)
        # print(data)
        if 'clicked' in data:
            which_box = data["clicked"]
            update_dashboard(self.turn, boxvalues[which_box])
            draw = check_draw()
            win = check_win()
            # Send a message to the group
            for group in self.groups:
                await self.channel_layer.group_send(
                group,
                {
                    'type': 'game.message',
                    'message': "Game state updated",
                    'turn': self.turn,
                    'id': which_box,
                    'win': win,
                    'draw': draw,
                    "player": self.player,
                }
            )
            
        elif 'reset' in data:
            new_game()
            await self.clear_all_boxvalues()
        else:
            print("Unknown message")
            print(data)

    async def game_message(self, event):
        # print(f"Game status: {message}, win: {win}, draw: {draw}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'turn': event['turn'],
            'id': event['id'],
            'draw': event['draw'],
            'win': event['win'],
            "player": event['player'],
        }))
    async def clear_all_boxvalues(self):
        await self.channel_layer.group_send(text_data=json.dumps(
            "active_game",{
            'clear': True,
            "turn": self.turn,
        }))