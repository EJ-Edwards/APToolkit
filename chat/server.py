import socket
import threading
import hashlib

# Room structure: {room_name: {"pin_hash": str, "admin": socket, "members": {socket: username}}}
rooms = {}
# Clients in lobby (not in a room yet): {socket: username}
lobby = {}
lock = threading.Lock()


def hash_pin(pin):
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def broadcast_room(room_name, message, sender_socket=None):
    """Send a message to all members of a room except the sender."""
    with lock:
        if room_name not in rooms:
            return
        for member_socket in list(rooms[room_name]["members"]):
            if member_socket != sender_socket:
                try:
                    member_socket.sendall(message.encode("utf-8"))
                except OSError:
                    remove_client(member_socket)


def send(client_socket, message):
    try:
        client_socket.sendall(message.encode("utf-8"))
    except OSError:
        pass


def get_client_room(client_socket):
    """Find which room a client is in, or None."""
    with lock:
        for room_name, room in rooms.items():
            if client_socket in room["members"]:
                return room_name
    return None


def remove_client(client_socket):
    """Remove a client from their room or lobby."""
    username = None
    room_name = None

    with lock:
        # Check lobby
        if client_socket in lobby:
            username = lobby.pop(client_socket)

        # Check rooms
        for rname, room in list(rooms.items()):
            if client_socket in room["members"]:
                username = room["members"].pop(client_socket)
                room_name = rname
                was_admin = (room["admin"] == client_socket)

                # If admin left and room still has members, promote someone
                if was_admin and room["members"]:
                    new_admin_socket = next(iter(room["members"]))
                    room["admin"] = new_admin_socket
                    new_admin_name = room["members"][new_admin_socket]
                    threading.Thread(
                        target=broadcast_room,
                        args=(rname, f"[ROOM] {new_admin_name} is now the admin."),
                        daemon=True,
                    ).start()

                # Delete empty rooms
                if not room["members"]:
                    del rooms[rname]
                break

    try:
        client_socket.close()
    except OSError:
        pass

    if username:
        print(f"[SERVER] {username} disconnected.")
        if room_name:
            broadcast_room(room_name, f"[ROOM] {username} has left the room.")


def handle_lobby_command(client_socket, username, message):
    """Process commands while the client is in the lobby."""
    parts = message.split(maxsplit=2)
    cmd = parts[0].lower()

    if cmd == "/create":
        if len(parts) < 3:
            send(client_socket, "[SERVER] Usage: /create <room_name> <pin>")
            return
        room_name = parts[1]
        pin = parts[2]
        with lock:
            if room_name in rooms:
                send(client_socket, f"[SERVER] Room '{room_name}' already exists.")
                return
            lobby.pop(client_socket, None)
            rooms[room_name] = {
                "pin_hash": hash_pin(pin),
                "admin": client_socket,
                "members": {client_socket: username},
            }
        print(f"[SERVER] {username} created room '{room_name}'")
        send(client_socket, f"[ROOM] You created and joined '{room_name}' as admin.\n"
             f"[ROOM] Commands: /kick <user>, /list, /leave, /quit")

    elif cmd == "/join":
        if len(parts) < 3:
            send(client_socket, "[SERVER] Usage: /join <room_name> <pin>")
            return
        room_name = parts[1]
        pin = parts[2]
        with lock:
            if room_name not in rooms:
                send(client_socket, f"[SERVER] Room '{room_name}' not found.")
                return
            if rooms[room_name]["pin_hash"] != hash_pin(pin):
                send(client_socket, "[SERVER] Incorrect PIN.")
                return
            lobby.pop(client_socket, None)
            rooms[room_name]["members"][client_socket] = username
        print(f"[SERVER] {username} joined room '{room_name}'")
        send(client_socket, f"[ROOM] You joined '{room_name}'. Type /leave to go back to lobby.")
        broadcast_room(room_name, f"[ROOM] {username} has joined the room.", client_socket)

    elif cmd == "/rooms":
        with lock:
            if rooms:
                room_list = "\n".join(
                    f"  {name} ({len(r['members'])} online)"
                    for name, r in rooms.items()
                )
                send(client_socket, f"[SERVER] Active rooms:\n{room_list}")
            else:
                send(client_socket, "[SERVER] No active rooms. Create one with /create <name> <pin>")

    else:
        send(client_socket, "[SERVER] You're in the lobby. Commands: /create <name> <pin>, /join <name> <pin>, /rooms")


