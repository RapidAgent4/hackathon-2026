from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from Dictionaries.matcher import User, form_match_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

waiting_pool = []
active_rooms = {}


@app.route('/')
def home():
    return render_template('index.html')


# 1. REAL HUMAN JOINS THE QUEUE
@socketio.on('join_queue')
def handle_join_queue(data):
    mode = "1on1" if data.get('mode') == "one_on_one" else "group"
    new_user = User(
        user_id=request.sid,
        real_name=data.get('real_name', "Alex Rivera '27"),
        bio=data.get('handle', "@alex.marist"),
        interests=data.get('interests', ["Coffee ☕"]),
        mode=mode
    )

    # Check if an active Group room (< 5 people) already shares an interest
    if mode == "group":
        for room_id, room in active_rooms.items():
            if room['mode'] == "group" and len(room['members']) < 5:
                if new_user.interests.intersection(set(room['common_interests'])):
                    used_aliases = {m.alias for m in room['members']}
                    while new_user.alias in used_aliases:
                        new_user = User(
                            request.sid,
                            new_user.real_name,
                            new_user.bio,
                            list(new_user.interests),
                            mode="group"
                        )

                    room['members'].append(new_user)
                    join_room(room_id, sid=request.sid)
                    broadcast_room_state(room)
                    return

    # Otherwise, run matcher.py against the waiting pool
    room = form_match_room(waiting_pool, new_user, similarity_threshold=0.05)

    if room is None:
        waiting_pool.append(new_user)
        emit('waiting', {'message': 'Waiting for other Marist students with matching interests...'})
        print(f"⏳ {new_user.real_name} waiting in {mode} queue...")
    else:
        for member in room['members']:
            if member in waiting_pool:
                waiting_pool.remove(member)
            join_room(room['room_id'], sid=member.user_id)

        room['duration_seconds'] = int(data.get('duration', 45))
        active_rooms[room['room_id']] = room
        print(f"🎉 Live Room {room['room_id']} launched with {len(room['members'])} real users!")
        broadcast_room_state(room)


def broadcast_room_state(room):
    """Sends each member their secret alias + the anonymous roster of everyone in the room."""
    roster = [m.alias for m in room['members']]
    for member in room['members']:
        emit('match_found', {
            'room_id': room['room_id'],
            'my_alias': member.alias,
            'roster': roster,
            'mode': room['mode'],
            'common_interests': room['common_interests'],
            'duration_seconds': room['duration_seconds'],
            'max_capacity': 5 if room['mode'] == "group" else 2
        }, to=member.user_id)


# 2. REAL-TIME MESSAGE BETWEEN COMPUTERS
@socketio.on('send_message')
def handle_send_message(data):
    room_id = data.get('room_id')
    room = active_rooms.get(room_id)
    if not room:
        return

    sender_alias = "Anonymous Fox"
    for member in room['members']:
        if member.user_id == request.sid:
            sender_alias = member.alias
            break

    emit('new_message', {
        'sender': sender_alias,
        'text': data.get('text', '')
    }, to=room_id, include_self=False)


# 3. LIVE UNMASKING & MEETUP SYNC ACROSS ALL SCREENS
@socketio.on('trigger_reveal')
def handle_trigger_reveal(data):
    room_id = data.get('room_id')
    choice = data.get('choice', 'reveal')
    room = active_rooms.get(room_id)
    if not room:
        return

    all_profiles = [
        {
            'alias': m.alias,
            'real_name': m.real_name,
            'handle': m.bio
        }
        for m in room['members']
    ]

    emit('reveal_all', {
        'choice': choice,
        'profiles': all_profiles
    }, to=room_id)


# 4. CLEANUP ON DISCONNECT
@socketio.on('disconnect')
def handle_disconnect():
    global waiting_pool
    waiting_pool = [u for u in waiting_pool if u.user_id != request.sid]


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5000, allow_unsafe_werkzeug=True)