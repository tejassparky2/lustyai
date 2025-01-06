import requests
from faker import Faker
from colorama import Fore, Style, init
import random
import time
import itertools
import concurrent.futures
import threading
import queue
import sys

# Initialize colorama
init(autoreset=True)

# Initialize Faker
faker = Faker()

# Load proxies from proxy.txt
proxy_file = "proxy.txt"
try:
    with open(proxy_file, "r") as f:
        proxy_list = [line.strip() for line in f if line.strip()]
    if not proxy_list:
        print(Fore.RED + "[!] Proxy list is empty in proxy.txt" + Style.RESET_ALL)
        sys.exit()
except FileNotFoundError:
    print(Fore.RED + f"[!] Proxy file '{proxy_file}' not found." + Style.RESET_ALL)
    sys.exit()

# Load Solana wallet addresses from sol_wallet.txt
sol_wallet_file = "sol_wallet.txt"
try:
    with open(sol_wallet_file, "r") as f:
        sol_wallets = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    sol_wallets = []

# Check if there are Solana addresses loaded
if not sol_wallets:
    print(Fore.YELLOW + "[!] No Solana addresses found in sol_wallet.txt. You can choose to generate fake addresses." + Style.RESET_ALL)

# Queue for Solana addresses
sol_queue = queue.Queue()

# Lock for printing to avoid jumbled prints in multi-threading
print_lock = threading.Lock()

def generate_fake_solana_address():
    # Solana addresses are base58 and typically 44 characters
    characters = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    return ''.join(random.choice(characters) for _ in range(44))

def generate_email():
    return f"{faker.first_name().lower()}{faker.last_name().lower()}{random.randint(10000, 99999)}@gmail.com"

def generate_username():
    return f"{faker.first_name().lower()}{faker.last_name().lower()}{random.randint(10000, 99999)}"

def register_account(session):
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyBE4cLaS8quuc59LYuS2aW898K1dB-b82w"
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
    }
    email = generate_email()
    password = "AdeArman1412"

    payload = {
        "returnSecureToken": True,
        "email": email,
        "password": password,
        "clientType": "CLIENT_TYPE_WEB",
    }

    with print_lock:
        print(Fore.CYAN + f"[*] Registering account: {email}" + Style.RESET_ALL)

    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            with print_lock:
                print(Fore.GREEN + "[+] Account registered successfully" + Style.RESET_ALL)
            return data
        else:
            with print_lock:
                print(Fore.RED + f"[!] Registration failed: {response.text}" + Style.RESET_ALL)
            return None
    except requests.RequestException as e:
        with print_lock:
            print(Fore.RED + f"[!] Registration request error: {e}" + Style.RESET_ALL)
        return None

def set_username(session, token):
    url = "https://europe-west1-aipump-420d2.cloudfunctions.net/users/set-username"
    headers = {
        "accept": "*/*",
        "authorization": token,
        "content-type": "application/json",
    }
    while True:
        username = generate_username()
        payload = {"username": username}

        with print_lock:
            print(Fore.CYAN + f"[*] Setting username: {username}" + Style.RESET_ALL)

        try:
            response = session.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                with print_lock:
                    print(Fore.GREEN + f"[+] Username set: {username}" + Style.RESET_ALL)
                return
            elif response.status_code == 409:
                with print_lock:
                    print(Fore.YELLOW + "[!] Username conflict, generating a new one..." + Style.RESET_ALL)
            else:
                with print_lock:
                    print(Fore.RED + f"[!] Error setting username: {response.text}" + Style.RESET_ALL)
                break
        except requests.RequestException as e:
            with print_lock:
                print(Fore.RED + f"[!] Username request error: {e}" + Style.RESET_ALL)
            break

def set_referred_by(session, token, ref_code):
    url = "https://europe-west1-aipump-420d2.cloudfunctions.net/users/set-referred-by"
    headers = {
        "accept": "*/*",
        "authorization": token,
        "content-type": "application/json",
    }
    payload = {"referredBy": ref_code}

    with print_lock:
        print(Fore.CYAN + f"[*] Setting referral: {ref_code}" + Style.RESET_ALL)

    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            with print_lock:
                print(Fore.GREEN + "[+] Referral set successfully" + Style.RESET_ALL)
        else:
            with print_lock:
                print(Fore.RED + f"[!] Error setting referral: {response.text}" + Style.RESET_ALL)
    except requests.RequestException as e:
        with print_lock:
            print(Fore.RED + f"[!] Referral request error: {e}" + Style.RESET_ALL)

def add_wallet(session, token, wallet):
    url = "https://europe-west1-aipump-420d2.cloudfunctions.net/users/add-wallet"
    headers = {
        "accept": "*/*",
        "authorization": token,
        "content-type": "application/json",
    }
    payload = {"wallet": wallet}

    with print_lock:
        print(Fore.CYAN + f"[*] Adding wallet: {wallet}" + Style.RESET_ALL)

    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            with print_lock:
                print(Fore.GREEN + "[+] Wallet added successfully" + Style.RESET_ALL)
        else:
            with print_lock:
                print(Fore.RED + f"[!] Error adding wallet: {response.text}" + Style.RESET_ALL)
    except requests.RequestException as e:
        with print_lock:
            print(Fore.RED + f"[!] Add wallet request error: {e}" + Style.RESET_ALL)

def worker(proxy):
    session = requests.Session()
    session.proxies = {
        "http": proxy,
        "https": proxy,
    }
    session.headers.update({
        "User-Agent": faker.user_agent(),
    })
    while True:
        try:
            sol_wallet = sol_queue.get(timeout=5)
        except queue.Empty:
            continue  # Retry if queue is empty

        try:
            with print_lock:
                print(Fore.BLUE + f"[*] Using proxy: {proxy}" + Style.RESET_ALL)

            account_data = register_account(session)
            if not account_data:
                sol_queue.task_done()
                continue

            token = account_data.get("idToken")
            if not token:
                with print_lock:
                    print(Fore.RED + "[!] No token received, skipping..." + Style.RESET_ALL)
                sol_queue.task_done()
                continue

            set_username(session, token)
            set_referred_by(session, token, "REFFMU")
            add_wallet(session, token, sol_wallet)

            sol_queue.task_done()
            time.sleep(2)
        except Exception as e:
            with print_lock:
                print(Fore.RED + f"[!] Worker error: {e}" + Style.RESET_ALL)
            sol_queue.task_done()

def main():
    print("Choose an option:")
    print("1. Load Solana addresses from sol_wallet.txt")
    print("2. Generate fake Solana addresses continuously")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        if not sol_wallets:
            print(Fore.RED + "[!] No Solana addresses to load. Exiting." + Style.RESET_ALL)
            sys.exit()
        for wallet in sol_wallets:
            sol_queue.put(wallet)
    elif choice == "2":
        def generate_addresses():
            while True:
                fake_wallet = generate_fake_solana_address()
                sol_queue.put(fake_wallet)
        threading.Thread(target=generate_addresses, daemon=True).start()
    else:
        print(Fore.RED + "[!] Invalid choice. Exiting." + Style.RESET_ALL)
        sys.exit()

    # Start ThreadPoolExecutor with 10 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        # Cycle through proxies
        proxy_cycle = itertools.cycle(proxy_list)
        # Submit worker tasks
        for _ in range(30):
            proxy = next(proxy_cycle)
            executor.submit(worker, proxy)

        try:
            # Keep the main thread alive while workers are running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[!] Shutdown requested by user. Exiting..." + Style.RESET_ALL)
            executor.shutdown(wait=False)
            sys.exit()

if __name__ == "__main__":
    main()