def handle_room_command(client_socket, username, room_name, message):
    """Process commands/messages while the client is in a room."""
    if message.startswith("/"):
        parts = message.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "/leave":
            with lock:
                if room_name in rooms:
                    rooms[room_name]["members"].pop(client_socket, None)
                    was_admin = rooms[room_name]["admin"] == client_socket
                    if was_admin and rooms[room_name]["members"]:
                        new_admin = next(iter(rooms[room_name]["members"]))
                        rooms[room_name]["admin"] = new_admin
                        new_name = rooms[room_name]["members"][new_admin]
                        broadcast_room(room_name, f"[ROOM] {new_name} is now the admin.")
                    if not rooms[room_name]["members"]:
                        del rooms[room_name]
                lobby[client_socket] = username
            broadcast_room(room_name, f"[ROOM] {username} has left the room.")
            send(client_socket, "[SERVER] You left the room. You're back in the lobby.\n"
                 "[SERVER] Commands: /create <name> <pin>, /join <name> <pin>, /rooms")

        elif cmd == "/list":
            with lock:
                if room_name in rooms:
                    admin_sock = rooms[room_name]["admin"]
                    admin_name = rooms[room_name]["members"].get(admin_sock, "?")
                    member_list = "\n".join(
                        f"  {'[admin] ' if m == admin_name else ''}{m}"
                        for m in rooms[room_name]["members"].values()
                    )
                    send(client_socket, f"[ROOM] Members in '{room_name}':\n{member_list}")

        elif cmd == "/kick":
            with lock:
                if room_name not in rooms:
                    return
                if rooms[room_name]["admin"] != client_socket:
                    send(client_socket, "[ROOM] Only the admin can kick users.")
                    return
            target_name = parts[1].strip() if len(parts) > 1 else ""
            if not target_name:
                send(client_socket, "[ROOM] Usage: /kick <username>")
                return
            with lock:
                target_socket = None
                if room_name in rooms:
                    for sock, uname in rooms[room_name]["members"].items():
                        if uname == target_name:
                            target_socket = sock
                            break
            if target_socket is None:
                send(client_socket, f"[ROOM] User '{target_name}' not found in this room.")
                return
            if target_socket == client_socket:
                send(client_socket, "[ROOM] You can't kick yourself.")
                return
            with lock:
                if room_name in rooms:
                    rooms[room_name]["members"].pop(target_socket, None)
                lobby[target_socket] = target_name
            send(target_socket, f"[ROOM] You were kicked from '{room_name}' by {username}.\n"
                 "[SERVER] You're back in the lobby.")
            broadcast_room(room_name, f"[ROOM] {target_name} was kicked by {username}.")
            send(client_socket, f"[ROOM] Kicked {target_name}.")

        else:
            send(client_socket, "[ROOM] Commands: /leave, /list, /kick <user>, /quit")
    else:
        formatted = f"{username}: {message}"
        print(f"  [{room_name}] {formatted}")
        broadcast_room(room_name, formatted, client_socket)


def handle_client(client_socket, address):
    """Handle communication with a single client."""
    try:
        client_socket.sendall("USERNAME_REQUEST".encode("utf-8"))
        username = client_socket.recv(1024).decode("utf-8").strip()
        if not username:
            username = f"User-{address[1]}"

        with lock:
            lobby[client_socket] = username

        print(f"[SERVER] {username} connected from {address}")
        send(client_socket,
             f"[SERVER] Welcome, {username}!\n"
             f"[SERVER] Commands: /create <room_name> <pin>, /join <room_name> <pin>, /rooms, /quit")

        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            message = data.decode("utf-8").strip()
            if message.lower() == "/quit":
                send(client_socket, "DISCONNECT")
                break

            room_name = get_client_room(client_socket)
            if room_name:
                handle_room_command(client_socket, username, room_name, message)
            else:
                handle_lobby_command(client_socket, username, message)

    except (ConnectionResetError, OSError):
        pass
    finally:
        remove_client(client_socket)


def start_server(host="127.0.0.1", port=9000):
    """Start the chat server on the given host and port."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(100)
    print(f"[SERVER] Listening on {host}:{port}")

    try:
        while True:
            client_socket, address = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, address), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        with lock:
            for rname in list(rooms):
                for sock in list(rooms[rname]["members"]):
                    try:
                        sock.close()
                    except OSError:
                        pass
            rooms.clear()
            for sock in list(lobby):
                try:
                    sock.close()
                except OSError:
                    pass
            lobby.clear()
        server.close()
