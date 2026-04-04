import sys
import os
from chat import start_chat, start_server
from tos import TOS_TEXT, print_tos

# Add project subfolders to path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chat"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tos"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "exploits"))

def get_host_port():
    host = input("Host [127.0.0.1]: ").strip() or "127.0.0.1"
    port_str = input("Port [9000]: ").strip() or "9000"
    return host, int(port_str)


def main():
    # Show and require acceptance of TOS before anything else
    print_tos()
    while True:
        print("\n APToolkit Main Menu")
        print("1. exploits")
        print("2. chat")
        print("3. exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            exploits_menu()
        elif choice == "2":
            chat_menu()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


def chat_menu():
    while True:
        print("\n Chat Menu")
        print("1. Start Server")
        print("2. Connect as Client")
        print("3. Back to Main Menu")
        choice = input("Select an option: ").strip()
        if choice == "1":
            host, port = get_host_port()
            print(f"Starting server on {host}:{port}...")
            start_server(host, port)
        elif choice == "2":
            host, port = get_host_port()
            start_chat(host, port)
        elif choice == "3":
            break
        else:
            print("Invalid option. Try again.")


def exploits_menu():
    while True:
        print("\n Exploits Menu")
        print("1. DoS Attack")
        print("2. Keylogger")
        print("3. Port Scanner")
        print("4. Back to Main Menu")
        choice = input("Select an option: ").strip()
        if choice == "1":
            from exploits.dos import DoSAttack
            dos_attack = DoSAttack()
            dos_attack.start()
        elif choice == "2":
            from exploits.keylogger import start_keylogger
            start_keylogger()
        elif choice == "3":
            try:
                import portscanner
                portscanner.run_scanner()
            except ImportError:
                print("[!] Error: Portscanner.py not found in exploits folder.")
        elif choice == "4":
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
