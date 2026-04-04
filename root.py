from chat import start_chat, start_server
from tos import TOS_TEXT, print_tos


def main():
    # Show and require acceptance of TOS before anything else
    if not print_tos():
        return
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


def exploits_menu():
    while True:
        print("\n Exploits Menu")
        print("1. DoS Attack")
        print("2. Keylogger")
        print("3. Back to Main Menu")



if __name__ == "__main__":
    main()
