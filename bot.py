import os
import sys
import types
import socket
import webbrowser

# ================= PYTHON 3.13+ COMPATIBILITY FIX =================
if 'imghdr' not in sys.modules:
    imghdr_mock = types.ModuleType('imghdr')
    imghdr_mock.what = lambda file, h=None: 'jpeg'
    sys.modules['imghdr'] = imghdr_mock

# ================= AUTO-INSTALLER FOR REQUIRED LIBRARIES =================
try:
    import telethon
    import python_socks
    if telethon.__version__ < '1.30.0':
        raise ImportError("Telethon too old")
except ImportError:
    print("\n[!] Installing required libraries (Telethon, Python-Socks)...")
    os.system(f"{sys.executable} -m pip install --upgrade telethon python-socks")
    print("\n[✔] Setup complete! Restarting script...\n")
    os.execv(sys.executable, ['python'] + sys.argv)

import glob
import random
import asyncio
import re
import shutil
import logging
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

from telethon import TelegramClient, errors, functions
from telethon.network import ConnectionTcpIntermediate, ConnectionTcpAbridged

# Disable Telethon background logging
logging.getLogger('telethon').setLevel(logging.CRITICAL)
init(autoreset=True)

# ================= GITHUB PROXY URL =================
GITHUB_PROXY_URL = "https://raw.githubusercontent.com/wptg88/wp_tg/main/proxies.txt"

# Default API Key
DEFAULT_API_ID = 25762761
DEFAULT_API_HASH = "f6712ac15fa56c713451eede724261eb"

# ================= AUTO NAMES LIST =================
AUTO_NAMES_LIST = [
    "RK", "ER", "RJ", "JEB", "Alex", "Sam", "Max", "Leo", "Ray", "Tom", "Bob", "Tim", "Jay", "Roy", 
    "Jon", "Dan", "Eli", "Ian", "Mac", "Abe", "Ben", "Cal", "Hal", "Sal", "Vic", "Zak", "Kai", "Jax", 
    "Fox", "Rex", "Ash", "Cid", "Dax", "Gus", "Kip", "Lex", "Ned", "Paz", "Taj", "Van", "Wes", "Zed",
    "John", "David", "Michael", "James", "Robert", "William", "Mary", "Patricia", "Jennifer", "Linda", 
    "Elizabeth", "Richard", "Joseph", "Charles", "Thomas", "Christopher", "Daniel", "Matthew", "Anthony", 
    "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Edward", 
    "Muhammad", "Ahmed", "Ali", "Omar", "Abdullah", "Tariq", "Khalid", "Hassan", "Hussein", "Ibrahim", 
    "Youssef", "Bilal", "Zaid", "Mahmoud", "Mustafa", "Hamza", "Karim", "Sami", "Nabil", "Majed", "Ramy", 
    "Adam", "Hawwa", "Maryam", "Asiya", "Khadija", "Aisha", "Fatima", "Zainab", "Ruqayyah", "Umm Kulthum",
    "Zaynab", "Zayn", "Zayd", "Qais", "Saad", "Fahd", "Badr", "Jamal", "Kamal", "Tariq", "Raed", "Anwar"
]

# ================= PREMIUM DESKTOP MODELS (ANTI-BAN) =================
DESKTOP_DEVICES = [
    {"device_model": "Windows 10 x64", "system_version": "10.0.19045", "app_version": "4.8.4 x64"},
    {"device_model": "Windows 11 x64", "system_version": "10.0.22621", "app_version": "4.11.2 x64"},
    {"device_model": "Ubuntu 22.04 LTS", "system_version": "Linux 5.15", "app_version": "4.9.1 x64"},
    {"device_model": "MacBook Pro M1", "system_version": "macOS 13.5", "app_version": "4.10.0 arm64"},
    {"device_model": "Windows 8.1 x64", "system_version": "6.3.9600", "app_version": "4.7.1 x64"},
    {"device_model": "Linux Mint 21", "system_version": "Linux 5.15", "app_version": "4.9.2 x64"},
    {"device_model": "iMac 27-inch", "system_version": "macOS 12.6", "app_version": "4.6.3 x64"},
    {"device_model": "Windows 10 x64", "system_version": "10.0.18363", "app_version": "4.5.3 x64"},
    {"device_model": "MacBook Air M2", "system_version": "macOS 14.1", "app_version": "4.13.0 arm64"},
    {"device_model": "Fedora 38", "system_version": "Linux 6.4", "app_version": "4.11.0 x64"},
    {"device_model": "Windows 11 x64", "system_version": "10.0.22000", "app_version": "4.10.5 x64"}
]

# Geo-location cache
GEO_CACHE = {}

# ================= Asyncio Event Loop Safe State =================
global_state = {'print_lock': None, 'semaphore': None, 'loop': None}

def get_print_lock():
    try: loop = asyncio.get_running_loop()
    except RuntimeError: return None
    if global_state['loop'] != loop or global_state['print_lock'] is None:
        global_state['print_lock'] = asyncio.Lock()
        global_state['loop'] = loop
    return global_state['print_lock']

def get_connect_semaphore(limit=40): 
    try: loop = asyncio.get_running_loop()
    except RuntimeError: return None
    if global_state['loop'] != loop or global_state['semaphore'] is None:
        global_state['semaphore'] = asyncio.Semaphore(limit)
        global_state['loop'] = loop
    return global_state['semaphore']

