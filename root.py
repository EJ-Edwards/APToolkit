import sys
import os

# Add project root to path so submodule imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chat"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tos"))

from tos import print_tos
import server
import chat


def main_menu():
    print("\n===== Chat Application =====")
    print("1. Start chat server")
    print("2. Join chatroom")
    print("3. View Terms of Service")
    print("4. Exploits")
    print("5. Start C2 Server")
    print("6. Exit")
    return input("Select an option: ").strip()


def get_host_port():
    host = input("Host [127.0.0.1]: ").strip() or "127.0.0.1"
    port_str = input("Port [9000]: ").strip() or "9000"
    return host, int(port_str)


def main():
    print_tos()

    while True:
        choice = main_menu()

        if choice == "1":
            host, port = get_host_port()
            print(f"Starting server on {host}:{port}...")
            server.start_server(host, port)

        elif choice == "2":
            host, port = get_host_port()
            chat.start_chat(host, port)

        elif choice == "3":
            from tos import TOS_TEXT
            print(TOS_TEXT)

        elif choice == "4":
            while True:
                exploit_choice = get_exploits_menu()
                if exploit_choice == "1":
                    print("[EXPLOIT] Keylogger selected - launching keylogger...")
                elif exploit_choice == "2":
                    break
                else:
                    print("Invalid option. Try again.")

        elif choice == "5":
            print("[C2] Starting C2 Server (not implemented).")

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Try again.")

def get_exploits_menu():
    print("\n===== Exploits =====")
    print("1. Keylogger")
    print("2. Back to Main Menu")
    return input("Select an option: ").strip()

if __name__ == "__main__":
    main()
