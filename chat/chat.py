import socket
import threading
import sys


def receive_messages(client_socket):
    """Listen for incoming messages from the server."""
    while True:
        try:
            data = client_socket.recv(4096).decode("utf-8")
            if not data or data == "DISCONNECT":
                print("\n[Disconnected from server]")
                break
            print(f"\r{data}\nYou: ", end="", flush=True)
        except (ConnectionResetError, OSError):
            print("\n[Connection lost]")
            break


def start_chat(host="127.0.0.1", port=9000):
    """Connect to the chat server and start chatting."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print("[ERROR] Could not connect to server. Is it running?")
        return

    # Wait for username request
    data = client_socket.recv(1024).decode("utf-8")
    if data == "USERNAME_REQUEST":
        username = input("Enter your username: ").strip()
        if not username:
            username = "Anonymous"
        client_socket.sendall(username.encode("utf-8"))

    # Start receiving messages in background
    receiver = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receiver.start()

    # Main input loop
    try:
        while True:
            message = input("You: ")
            if not message:
                continue
            if message.lower() == "/quit":
                client_socket.sendall("/quit".encode("utf-8"))
                break
            if message.lower() == "/help":
                print("[HELP] Lobby:  /create <name> <pin>, /join <name> <pin>, /rooms")
                print("[HELP] Room:   /leave, /list, /kick <user>")
                print("[HELP] Global: /quit, /help")
                continue
            client_socket.sendall(message.encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        client_socket.close()
        print("Goodbye!")