# ================= ANSI COLOR CODES =================
CYAN = Fore.CYAN + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
MAGENTA = Fore.MAGENTA + Style.BRIGHT
WHITE = Fore.WHITE + Style.BRIGHT
BLUE = Fore.BLUE + Style.BRIGHT
RESET = Style.RESET_ALL

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

# ================= STARTUP PROMPT & AUTO UPDATER =================
def fetch_online_proxies():
    if not GITHUB_PROXY_URL: return
    print(f"\n{YELLOW} [*] Downloading latest proxies from GitHub...{RESET}")
    try:
        req = urllib.request.Request(GITHUB_PROXY_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            proxy_data = resp.read().decode('utf-8')
            if proxy_data.strip():
                with open("proxies.txt", "w", encoding="utf-8") as f: f.write(proxy_data)
                print(f"{GREEN} [✔] Proxies successfully updated!{RESET}")
    except Exception:
        print(f"{RED} [✖] Failed to fetch proxies from GitHub (Using local file).{RESET}")

def startup_channel_prompt():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             WELCOME TO CHECKER V6                " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")
    print(f"\n{WHITE} 🚀 Join our Telegram Channel for updates!{RESET}")
    print(f"{GREEN} 👉 https://t.me/WORLD_UPDATE_TOP1 👈{RESET}\n")
    print(f"{YELLOW} [*] Opening channel automatically...{RESET}")
    
    url = "https://t.me/WORLD_UPDATE_TOP1"
    try:
        if "com.termux" in os.environ.get("PREFIX", "") or os.path.exists('/data/data/com.termux/files/usr/bin/termux-open-url'):
            os.system(f"termux-open-url {url} > /dev/null 2>&1")
        elif sys.platform == 'win32': os.system(f"start {url}")
        elif sys.platform == 'darwin': os.system(f"open {url}")
        else: webbrowser.open(url)
    except Exception: pass
        
    fetch_online_proxies()
    input(f"\n{YELLOW} [?] Press ENTER after joining to continue... {RESET}")

# ================= ACCURATE GEO-LOCATION RESOLVER =================
def resolve_ip_geo(ip):
    if not ip or ip.lower() in ['unknown', 'localhost', '127.0.0.1']: return "Unknown"
    if ip in GEO_CACHE: return GEO_CACHE[ip]
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=status,country,city", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('status') == 'success':
                loc = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
                if loc:
                    GEO_CACHE[ip] = loc
                    return loc
    except Exception: pass
    return "Unknown"

# ================= NETWORK & VPN DETECTOR =================
def get_current_network_info():
    try:
        req = urllib.request.Request("http://ip-api.com/json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            isp = data.get('isp', '')
            isp_short = isp[:15] + '..' if len(isp) > 15 else isp
            loc = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
            return {'ip': data.get('query', 'Unknown'), 'location': loc if loc else "Unknown", 'isp': isp_short, 'status': True}
    except Exception:
        return {'ip': 'Local IP', 'location': 'Local Network', 'isp': 'Direct', 'status': False}

# ================= CLEAN UI MENU =================
def show_banner():
    clear_screen()
    net = get_current_network_info()
    vpn_status = f"{GREEN}ONLINE 🌐{RESET}" if net['status'] else f"{YELLOW}LOCAL 📶{RESET}"
    
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             C H E C K E R   V 6                  " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")
    print(f"{WHITE} » IP  : {YELLOW}{net['ip']}{RESET}")
    print(f"{WHITE} » Loc : {GREEN}{net['location']}{RESET}")
    print(f"{WHITE} » Net : {MAGENTA}{net['isp']}{RESET} [{vpn_status}]")
    print(f"{WHITE} » Dev : {CYAN}Telegram 👉 @WORLD_UPDATE_TOP1{RESET}")
    print(CYAN + "────────────────────────────────────────────────────")
    print(f"{CYAN} [1] {GREEN}⚡ {YELLOW}Create Session & JSON{RESET}")
    print(f"{CYAN} [2] {GREEN}🌐 {GREEN}Upload / Check Proxies{RESET}")
    print(f"{CYAN} [3] {GREEN}🔑 {MAGENTA}Upload / Check API Keys{RESET}")
    print(f"{CYAN} [4] {GREEN}👥 {BLUE}Join Public Channel / Group{RESET}")
    print(f"{CYAN} [5] {GREEN}🔰 {GREEN}Check Folder Sessions (Auto Name){RESET}")
    print(f"{CYAN} [6] {GREEN}💔 {YELLOW}Breakup Session (Fast Mode){RESET}")
    print(f"{CYAN} [7] {GREEN}🔐 {MAGENTA}2FA Manager (Change/Disable/Reset){RESET}")
    print(f"{CYAN} [8] {GREEN}🔢 {RED}Read OTP Session{RESET}")
    print(f"{CYAN} [9] {GREEN}🧹 {RED}Clear All Chat History{RESET}")
    print(f"{CYAN}[10] {GREEN}📁 {YELLOW}Session to JSON Converter{RESET}")
    print(f"{CYAN}[11] {GREEN}🛡️ {MAGENTA}Spam Check Menu{RESET}")
    print(f"{CYAN}[12] {GREEN}🔥 {RED}Kill Session (Self Logout){RESET}")
    print(f"{CYAN} [0] {GREEN}🚨 {RED}Exit Tools{RESET}")
    print(CYAN + "════════════════════════════════════════════════════" + RESET)

