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
            self.player_symbol = "O"
            self.player_id = uuid.uuid4()
            self.room_name = waiting_room
            # self.room_group_name = f"game_{self.room_name}"
            # print("Room Name: " , self.room_name)
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({
                "player_symbol": self.player_symbol
            }))
            cache.delete("waiting_room")
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "game.start",
                    "status": "started",
                    "message": f"Welcome {self.player_symbol}",
                    "player_symbol": self.player_symbol,
                    "player_symbols": {"X": "Player 1", "O": "Player 2"}
                }
            )
            # both players are now connected starting the game
            
        else:
            # Create new waiting room
            self.player_symbol = "X"
            self.player_id = uuid.uuid4()
            self.room_name = f"game_{str(self.player_id)[:4]}"
            cache.set("waiting_room", self.room_name, timeout=30)
            print("Room Name: " , self.room_name)
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            self.status = "waiting"
            await self.send(text_data=json.dumps({
            "status": "waiting",
            "message": f"Hi {self.player_symbol} Waiting for opponent...",
            "player_symbol": self.player_symbol
        }))
        print(self.player_symbol, "joined the game") 
        # await self.game_start(self.room_name)
        # Accept the WebSocket connection
        # print(get_random_message())
        MyConsumer.players.append(self.player_id)
        # await self.accept()
        await self.wait_for_one_to_play()
        # if len(MyConsumer.players)<=2:
        #     await self.channel_layer.group_add(f"active_game", self.channel_name)
        # else:
        #     await self.channel_layer.group_add(f"spectrators",self.channel_name)

        if self.player_symbol == "X":
            # First player gets 'X' turn
            self.turn = "O"
        else:
            self.turn = "X"
        # else:
        #     self.turn = ""
        #     self.player = "Spectrator"
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
        print(self.player_symbol, "left the game")
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "game.start",
                "status": "disconnected",
                "message": f"{self.player_symbol} Left the Game!",
                "player_symbols": {"X": "Player 1", "O": "Player 2"},
                "player_symbol": self.player_symbol
            }
        )
        if cache.get("waiting_room") == self.room_name:
            cache.delete("waiting_room")
        await self.channel_layer.group_discard(self.room_name, self.channel_name)


    async def receive(self, text_data):
        # Handle received WebSocket messages
        data = json.loads(text_data)
        # print(data)
        if 'clicked' in data:
            which_box = data["clicked"]
            if self.player_symbol == "X" or self.player_symbol == "O":
                update_dashboard(self.turn, boxvalues[which_box])
            draw = check_draw()
            win = check_win()
            if win == "X won" or win == "O won":
                new_game()
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
                    "player_symbol": self.player_symbol,
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
            "status": event["status"],
            "turn": self.turn,
            "player_symbol": event["player_symbol"],
            "message": event["message"],
            "player_symbols": event["player_symbols"]
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
            "player_symbol": event['player_symbol'],
        }))
    async def clear_all_boxvalues(self):
        await self.channel_layer.group_send(
            self.room_name,{
            'clear': True,
            "turn": self.turn,
        })
    async def wait_for_one_to_play(self):
        pass