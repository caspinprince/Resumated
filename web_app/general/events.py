from flask import session, request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, send
from web_app import socketio


@socketio.on('joined', namespace='/chat')
def joined(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'username': current_user.username}, room=request.sid, namespace='/chat')


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': message['msg'], 'username': current_user.username}, room=room, namespace='/chat')


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room, namespace='/chat')