# ================= UNIVERSAL PROXY PARSER =================
def universal_proxy_parser(raw_text):
    proxies = []
    lines = raw_text.replace(',', '\n').split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        chunks = line.split()
        if len(chunks) == 4 and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', chunks[0]) and chunks[1].isdigit():
            proxies.append(f"{chunks[0]}:{chunks[1]}:{chunks[2]}:{chunks[3]}"); continue
        elif len(chunks) == 2 and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', chunks[0]) and chunks[1].isdigit():
            proxies.append(f"{chunks[0]}:{chunks[1]}"); continue
        for chunk in chunks:
            chunk = chunk.replace('http://', '').replace('https://', '').replace('socks5://', '').replace('socks4://', '')
            ip_match = re.search(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', chunk)
            if not ip_match: continue
            ip = ip_match.group()
            rest = chunk.replace(ip, '[IP]')
            m1 = re.match(r'^\[IP\]:(\d+):([^:@\s]+):([^:@\s]+)$', rest)
            if m1: proxies.append(f"{ip}:{m1.group(1)}:{m1.group(2)}:{m1.group(3)}"); continue
            m2 = re.match(r'^([^:@\s]+):([^:@\s]+)@\[IP\]:(\d+)$', rest)
            if m2: proxies.append(f"{ip}:{m2.group(3)}:{m2.group(1)}:{m2.group(2)}"); continue
            m3 = re.match(r'^\[IP\]:(\d+)@([^:@\s]+):([^:@\s]+)$', rest)
            if m3: proxies.append(f"{ip}:{m3.group(1)}:{m3.group(2)}:{m3.group(3)}"); continue
            m4 = re.match(r'^([^:@\s]+):([^:@\s]+):\[IP\]:(\d+)$', rest)
            if m4: proxies.append(f"{ip}:{m4.group(3)}:{m4.group(1)}:{m4.group(2)}"); continue
            m5 = re.match(r'^\[IP\]:(\d+)$', rest)
            if m5: proxies.append(f"{ip}:{m5.group(1)}"); continue
    return list(dict.fromkeys(proxies))

def load_proxies(file_path="proxies.txt"):
    if not os.path.exists(file_path): return []
    proxy_list = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            geo_tag = ""
            if "#" in line: line, geo_tag = line.split("#", 1)
            proto = "socks5"
            if "://" in line: proto, line = line.split("://", 1)
            
            if "@" in line:
                auth, ip_port = line.split("@", 1)
                user, pwd = auth.split(":", 1) if ":" in auth else (auth, "")
                if ":" in ip_port: 
                    ip, port = ip_port.split(":", 1)
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port), 'user': user, 'pwd': pwd, 'geo': loc})
            else:
                parts = line.split(":")
                if len(parts) >= 4:
                    ip, port, user, pwd = parts[0], int(parts[1]), parts[2], parts[3]
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port), 'user': user, 'pwd': pwd, 'geo': loc})
                elif len(parts) == 2:
                    ip, port = parts[0], int(parts[1])
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port), 'user': None, 'pwd': None, 'geo': loc})
    return proxy_list

def load_api_keys(file_path="api_keys.txt"):
    if not os.path.exists(file_path): return [(DEFAULT_API_ID, DEFAULT_API_HASH)]
    api_list = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            match = re.search(r'(\d{5,10})\s*[:\s,\t]+\s*([a-fA-F0-9]{32})', line)
            if match:
                pair = (int(match.group(1)), match.group(2))
                if pair not in api_list: api_list.append(pair)
    return api_list if api_list else [(DEFAULT_API_ID, DEFAULT_API_HASH)]

def move_to_corrupt(session_file_path):
    corrupt_dir = "Corrupt_Sessions"
    os.makedirs(corrupt_dir, exist_ok=True)
    try:
        dest_path = os.path.join(corrupt_dir, os.path.basename(session_file_path))
        if os.path.exists(dest_path): os.remove(dest_path)
        shutil.move(session_file_path, dest_path)
        journal = session_file_path + "-journal"
        if os.path.exists(journal):
            j_dest = os.path.join(corrupt_dir, os.path.basename(journal))
            if os.path.exists(j_dest): os.remove(j_dest)
            shutil.move(journal, j_dest)
    except Exception: pass

def update_json_2fa(session_file, new_2fa):
    json_file = session_file.replace('.session', '.json')
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f: data = json.load(f)
            data['twoFA'] = new_2fa
            with open(json_file, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception: pass

def create_telethon_client(session_base, api_pair, timeout=12, device_config=None, proxy_info=None):
    proxy_dict = None
    if proxy_info and 'python_socks' in sys.modules:
        p_type = python_socks.ProxyType.HTTP if proxy_info.get('proto', 'socks5').lower() in ['http', 'https'] else python_socks.ProxyType.SOCKS5
        proxy_dict = {
            'proxy_type': p_type,
            'addr': proxy_info['ip'],
            'port': int(proxy_info['port']),
            'username': proxy_info.get('user'),
            'password': proxy_info.get('pwd'),
            'rdns': True
        }

    dm = device_config['device_model'] if device_config else "HP Spectre x360 14"
    sv = device_config['system_version'] if device_config else "Windows 10 x64"
    av = device_config['app_version'] if device_config else "6.8.2 x64"

    return TelegramClient(
        session_base, api_pair[0], api_pair[1], 
        device_model=dm, system_version=sv, app_version=av,
        lang_code="en", system_lang_code="en-US",
        proxy=proxy_dict,
        connection=ConnectionTcpAbridged if proxy_dict else ConnectionTcpIntermediate, 
        timeout=timeout, auto_reconnect=False, connection_retries=1, retry_delay=1, flood_sleep_threshold=20
    )

def format_telegram_date(dt):
    if not dt: return "Unknown"
    tz_bd = timezone(timedelta(hours=6))
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz_bd).strftime("%Y-%m-%d %H:%M:%S UTC+06:00")

