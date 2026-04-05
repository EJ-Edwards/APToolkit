import sys
import os
import subprocess
import time
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

def c2_menu():
    """Logic to launch and manage the Go C2 Server"""
    while True:
        print("\n--- C2 (Command and Control) Manager ---")
        print("1. Launch Go C2 Server")
        print("2. Check Server Status (Localhost:8080)")
        print("3. Back to Main Menu")
        
        choice = input("Select an option: ").strip()

        if choice == "1":
            # Determine the binary name based on OS
            binary_name = "./c2server" if os.name != 'nt' else "c2server.exe"
            
            if not os.path.exists(binary_name):
                print(f"[!] Error: {binary_name} not found.")
                print("[*] Please run 'go build -o c2server main.go' first.")
                continue

            try:
                print(f"[*] Starting {binary_name}...")
                # Launching as a subprocess
                process = subprocess.Popen(
                    [binary_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(f"[+] C2 Server launched successfully (PID: {process.pid})")
                print("[*] Server is running on http://localhost:8080")
                time.sleep(1) # Brief pause to let it initialize
            except Exception as e:
                print(f"[!] Failed to launch C2 server: {e}")

        elif choice == "2":
            print("[*] Checking if server is responding...")
            # Note: You could use the 'requests' library here to ping :8080
            print("[!] Feature pending: Implement health check via requests.get()")
            
        elif choice == "3":
            break
        else:
            print("Invalid option.")

def main():
    # Show and require acceptance of TOS before anything else
    print_tos()
    while True:
        print("\n========================")
        print("   APToolkit Main Menu")
        print("========================")
        print("1. Exploits")
        print("2. C2 (Command and Control)")
        print("3. Chat")
        print("4. Exit")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            exploits_menu()
        elif choice == "2":
            c2_menu() # Now calls the function defined above
        elif choice == "3":
            chat_menu()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

def chat_menu():
    while True:
        print("\n--- Chat Menu ---")
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
        print("\n--- Exploits Menu ---")
        print("1. DoS Attack")
        print("2. Keylogger")
        print("3. Port Scanner")
        print("4. RAT")
        print("5. Back to Main Menu")
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
                print("[!] Error: portscanner.py not found in exploits folder.")
        elif choice == "4":
            try:
                import rat
                rat.start_rat()
            except ImportError:
                print("[!] Error: rat.py not found in exploits folder.")
        elif choice == "5":
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()