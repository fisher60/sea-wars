import asyncio
import uuid
from typing import Coroutine

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    WebSocket,
    status
)

from fastapi.websockets import WebSocketState

from game import Player, Territory, game_update

app = FastAPI()

current_users: dict[str: Player] = {}


class Message:
    def __init__(self, message_type: str, data: dict):
        self.message_type = message_type
        self.data = data


primary_queue: dict[uuid.UUID: list[Message]] = {}


class WebSocketHandler:
    def __init__(self, websocket: WebSocket):
        self.ws: WebSocket = websocket
        self.message_queue: list[Message] = []
        self.task_queue: list[Coroutine] = []


def add_to_primary_queue(player_uuid: uuid.UUID, message: Message):
    if primary_queue.get(player_uuid):
        primary_queue[player_uuid].append(message)
    else:
        primary_queue[player_uuid] = [message]


async def send_chat(handler: WebSocketHandler, chat) -> None:
    await handler.ws.send_text(chat)


async def send_player_update(ws_handler: WebSocketHandler, player: Player):
    await ws_handler.ws.send_json(
        {
            "message": {
                "player": {
                    "uuid": str(player.player_id),
                    "money": player.money,
                    "army": player.army,
                    "workers": player.workers
                },
                "territories": {
                    x: [territory.pos_x, territory.pos_y] for x, territory in enumerate(player.territories)
                }
            }
        }
    )


@app.post("/buy_territory")
async def buy_territory(territory_x: int, territory_y: int, player_uuid: uuid.UUID = Header()):
    ...


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = Cookie(default=None)):
    """Handles all game logic including client inputs and server updates."""
    ws_handler = WebSocketHandler(websocket)
    await ws_handler.ws.accept()

    # Check if the user sent a player token
    if token is None:
        player_uuid = uuid.uuid4()
        player = Player(player_id=player_uuid, territories=[Territory(1, 1)])
        current_users[str(player_uuid)] = player
    # If the user sent a player token, attempt to retrieve the player data
    else:
        if current_users.get(token):
            player = current_users[token]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"player with UUID {token} does not exist."
            )

    # Send player data immediately to avoid delay from game update wait time
    await send_player_update(ws_handler, player)

    async def ws_receiver(handler: WebSocketHandler):
        """Receive messages from client."""
        while handler.ws.client_state is WebSocketState.CONNECTED:
            message = await handler.ws.receive_json()
            message_obj = Message(message_type=message["type"], data=message["message"])
            handler.message_queue.append(message_obj)

    async def ws_sender(handler: WebSocketHandler):
        """Send any/all messages to the client. This includes world updates and all game information to the client."""

        # Add the main player game update to the task queue
        while handler.ws.client_state is WebSocketState.CONNECTED:
            handler.task_queue.append(game_update(player))

            # Convert all existing client messages to executable tasks
            while handler.message_queue:
                this_message = handler.message_queue.pop(0)

                # Create 'chat' type tasks and add to queue
                if this_message.message_type == "chat":
                    handler.task_queue.append(send_chat(handler, this_message.data))

            # Execute all existing tasks in the current queue
            while handler.task_queue:
                await handler.task_queue.pop(0)

            # Send main game update date to client
            await send_player_update(handler, player)

    tasks = [ws_receiver(ws_handler), ws_sender(ws_handler)]

    # Send/receive tasks over websocket until any exception occurs
    # TODO: error handling in tasks
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