def create_expert_json(session_name, phone, user_id, first_name, last_name, username, api_id, api_hash, two_fa, device_config=None, proxy_info=None):
    current_time = datetime.now(timezone(timedelta(hours=7))).isoformat()
    dev_model = device_config['device_model'] if device_config else "Windows PC"
    app_ver = device_config['app_version'] if device_config else "6.8.2 x64"
    sys_ver = device_config['system_version'] if device_config else "Windows 10 x64"

    return {
        "twoFA": two_fa if two_fa and str(two_fa).upper() != 'N' else "",
        "spambot": "free", "session_file": session_name, "phone": phone, "user_id": user_id,
        "app_id": api_id, "app_hash": api_hash, "sdk": sys_ver, "app_version": app_ver,
        "device": dev_model, "last_check_time": current_time,
        "first_name": first_name or "", "last_name": last_name or "", "username": username or "",
        "proxy": proxy_info
    }

async def ordered_output_printer(results_buffer, total_files):
    next_idx = 1
    while next_idx <= total_files:
        while next_idx not in results_buffer: await asyncio.sleep(0.01)
        output_buffer, is_corrupt, session_file = results_buffer.pop(next_idx)
        for line in output_buffer: print(line)
        if is_corrupt and session_file:
            try: move_to_corrupt(session_file)
            except Exception: pass
        await asyncio.sleep(0.05) 
        next_idx += 1

# ================= 2: PROXY TESTER =================
def test_single_proxy_thread(p_str, idx, is_http=False):
    parts = p_str.split(':')
    ip, port = parts[0], int(parts[1])
    proto_prefix = "http" if is_http else "socks5"
    try:
        with socket.create_connection((ip, port), timeout=4.0):
            loc = resolve_ip_geo(ip)
            return (True, f"{proto_prefix}://{p_str}", f"{GREEN}[ALIVE #{idx}] {ip}:{port} -> ({loc}){RESET}")
    except Exception: return (False, None, f"{RED}[DEAD #{idx}] {ip}:{port} - Timeout{RESET}")

def upload_and_check_proxies():
    print(f"\n{CYAN}--- PROXY AUTO-UPLOADER ---{RESET}")
    print(f"{YELLOW}Paste your proxies below. Type 'DONE' when finished:{RESET}\n")
    input_lines = []
    while True:
        try:
            line = input().strip()
            if line.upper() in ['DONE', 'OK', 'EXIT']: break
            if line: input_lines.append(line)
        except (EOFError, KeyboardInterrupt): break

    raw_data = "\n".join(input_lines)
    found_proxies = universal_proxy_parser(raw_data)
    if not found_proxies:
        print(f"{RED}[✖] No valid proxies detected!{RESET}")
        return

    print(f"\n{GREEN}✔ Extracted {len(found_proxies)} Proxies!{RESET}")
    proto_opt = input(f"{YELLOW}Protocol: [1] HTTP/HTTPS  [2] SOCKS5: {RESET}").strip()
    is_http_proxy = True if proto_opt == "1" else False
    proto_name = "http" if is_http_proxy else "socks5"

    opt = input(f"{YELLOW}Options: [1] Save Directly  [2] Test Ping First: {RESET}").strip()
    if opt == "1":
        with open("proxies.txt", "w", encoding="utf-8") as f:
            for vp in found_proxies: f.write(f"{proto_name}://{vp}\n")
        print(f"\n{GREEN}✔ SUCCESS! {len(found_proxies)} Proxies saved to 'proxies.txt'.{RESET}")
    elif opt == "2":
        print(f"\n{YELLOW}[*] Testing Fast TCP Connections...{RESET}")
        valid_proxies = []
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(test_single_proxy_thread, p, i, is_http_proxy) for i, p in enumerate(found_proxies, 1)]
            for f in futures:
                is_alive, proxy_formatted, msg = f.result()
                print(msg)
                if is_alive: valid_proxies.append(proxy_formatted)
        if valid_proxies:
            with open("proxies.txt", "w", encoding="utf-8") as f:
                for vp in valid_proxies: f.write(vp + "\n")
            print(f"{GREEN}✔ SUCCESS! Saved {len(valid_proxies)} working proxies.{RESET}")
        else: print(f"{RED}[✖] No working proxies found.{RESET}")

# ================= 3: API KEYS UPLOADER =================
async def upload_and_check_api_keys():
    print(f"\n{CYAN}--- API KEYS UPLOADER ---{RESET}")
    print(f"{YELLOW}Paste your API Keys (Format: APP_ID API_HASH). Type 'DONE' when finished:{RESET}\n")
    input_lines = []
    while True:
        try:
            line = input().strip()
            if line.upper() in ['DONE', 'OK', 'EXIT']: break
            if line: input_lines.append(line)
        except (EOFError, KeyboardInterrupt): break
    
    if not input_lines: return
    
    with open("api_keys.txt", "w", encoding="utf-8") as f:
        for line in input_lines: f.write(line + "\n")
    print(f"{GREEN}[✔] API Keys saved successfully!{RESET}")

