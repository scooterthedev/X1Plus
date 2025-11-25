import asyncio
import logging
from x1plus.services.x1plusd.dbus import X1PlusDBusService

logger = logging.getLogger(__name__)

IRC_INTERFACE = 'x1plus.irc'
IRC_PATH = '/x1plus/irc'

class IRCService(X1PlusDBusService):
    def __init__ (self, daemon, **kwargs):
        self.daemon = daemon
        self.reader = None
        self.writer = None
        self.connected = False
        self.nick = ""
        self.channel = ""
        self.server = ""
        self.port = 6667
        self.task_handle = None

        super().__init__(
            router=daemon.router,
            dbus_interface=IRC_INTERFACE,
            dbus_path=IRC_PATH,
            **kwargs
        )

    async def dbus_Connect(self, req):
        self.server = str(reg.get('server', 'irc.hackclub.com'))
        self.port = int(reg.get('port', 6667))
        self.nick = str(reg.get('nick', 'the3dprinter'))
        self.channel = str(reg.get('channel', '#lounge'))

        if self.connected:
            await self.disconnect()

        self.task_handle = asyncio.create_task(self.run_client())
        return {'status': 'connecting'}
    
    async def dbus_Diconnect(self, req):
        await self.disconnect()
        return {'status': 'disconnected'}
    
    async def dbusSendMessage(self, req):
        msg = str(reg.get('message', ''))
        if not self.connected or not self.writer:
            return {'status': 'not connected'}
        
        try:
            self.writer.write(f"PRIVMSG {self.channel} :{msg}\r\n".encode())
            await self.writer.drain()
            await self.emit_signal("MessageReeceived", {'sender': self.nick, 'message': msg, 'type': 'self'})
            return {'status': 'message sent'}
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {'status': 'error sending message'}
        
    async def disconnect(self):
        self.connected = False
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except:
                pass
            self.writer = None
            self.reader = None
        if self.task_handle:
            self.task_handle.cancel()
            try:
                await self.task_handle
            except asyncio.CancelledError:
                pass
            self.task_handle = None
        await self.emit_signal("StatusChanged", {'connected': False})

    async def _run_client(self):
        try:
            logger.info(f"Connecting to IRC server {self.server}:{self.port}")
            await self.emit_signal("MessageReceived", {'sender': 'System', 'message': f'Connecting to {self.server}:{self.port}', 'type': 'system'})
            self.reader, self.writer = await asyncio.open_connection(self.server, self.port)