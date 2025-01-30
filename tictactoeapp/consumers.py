import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tictactoe.settings")  # Replace with your settings module
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game import *
import uuid
from django.core.cache import cache
boxvalues = {"one": 0, "two": 1, "three": 2, "four": 3, "five": 4, "six": 5, "seven": 6, "eight": 7, "nine": 8}
# def get_random_message():
#     # Get a random message from the Message model
#     random_message = FirstPopupMessages.objects.order_by('?').first()
#     return random_message.text if random_message else "Best of Luck."
def get_random_message():
    
    return "Best of Luck"

class MyConsumer(AsyncWebsocketConsumer):
    TURN = "O"
    players = []
    game_state = {"current_turn": None}
    groups = ["active_game"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        waiting_room = cache.get("waiting_room")
        if waiting_room:
            # join existing room and start game
            self.player_id = uuid.uuid4()
            self.room_name = waiting_room
            # self.room_group_name = f"game_{self.room_name}"
            print("Room Name: " , self.room_name)
            await self.channel_layer.group_add(f"waiting_room", self.channel_name)
            await self.accept()
            self.status = "started"
            # Remove waiting room from cache
            cache.delete(waiting_room)
            # Send Both Players to start game
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "game.start",
                    "status": "started",
                    "message": "Game starting!",
                    "player_symbols": {"player_1": "X", "player_2": "O"},
                },
            )   
        else:
            # Create new waiting room

            self.player_id = uuid.uuid4()
            self.room_name = f"game_{str(self.player_id)[:4]}"
            cache.set("waiting_room", self.room_name)
            print("Room Name: " , self.room_name)
            await self.channel_layer.group_add(self.room_name, str(self.player_id)[:4])
            await self.accept()
            self.status = "waiting"
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "game.start",
                    "status": "waiting",
                    "message": "Game starting!",
                    "player_symbols": {"player_1": "X", "player_2": "O"},
                    "player_symbols": "X"
                },
            ) 

        await self.game_start(self.room_name)
        # Accept the WebSocket connection
        print(get_random_message())
        MyConsumer.players.append(self.player_id)
        # await self.accept()
        await self.wait_for_one_to_play()
        # if len(MyConsumer.players)<=2:
        #     await self.channel_layer.group_add(f"active_game", self.channel_name)
        # else:
        #     await self.channel_layer.group_add(f"spectrators",self.channel_name)

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
        # await self.send(text_data=json.dumps({
        #     # "first_message": random_message,
        #     'message': 'Connected',
        #     "turn": self.turn,
        #     "player":self.player
        #     # "turn": MyConsumer.TURN,
        # }))
        # if len(MyConsumer.players) == 2:
        #     MyConsumer.game_state["current_turn"] = MyConsumer.players[0]

    async def disconnect(self, close_code):
        # Clean up if the player leaves before the game starts
        if cache.get("waiting_room") == self.room_name:
            cache.delete("waiting_room")
        await self.channel_layer.group_discard(self.room_name, self.channel_name)


    async def receive(self, text_data):
        # Handle received WebSocket messages
        data = json.loads(text_data)
        # print(data)
        if 'clicked' in data:
            which_box = data["clicked"]
            if self.player == "X" or self.player == "O":
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
    async def game_start(self, event):
        # Send game start message to both players
        await self.send(text_data=json.dumps({
            "status": self.status
        }))
        # await self.send(text_data=f"You are Player {event['player_symbols']['player_2']}")

        
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
    async def wait_for_one_to_play(self):
        pass