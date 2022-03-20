"""
Alternate file to be run in local environment to start app w/ websocket capabilities(for messaging services).
Replaces `flask run`
"""

from web_app import create_app, socketio
from web_app.general import events

app = create_app()

if __name__ == '__main__':
    socketio.run(app)