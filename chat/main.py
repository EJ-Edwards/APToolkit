import sys

try:
    from .chat import start_chat
    from .server import start_server
except ImportError:
    from chat import start_chat
    from server import start_server


def print_usage():
    print("Usage:")
    print("  python main.py server [host] [port]   - Start the chat server")
    print("  python main.py client [host] [port]   - Connect as a client")
    print()
    print("Enter a custom host and port")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()
    host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 9000

    if mode == "server":
        start_server(host, port)
    elif mode == "client":
        start_chat(host, port)
    else:
        print(f"Unknown mode: {mode}")
        print_usage()
        sys.exit(1)