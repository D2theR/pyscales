from channels.routing import route
from .scale_conn import ws_connect


channel_routing = [
    route('websocket.connect', ws_connect)
]