# ================= 1: CREATE SESSION AND JSON =================
async def create_session():
    api_keys = load_api_keys("api_keys.txt")
    net_info = get_current_network_info()
    print(f"\n{CYAN}--- NEW SESSION CREATOR ---{RESET}")
    folder = input(f"{YELLOW}Enter Folder Name to save files: {RESET}").strip()
    folder = folder if folder else "sessions"
    os.makedirs(folder, exist_ok=True)
    two_fa_input = input(f"{YELLOW}Enter 2FA Password to save in JSON (Type 'N' if none): {RESET}").strip()
    two_fa_pass = "" if two_fa_input.upper() == 'N' else two_fa_input

    session_count = 1
    while True:
        api_pair = random.choice(api_keys)
        chosen_device = random.choice(DESKTOP_DEVICES)
        print(f"\n{CYAN}--- CREATING SESSION #{session_count} ---{RESET} {MAGENTA}[API: {api_pair[0]}]{RESET}")
        phone = input(f"{YELLOW}Enter Phone Number (or 'E' to Exit): {RESET}").strip()
        if phone.upper() in ['E', 'EXIT']: break
        if not phone: continue

        session_name = phone.replace("+", "")
        session_path = os.path.join(folder, session_name)
        client = create_telethon_client(session_path, api_pair, timeout=10, device_config=chosen_device)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                try:
                    await client.send_code_request(phone)
                    code = input(f"{GREEN}Enter Telegram OTP code: {RESET}").strip()
                    try: await client.sign_in(phone, code)
                    except errors.SessionPasswordNeededError:
                        pwd = input(f"{YELLOW}Enter 2FA Login Password: {RESET}").strip()
                        await client.sign_in(password=pwd)
                        two_fa_pass = pwd 
                    print(f"{GREEN}[✔] Session created successfully: {session_name}.session{RESET}")
                    me = await client.get_me()
                    json_data = create_expert_json(session_name, session_name, me.id, me.first_name, me.last_name, me.username, api_pair[0], api_pair[1], two_fa_pass, chosen_device)
                    with open(os.path.join(folder, f"{session_name}.json"), "w", encoding="utf-8") as f: json.dump(json_data, f, indent=4, ensure_ascii=False)
                    session_count += 1
                except Exception as e: print(f"{RED}[✖] Error: {e}{RESET}")
            else: print(f"{GREEN}[✔] Account is already Authorized!{RESET}")
        finally:
            try: await client.disconnect()
            except Exception: pass

