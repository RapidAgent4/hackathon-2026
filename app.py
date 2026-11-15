import uuid
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from Dictionaries.matcher import User, form_match_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

waiting_pool = []
active_rooms = {}


@app.route('/')
def home():
    return render_template('index.html')


def remove_user_from_all(sid):
    """Removes a user from the waiting pool and any active room they are in."""
    global waiting_pool
    waiting_pool = [u for u in waiting_pool if u.user_id != sid]

    # Iterate over a static list of items so we can safely delete empty rooms
    for room_id, room in list(active_rooms.items()):
        leaving_member = next((m for m in room['members'] if m.user_id == sid), None)
        if leaving_member:
            # 1. Remove from the server's room member list and SocketIO room
            room['members'].remove(leaving_member)
            leave_room(room_id, sid=sid)
            print(f"👋 {leaving_member.real_name} ({leaving_member.alias}) left room {room_id}")

            # 2. Notify remaining members in the chat
            emit('new_message', {
                'sender': 'System',
                'text': f"{leaving_member.alias} has left the room."
            }, to=room_id)

            # 3. Clean up the room if empty (or if a 1-on-1 loses a partner), else update roster
            if len(room['members']) == 0:
                del active_rooms[room_id]
                print(f"🧹 Room {room_id} is now empty and was closed.")
            elif room['mode'] == "1on1" and len(room['members']) < 2:
                # Optional: Keep the room open so they see the system message, or close it from active matching
                del active_rooms[room_id]
                print(f"🧹 1-on-1 Room {room_id} closed because a partner left.")
            else:
                # Update the roster UI for the remaining group members
                broadcast_room_state(room)


# 1. REAL HUMAN JOINS THE QUEUE
@socketio.on('join_queue')
def handle_join_queue(data):
    # Clean up any previous room or queue state in case the user hit Reset without refreshing
    remove_user_from_all(request.sid)

    mode = "1on1" if data.get('mode') == "one_on_one" else "group"
    new_user = User(
        user_id=request.sid,
        real_name=data.get('real_name', "Alex Rivera '27"),
        bio=data.get('handle', "@alex.marist"),
        interests=data.get('interests', ["Coffee ☕"]),
        mode=mode
    )

    # Check if an active Group room (less than 5 people) already shares an interest
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
        # Ensure room_id is always unique even if matcher.py returns a static room_id
        if not room.get('room_id') or room['room_id'] in active_rooms:
            room['room_id'] = f"room_{uuid.uuid4().hex[:8]}"

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


# 4. HANDLE RESET BUTTON (LEAVING THE ROOM WITHOUT CLOSING TAB)
@socketio.on('reset_chat')
@socketio.on('leave_room')
def handle_reset_chat(data=None):
    remove_user_from_all(request.sid)


# 5. CLEANUP ON DISCONNECT OR PAGE REFRESH
@socketio.on('disconnect')
def handle_disconnect():
    remove_user_from_all(request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5000, allow_unsafe_werkzeug=True)