# ================= 6: BREAKUP SESSION =================
async def clone_single_session_task(session_file, idx, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file
    target_session_base = os.path.join(target_folder, s_name)
    temp_session_file = f"{target_session_base}.session"

    log_buffer = []
    account_success = False
    is_already_dead = False
    await asyncio.sleep(random.uniform(0.1, 0.8))

    for attempt in range(1, 4):
        api_pair = random.choice(api_keys)
        chosen_device = random.choice(DESKTOP_DEVICES)
        chosen_proxy = random.choice(proxies) if proxies else None

        if os.path.exists(temp_session_file):
            try: os.remove(temp_session_file)
            except Exception: pass

        proxy_timeout = 7.0 if chosen_proxy else 10.0
        old_client = create_telethon_client(session_base, api_pair, timeout=8)
        new_client = create_telethon_client(target_session_base, api_pair, timeout=proxy_timeout, device_config=chosen_device, proxy_info=chosen_proxy)

        try:
            async with get_connect_semaphore(40):
                await asyncio.wait_for(old_client.connect(), timeout=8.0)
                if not await old_client.is_user_authorized():
                    log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Logged Out / Dead{RESET}")
                    is_already_dead = True
                    break 

                await asyncio.wait_for(new_client.connect(), timeout=proxy_timeout)

            me_old = await old_client.get_me()
            phone = f"+{me_old.phone}" if me_old and me_old.phone else f"+{s_name}"

            sent_code = await asyncio.wait_for(new_client.send_code_request(phone), timeout=12.0)
            await asyncio.sleep(1.5) 

            otp_code = None
            for _ in range(6):
                async for message in old_client.iter_messages(777000, limit=2):
                    match = re.search(r'\b\d{5}\b', message.message)
                    if match:
                        otp_code = match.group(0)
                        break
                if otp_code: break
                await asyncio.sleep(1.0)

            if not otp_code:
                if attempt == 3: log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> OTP Not Received!{RESET}")
                continue

            try:
                await asyncio.wait_for(new_client.sign_in(phone=phone, code=otp_code, phone_code_hash=sent_code.phone_code_hash), timeout=12.0)
            except errors.SessionPasswordNeededError:
                if two_fa_password:
                    try: await asyncio.wait_for(new_client.sign_in(password=two_fa_password), timeout=12.0)
                    except errors.PasswordHashInvalidError:
                        log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> 2FA Password Wrong! (Skipped){RESET}")
                        break
                else:
                    log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> 2FA Required! (Skipped){RESET}")
                    break

            if await new_client.is_user_authorized():
                used_ip = chosen_proxy['ip'] if chosen_proxy else default_ip
                loc_string = chosen_proxy['geo'] if chosen_proxy else resolve_ip_geo(used_ip)
                proxy_str = f"{chosen_proxy.get('proto', 'http')}://{chosen_proxy['ip']}:{chosen_proxy['port']}" if chosen_proxy else None

                json_data = create_expert_json(s_name, phone.replace("+",""), me_old.id, me_old.first_name, me_old.last_name, me_old.username, api_pair[0], api_pair[1], two_fa_password, chosen_device, proxy_str)
                with open(os.path.join(target_folder, f"{s_name}.json"), "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)

                log_buffer.append(CYAN + "-" * 50)
                log_buffer.append(f"{CYAN}[{idx}/{total_files}] Success: {GREEN}{phone} {MAGENTA}[API: {api_pair[0]}]{RESET}")
                log_buffer.append(f"   {WHITE}OTP Code : {YELLOW}{otp_code}{RESET}")
                log_buffer.append(f"   {WHITE}Device   : {RED}{chosen_device['device_model']}{RESET}")
                log_buffer.append(f"   {WHITE}Login IP : {YELLOW}{used_ip}{WHITE} ({GREEN}{loc_string}{WHITE}){RESET}")
                log_buffer.append(f"   {YELLOW}⚡ Old Session is STILL ALIVE (No Logout)!{RESET}")

                account_success = True
                stats_dict['success'] += 1
                break 

        except (errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError, errors.AuthKeyInvalidError, errors.SessionExpiredError, errors.SessionRevokedError, errors.UserDeactivatedBanError, errors.UserDeactivatedError):
            log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Dead (Auth Invalid){RESET}")
            is_already_dead = True
            break
        except errors.ApiIdInvalidError:
            log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Failed: API ID Blocked!{RESET}")
        except Exception as e:
            err_msg = str(e).strip()[:35] if str(e).strip() else e.__class__.__name__
            if attempt == 3: log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Failed: {err_msg}{RESET}")
        finally:
            try: await old_client.disconnect()
            except Exception: pass
            try: await new_client.disconnect()
            except Exception: pass

    if account_success or is_already_dead:
        processed_folder = "Processed_Sessions"
        os.makedirs(processed_folder, exist_ok=True)
        try:
            if os.path.exists(session_file): shutil.move(session_file, os.path.join(processed_folder, os.path.basename(session_file)))
            old_json = session_file.replace('.session', '.json')
            if os.path.exists(old_json): shutil.move(old_json, os.path.join(processed_folder, os.path.basename(old_json)))
        except Exception: pass

    if not account_success and not is_already_dead:
        stats_dict['fail'] += 1
        if not log_buffer: log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Breakup Failed{RESET}")
        if os.path.exists(temp_session_file):
            try: os.remove(temp_session_file)
            except Exception: pass

    results_buffer[idx] = (log_buffer, False, None)

async def breakup_worker(queue, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip):
    while True:
        try: item = queue.get_nowait()
        except asyncio.QueueEmpty: break
        idx, s_file = item
        try: await clone_single_session_task(s_file, idx, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip)
        except Exception as e: results_buffer[idx] = ([f"{RED}Error on {s_file}: {e}{RESET}"], False, None)
        queue.task_done()

async def breakup_session():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             B R E A K U P   S E S S I O N        " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")
    print(f"{WHITE} [1] Breakup using Local Internet / VPN{RESET}")
    print(f"{WHITE} [2] Breakup using Proxies (Random IPs){RESET}")
    print(f"{WHITE} [0] Back to Main Menu{RESET}")
    print(CYAN + "────────────────────────────────────────────────────" + RESET)
    mode = input(f"\n{YELLOW}[#] Select Mode: {RESET}").strip()
    
    proxies = []
    if mode == "1": pass 
    elif mode == "2":
        proxies = load_proxies("proxies.txt")
        if not proxies:
            print(f"\n{RED}[✖] No proxies found in 'proxies.txt'!{RESET}")
            return
    elif mode == "0": return
    else: return

    api_keys = load_api_keys("api_keys.txt")
    default_ip = get_current_network_info()['ip']

    folder = input(f"\n{YELLOW}Enter Target Folder Name: {RESET}").strip()
    if not os.path.exists(folder):
        print(f"{RED}[✖] Folder not found!{RESET}")
        return

    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0:
        print(f"{RED}[✖] No .session files found!{RESET}")
        return

    pwd_input = input(f"{YELLOW}Enter global 2FA Password (type 'N' to skip): {RESET}").strip()
    two_fa_password = None if pwd_input.upper() == 'N' or not pwd_input else pwd_input
    
    w_input = input(f"{YELLOW}Worker Count [Recommended: 20-40]: {RESET}").strip()
    concurrency = int(w_input) if w_input.isdigit() and 1 <= int(w_input) <= 60 else 30

    target_folder = "breakup_session"
    os.makedirs(target_folder, exist_ok=True)

    print(f"\n{CYAN}⚡ Fast Breakup Started (No Auto-Logout)...{RESET}")
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1): queue.put_nowait((idx, s_file))

    stats_dict = {'success': 0, 'fail': 0}
    results_buffer = {}
    workers = [asyncio.create_task(breakup_worker(queue, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip)) for _ in range(min(concurrency, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task
    print(f"\n{GREEN}✔ Breakup Completed! Success: {stats_dict['success']} | Failed: {stats_dict['fail']}{RESET}")

# ================= 7: 2FA MANAGER =================
async def check_2fa_task(session_file, idx, total_files, api_keys, mode, old_pwd, new_pwd, reset_folder, stats, results_buffer):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file
    
    out = []
    api_pair = random.choice(api_keys)
    client = create_telethon_client(session_base, api_pair, timeout=10)
    is_pending_reset = False
    await asyncio.sleep(random.uniform(0.5, 2.0))

    try:
        async with get_connect_semaphore(15):
            await asyncio.wait_for(client.connect(), timeout=10.0)

        if not await client.is_user_authorized():
            out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Logged Out{RESET}")
            stats['error'] += 1
            results_buffer[idx] = (out, False, None)
            return

        pwd_info = await client(functions.account.GetPasswordRequest())
        if mode == "1":
            if pwd_info.has_password:
                try:
                    await client.edit_2fa(current_password=old_pwd, new_password=None)
                    update_json_2fa(session_file, "")
                    out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> 2FA Disabled!{RESET}")
                    stats['success'] += 1
                except errors.PasswordHashInvalidError:
                    out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Wrong Password!{RESET}")
                    stats['error'] += 1
            else:
                out.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> No 2FA exists.{RESET}")
                stats['success'] += 1
        elif mode == "2":
            if pwd_info.has_password:
                try:
                    await client.edit_2fa(current_password=old_pwd, new_password=new_pwd)
                    update_json_2fa(session_file, new_pwd)
                    out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> 2FA Changed!{RESET}")
                    stats['success'] += 1
                except errors.PasswordHashInvalidError:
                    out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Wrong Password!{RESET}")
                    stats['error'] += 1
            else:
                await client.edit_2fa(new_password=new_pwd)
                update_json_2fa(session_file, new_pwd)
                out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> New 2FA Set!{RESET}")
                stats['success'] += 1
        elif mode == "3":
            if not pwd_info.has_password:
                out.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> No 2FA to reset.{RESET}")
                stats['success'] += 1
            else:
                try:
                    await client(functions.account.ResetPasswordRequest())
                    update_json_2fa(session_file, "")
                    out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> Reset Instantly!{RESET}")
                    stats['success'] += 1
                except errors.ResetWaitError as e:
                    days = e.seconds // 86400
                    hours = (e.seconds % 86400) // 3600
                    out.append(f"{MAGENTA}[{idx}/{total_files}] {s_name} -> Pending: {days}d, {hours}h{RESET}")
                    stats['pending'] += 1
                    is_pending_reset = True
    except Exception as ex:
        err_msg = str(ex).strip()[:30] if str(ex).strip() else ex.__class__.__name__
        out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Failed: {err_msg}{RESET}")
        stats['error'] += 1
    finally:
        try: await client.disconnect()
        except Exception: pass

    if is_pending_reset:
        try:
            shutil.move(session_file, os.path.join(reset_folder, os.path.basename(session_file)))
            json_file = session_file.replace('.session', '.json')
            if os.path.exists(json_file): shutil.move(json_file, os.path.join(reset_folder, os.path.basename(json_file)))
        except: pass
    results_buffer[idx] = (out, False, None)

async def two_fa_worker(queue, total_files, api_keys, mode, old_pwd, new_pwd, reset_folder, stats, results_buffer):
    while True:
        try: item = queue.get_nowait()
        except asyncio.QueueEmpty: break
        idx, session_file = item
        await check_2fa_task(session_file, idx, total_files, api_keys, mode, old_pwd, new_pwd, reset_folder, stats, results_buffer)
        queue.task_done()

async def run_2fa_manager():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             2 F A   M A N A G E R                " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")
    print(f"{WHITE} [1] Disable 2FA\n [2] Change 2FA\n [3] Reset Password\n [0] Back{RESET}")
    mode = input(f"\n{YELLOW}[#] Select Action: {RESET}").strip()
    if mode not in ["1", "2", "3"]: return

    folder = input(f"\n{YELLOW}Enter Folder Name: {RESET}").strip()
    if not os.path.exists(folder): return
    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0: return

    old_pwd, new_pwd = "", ""
    reset_folder = "Reset_Pending_Sessions"
    if mode == "1": old_pwd = input(f"{YELLOW}Enter Current 2FA Password: {RESET}").strip()
    elif mode == "2":
        old_pwd = input(f"{YELLOW}Enter Current 2FA (leave empty if none): {RESET}").strip()
        new_pwd = input(f"{YELLOW}Enter NEW 2FA Password: {RESET}").strip()
    elif mode == "3": os.makedirs(reset_folder, exist_ok=True)

    api_keys = load_api_keys("api_keys.txt")
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1): queue.put_nowait((idx, s_file))

    stats = {'success': 0, 'pending': 0, 'error': 0}
    results_buffer = {}
    print(f"\n{CYAN}⚡ Starting 2FA Manager...{RESET}")
    workers = [asyncio.create_task(two_fa_worker(queue, total_files, api_keys, mode, old_pwd, new_pwd, reset_folder, stats, results_buffer)) for _ in range(min(15, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task
    print(f"\n{GREEN}✔ Completed! Success: {stats['success']} | Pending: {stats['pending']}{RESET}")

# ================= 5: FOLDER SESSIONS CHECKER =================
async def fast_check_session_task(session_file, idx, total_count, api_keys, default_ip, results_buffer, stats, names_list, frozen_folder):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file
    is_corrupt, is_alive, is_frozen = False, False, False
    output_buffer = []
    await asyncio.sleep(random.uniform(0.5, 1.5))

    for attempt in range(1, 4):
        api_pair = random.choice(api_keys)
        timeout_sec = 8.0 if attempt == 1 else 12.0
        client = create_telethon_client(session_base, api_pair, timeout=timeout_sec)
        try:
            async with get_connect_semaphore(35): 
                await asyncio.wait_for(client.connect(), timeout=timeout_sec)

            me_res, auth_res = await asyncio.gather(client.get_me(), client(functions.account.GetAuthorizationsRequest()), return_exceptions=True)
            if isinstance(me_res, (errors.UserDeactivatedBanError, errors.UserDeactivatedError, errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError, errors.AuthKeyInvalidError, errors.SessionPasswordNeededError, errors.SessionRevokedError, errors.SessionExpiredError)):
                is_corrupt = True
                output_buffer.append(f"{RED}[{idx}/{total_count}] {s_name} [💀 Banned/Expired]{RESET}")
                break
            if me_res is None:
                is_corrupt = True
                output_buffer.append(f"{RED}[{idx}/{total_count}] {s_name} [💀 Logged Out]{RESET}")
                break

            if not isinstance(me_res, Exception) and me_res:
                user_name = me_res.first_name if me_res.first_name else "Unknown"
                if names_list:
                    random_name = random.choice(names_list)
                    try:
                        await client(functions.account.UpdateProfileRequest(first_name=random_name))
                        user_name = f"{random_name} (Updated)"
                        is_alive = True
                    except Exception:
                        is_frozen = True
                        is_alive = False
                else: is_alive = True

                if is_alive:
                    output_buffer.append(f"{CYAN}[{idx}/{total_count}] {GREEN}User: {user_name} {WHITE}| {YELLOW}+{s_name}{RESET}")
                elif is_frozen:
                    output_buffer.append(f"{YELLOW}[{idx}/{total_count}] {s_name} [❄️ FROZEN - Name Change Failed]{RESET}")
                break
        except Exception:
            await asyncio.sleep(0.3 * attempt)
            continue
        finally:
            try: await client.disconnect()
            except Exception: pass

    if is_frozen:
        try:
            shutil.move(session_file, os.path.join(frozen_folder, os.path.basename(session_file)))
            json_file = session_file.replace('.session', '.json')
            if os.path.exists(json_file): shutil.move(json_file, os.path.join(frozen_folder, os.path.basename(json_file)))
        except: pass

    if is_corrupt: stats['corrupt'] += 1
    elif is_frozen: stats['frozen'] += 1
    elif is_alive: stats['alive'] += 1
    else: stats['error'] += 1
    results_buffer[idx] = (output_buffer, is_corrupt, session_file)

async def check_queue_worker(queue, total_count, api_keys, default_ip, results_buffer, stats, names_list, frozen_folder):
    while True:
        try: item = queue.get_nowait()
        except asyncio.QueueEmpty: break
        idx, session_file = item
        try: await fast_check_session_task(session_file, idx, total_count, api_keys, default_ip, results_buffer, stats, names_list, frozen_folder)
        except Exception: results_buffer[idx] = ([], False, None)
        queue.task_done()

async def check_folder_sessions():
    api_keys = load_api_keys("api_keys.txt")
    default_ip = get_current_network_info()['ip']
    folder = input(f"\n{YELLOW}Enter Folder Name: {RESET}").strip()
    if not os.path.exists(folder): return
    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0: return

    change_name_opt = input(f"{YELLOW}Randomly change account names? (Y/N): {RESET}").strip().upper()
    names_list = AUTO_NAMES_LIST if change_name_opt == 'Y' else []
    frozen_folder = "Frozen_Sessions"
    if names_list: os.makedirs(frozen_folder, exist_ok=True)

    print(f"\n{CYAN}Starting Session Check...{RESET}")
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1): queue.put_nowait((idx, s_file))
    stats = {'alive': 0, 'corrupt': 0, 'frozen': 0, 'error': 0}
    results_buffer = {}
    workers = [asyncio.create_task(check_queue_worker(queue, total_files, api_keys, default_ip, results_buffer, stats, names_list, frozen_folder)) for _ in range(min(30, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task
    print(f"\n{GREEN}✔ Completed! Alive: {stats['alive']} | Dead: {stats['corrupt']} | Frozen: {stats['frozen']}{RESET}")

# ================= PLACEHOLDERS =================
async def join_public_channel(): print(f"\n{YELLOW}[!] Join Channel feature is coming soon!{RESET}")
async def read_otp(): print(f"\n{YELLOW}[!] Read OTP feature is coming soon!{RESET}")
async def clear_all_history(): print(f"\n{YELLOW}[!] History feature is coming soon!{RESET}")
async def session_to_json(): print(f"\n{YELLOW}[!] Session to JSON Converter feature is coming soon!{RESET}")
def spam_check_menu(): print(f"\n{YELLOW}[!] Spam Check feature is coming soon!{RESET}")
async def run_kill_session(): print(f"\n{YELLOW}[!] Kill Session feature is coming soon!{RESET}")

def main():
    startup_channel_prompt()
    while True:
        show_banner()
        choice = input(f"\n{YELLOW}[#] Select Option: {RESET}").strip().upper()

        if choice in ["1"]: asyncio.run(create_session())
        elif choice in ["2"]: upload_and_check_proxies()
        elif choice in ["3"]: asyncio.run(upload_and_check_api_keys())
        elif choice in ["4"]: asyncio.run(join_public_channel())
        elif choice in ["5"]: asyncio.run(check_folder_sessions())
        elif choice in ["6"]: asyncio.run(breakup_session())
        elif choice in ["7"]: asyncio.run(run_2fa_manager())
        elif choice in ["8"]: asyncio.run(read_otp())
        elif choice in ["9"]: asyncio.run(clear_all_history())
        elif choice in ["10"]: asyncio.run(session_to_json())
        elif choice in ["11"]: spam_check_menu()
        elif choice in ["12"]: asyncio.run(run_kill_session())
        elif choice in ["0", "E", "EXIT"]:
            print(f"\n{RED}[!] Exiting Tools. Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}[✖] Invalid Option!{RESET}")
        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
