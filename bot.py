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
    print("\n[!] প্রয়োজনীয় লাইব্রেরি ইনস্টল করা হচ্ছে (Telethon, Python-Socks)...")
    os.system(f"{sys.executable} -m pip install --upgrade telethon python-socks")
    print("\n[✔] সেটআপ সম্পন্ন! স্ক্রিপ্ট রিস্টার্ট হচ্ছে...\n")
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

# টেলিথনের ব্যাকগ্রাউন্ড লগ বন্ধ করা হলো
logging.getLogger('telethon').setLevel(logging.CRITICAL)
init(autoreset=True)

# ================= 🔴 আপনার গিটহাব প্রক্সি লিংক এখানে দিন 🔴 =================
# গিটহাবে আপনার proxies.txt ফাইলটি ওপেন করে "Raw" বাটনে ক্লিক করুন এবং সেই লিংকটি এখানে দিন।
# যদি লিংক ফাঁকা থাকে, তবে এটি লোকাল proxies.txt ব্যবহার করবে।
GITHUB_PROXY_URL = "" 
# উদাহরণ: GITHUB_PROXY_URL = "https://raw.githubusercontent.com/আপনার_ইউজারনেম/TeleChecker/main/proxies.txt"

# ডিফল্ট API Key
DEFAULT_API_ID = 25762761
DEFAULT_API_HASH = "f6712ac15fa56c713451eede724261eb"

# ================= 250+ AUTO NAMES LIST =================
AUTO_NAMES_LIST = [
    "RK", "ER", "RJ", "JEB", "Alex", "Sam", "Max", "Leo", "Ray", "Tom", "Bob", "Tim", "Jay", "Roy", 
    "Jon", "Dan", "Eli", "Ian", "Mac", "Abe", "Ben", "Cal", "Hal", "Sal", "Vic", "Zak", "Kai", "Jax", 
    "Fox", "Rex", "Ash", "Cid", "Dax", "Gus", "Kip", "Lex", "Ned", "Paz", "Taj", "Van", "Wes", "Zed",
    "John", "David", "Michael", "James", "Robert", "William", "Mary", "Patricia", "Jennifer", "Linda", 
    "Elizabeth", "Richard", "Joseph", "Charles", "Thomas", "Christopher", "Daniel", "Matthew", "Anthony", 
    "Muhammad", "Ahmed", "Ali", "Omar", "Abdullah", "Tariq", "Khalid", "Hassan", "Hussein", "Ibrahim", 
    "Adam", "Hawwa", "Maryam", "Asiya", "Khadija", "Aisha", "Fatima", "Zainab", "Ruqayyah", "Umm Kulthum",
    "Zaynab", "Zayn", "Zayd", "Qais", "Saad", "Fahd", "Badr", "Jamal", "Kamal", "Tariq", "Raed", "Anwar"
]

# ================= 25 PREMIUM DESKTOP MODELS =================
DESKTOP_DEVICES = [
    {"device_model": "Windows 10 x64", "system_version": "10.0.19045", "app_version": "4.8.4 x64"},
    {"device_model": "Windows 11 x64", "system_version": "10.0.22621", "app_version": "4.11.2 x64"},
    {"device_model": "Ubuntu 22.04 LTS", "system_version": "Linux 5.15", "app_version": "4.9.1 x64"},
    {"device_model": "MacBook Pro M1", "system_version": "macOS 13.5", "app_version": "4.10.0 arm64"},
    {"device_model": "Windows 8.1 x64", "system_version": "6.3.9600", "app_version": "4.7.1 x64"},
    {"device_model": "Linux Mint 21", "system_version": "Linux 5.15", "app_version": "4.9.2 x64"},
    {"device_model": "iMac 27-inch", "system_version": "macOS 12.6", "app_version": "4.6.3 x64"},
    {"device_model": "Fedora 38", "system_version": "Linux 6.4", "app_version": "4.11.0 x64"},
    {"device_model": "Windows 11 x64", "system_version": "10.0.22000", "app_version": "4.10.5 x64"}
]

GEO_CACHE = {}
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

CYAN = Fore.CYAN + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
MAGENTA = Fore.MAGENTA + Style.BRIGHT
WHITE = Fore.WHITE + Style.BRIGHT
RESET = Style.RESET_ALL

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

# ================= STARTUP CHANNEL PROMPT & PROXY FETCHER =================
def fetch_online_proxies():
    if not GITHUB_PROXY_URL:
        return
    print(f"\n{YELLOW} [*] গিটহাব থেকে নতুন প্রক্সি ডাউনলোড করা হচ্ছে...{RESET}")
    try:
        req = urllib.request.Request(GITHUB_PROXY_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            proxy_data = resp.read().decode('utf-8')
            if proxy_data.strip():
                with open("proxies.txt", "w", encoding="utf-8") as f:
                    f.write(proxy_data)
                print(f"{GREEN} [✔] প্রক্সি সফলভাবে আপডেট হয়েছে!{RESET}")
    except Exception as e:
        print(f"{RED} [✖] গিটহাব থেকে প্রক্সি আপডেট ফেইল হয়েছে (লোকাল প্রক্সি ব্যবহার হবে)।{RESET}")
    
def startup_channel_prompt():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "              🔥 WELCOME TO CHECKER V6 🔥               " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════════════╝")
    print(f"\n{WHITE} 🚀 আমাদের নতুন আপডেট এবং সাপোর্ট পেতে টেলিগ্রাম চ্যানেলে জয়েন করুন!{RESET}")
    print(f"{GREEN} 👉 https://t.me/WORLD_UPDATE_TOP1 👈{RESET}\n")
    print(f"{YELLOW} [*] চ্যানেলটি অটোমেটিক ওপেন করা হচ্ছে...{RESET}")
    
    url = "https://t.me/WORLD_UPDATE_TOP1"
    
    try:
        if "com.termux" in os.environ.get("PREFIX", "") or os.path.exists('/data/data/com.termux/files/usr/bin/termux-open-url'):
            os.system(f"termux-open-url {url} > /dev/null 2>&1")
        elif sys.platform == 'win32':
            os.system(f"start {url}")
        elif sys.platform == 'darwin':
            os.system(f"open {url}")
        else:
            webbrowser.open(url)
    except Exception:
        pass
        
    fetch_online_proxies() # গিটহাব থেকে প্রক্সি ডাউনলোড
    input(f"\n{YELLOW} [?] চ্যানেলে জয়েন করা হলে, মূল মেনুতে যেতে ENTER চাপুন... {RESET}")

# ================= ACCURATE GEO-LOCATION RESOLVER =================
def resolve_ip_geo(ip):
    if not ip or ip.lower() in ['unknown', 'localhost', '127.0.0.1']: return "Unknown Location"
    if ip in GEO_CACHE: return GEO_CACHE[ip]
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=status,country,city,regionName", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('status') == 'success':
                loc = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
                if loc:
                    GEO_CACHE[ip] = loc
                    return loc
    except Exception: pass
    return "Unknown Location"

def get_current_network_info():
    try:
        req = urllib.request.Request("http://ip-api.com/json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            loc = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
            return {'ip': data.get('query', 'Unknown IP'), 'location': loc if loc else "Unknown Location", 'isp': data.get('isp', ''), 'status': True}
    except Exception:
        return {'ip': 'Direct / Local IP', 'location': 'Local Network / Device', 'isp': 'Direct Mobile / WiFi', 'status': False}

def show_banner():
    clear_screen()
    net = get_current_network_info()
    vpn_status = f"{GREEN}ONLINE 🌐{RESET}" if net['status'] else f"{YELLOW}LOCAL / DIRECT 📶{RESET}"
    
    print(CYAN + "╔══════════════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "                 C H E C K E R   V 6 (FAST PROXY)         " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════════════╝")
    print(f"{WHITE} » IP Address  : {YELLOW}{net['ip']}{RESET}")
    print(f"{WHITE} » Location    : {GREEN}{net['location']}{RESET}")
    print(f"{WHITE} » Network/VPN : {MAGENTA}{net['isp']}{RESET} [{vpn_status}]")
    print(f"{WHITE} » Contact     : {CYAN}Telegram 👉 @WORLD_UPDATE_TOP1{RESET}")
    print(CYAN + "──────────────────────────────────────────────────────────")
    print(f"{CYAN} [1] {GREEN}⚡ {YELLOW}Create Session & JSON{RESET}")
    print(f"{CYAN} [2] {GREEN}🌐 {GREEN}Upload / Check Proxies (Auto Format Detect){RESET}")
    print(f"{CYAN} [3] {GREEN}🔑 {MAGENTA}Upload / Check API Keys{RESET}")
    print(f"{CYAN} [4] {GREEN}👥 {Fore.BLUE + Style.BRIGHT}Join Public Channel / Group (Auto Join){RESET}")
    print(f"{CYAN} [5] {GREEN}🔰 {GREEN}Check Folder Sessions (With Auto Name Changer){RESET}")
    print(f"{CYAN} [6] {GREEN}💔 {YELLOW}Breakup Session Menu (No Auto-Logout){RESET}")
    print(f"{CYAN} [7] {GREEN}🔐 {MAGENTA}2FA Manager (Change/Disable/Reset){RESET}")
    print(f"{CYAN} [8] {GREEN}🔢 {RED}Read OTP Session{RESET}")
    print(f"{CYAN} [9] {GREEN}🧹 {RED}Clear All Chat History{RESET}")
    print(f"{CYAN}[10] {GREEN}📁 {YELLOW}Session to JSON Converter{RESET}")
    print(f"{CYAN}[11] {GREEN}🛡️ {MAGENTA}Spam Check Menu{RESET}")
    print(f"{CYAN}[12] {GREEN}🔥 {RED}Kill Session (Self Logout){RESET}")
    print(f"{CYAN} [0] {GREEN}🚨 {RED}Exit Tools{RESET}")
    print(CYAN + "══════════════════════════════════════════════════════════" + RESET)

def universal_proxy_parser(raw_text):
    proxies = []
    lines = raw_text.replace(',', '\n').split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        chunks = line.split()
        if len(chunks) == 4 and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', chunks[0]) and chunks[1].isdigit():
            proxies.append(f"{chunks[0]}:{chunks[1]}:{chunks[2]}:{chunks[3]}")
            continue
        elif len(chunks) == 2 and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', chunks[0]) and chunks[1].isdigit():
            proxies.append(f"{chunks[0]}:{chunks[1]}")
            continue
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
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown Location" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port), 'user': user, 'pwd': pwd, 'geo': loc})
            else:
                parts = line.split(":")
                if len(parts) >= 4:
                    ip, port, user, pwd = parts[0], int(parts[1]), parts[2], parts[3]
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown Location" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port), 'user': user, 'pwd': pwd, 'geo': loc})
                elif len(parts) == 2:
                    ip, port = parts[0], int(parts[1])
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown Location" else resolve_ip_geo(ip)
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
    corrupt_dir = "sesi_corupt"
    os.makedirs(corrupt_dir, exist_ok=True)
    try:
        base_name = os.path.basename(session_file_path)
        dest_path = os.path.join(corrupt_dir, base_name)
        if os.path.exists(dest_path): os.remove(dest_path)
        shutil.move(session_file_path, dest_path)
        journal = session_file_path + "-journal"
        if os.path.exists(journal):
            j_dest = os.path.join(corrupt_dir, os.path.basename(journal))
            if os.path.exists(j_dest): os.remove(j_dest)
            shutil.move(journal, j_dest)
    except Exception:
        pass

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
        session_base, 
        api_pair[0], 
        api_pair[1], 
        device_model=dm,
        system_version=sv,
        app_version=av,
        lang_code="en",
        system_lang_code="en-US",
        proxy=proxy_dict,
        connection=ConnectionTcpAbridged if proxy_dict else ConnectionTcpIntermediate, 
        timeout=timeout, 
        auto_reconnect=False, 
        connection_retries=1, 
        retry_delay=1, 
        flood_sleep_threshold=20
    )

def create_expert_json(session_name, phone, user_id, first_name, last_name, username, api_id, api_hash, two_fa, device_config=None, proxy_info=None):
    current_time = datetime.now(timezone(timedelta(hours=7))).isoformat()
    dev_model = device_config['device_model'] if device_config else "HP Spectre x360 14"
    app_ver = device_config['app_version'] if device_config else "6.8.2 x64"
    sys_ver = device_config['system_version'] if device_config else "Windows 10 x64"

    return {
        "twoFA": two_fa if two_fa and str(two_fa).upper() != 'N' else "",
        "spambot": "free",
        "session_file": session_name,
        "phone": phone,
        "user_id": user_id,
        "app_id": api_id,
        "app_hash": api_hash,
        "sdk": sys_ver,
        "app_version": app_ver,
        "device": dev_model,
        "last_check_time": current_time,
        "first_name": first_name or "",
        "last_name": last_name or "",
        "username": username or "",
        "proxy": proxy_info
    }

async def ordered_output_printer(results_buffer, total_files):
    next_idx = 1
    while next_idx <= total_files:
        while next_idx not in results_buffer:
            await asyncio.sleep(0.01)
        output_buffer, is_corrupt, session_file = results_buffer.pop(next_idx)
        for line in output_buffer: print(line)
        if is_corrupt and session_file:
            try: move_to_corrupt(session_file)
            except Exception: pass
        await asyncio.sleep(0.05)
        next_idx += 1

# ================= OPTION 2: ADVANCED TCP PING PROXY TESTER =================
def test_single_proxy_thread(p_str, idx, is_http=False):
    parts = p_str.split(':')
    ip, port = parts[0], int(parts[1])
    proto_prefix = "http" if is_http else "socks5"
    try:
        with socket.create_connection((ip, port), timeout=4.0):
            loc = resolve_ip_geo(ip)
            return (True, f"{proto_prefix}://{p_str}", f"{GREEN}[ALIVE #{idx}] [{proto_prefix.upper()}] {ip}:{port} -> ({loc}){RESET}")
    except Exception:
        return (False, None, f"{RED}[DEAD #{idx}] {ip}:{port} - Timeout{RESET}")

def upload_and_check_proxies():
    print(f"\n{CYAN}--- UNIVERSAL PROXY AUTO-UPLOADER ---{RESET}")
    print(f"{YELLOW}Paste your proxies below. Type 'DONE' on a new line when finished:{RESET}\n")
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
        print(f"{RED}[✖] No valid proxies detected in input!{RESET}")
        return

    print(f"\n{GREEN}✔ Automatically Detected & Extracted {len(found_proxies)} Proxies!{RESET}")
    proto_opt = input(f"{YELLOW}Protocol: [1] HTTP/HTTPS  [2] SOCKS5: {RESET}").strip()
    is_http_proxy = True if proto_opt == "1" else False
    proto_name = "http" if is_http_proxy else "socks5"

    opt = input(f"{YELLOW}Options: [1] Save Directly  [2] Test Connections First: {RESET}").strip()

    if opt == "1":
        with open("proxies.txt", "w", encoding="utf-8") as f:
            for vp in found_proxies: f.write(f"{proto_name}://{vp}\n")
        print(f"\n{GREEN}✔ SUCCESS! {len(found_proxies)} Proxies saved directly as {proto_name.upper()} in 'proxies.txt'.{RESET}")
    elif opt == "2":
        print(f"\n{YELLOW}[*] Testing Connections...{RESET}")
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
            print(f"{GREEN}✔ SUCCESS! Saved {len(valid_proxies)} active proxies to 'proxies.txt'.{RESET}")
        else: print(f"{RED}[✖] No working proxies found.{RESET}")

# ================= OPTION 1: CREATE SESSION AND JSON =================
async def create_session():
    api_keys = load_api_keys("api_keys.txt")
    folder = input(f"\n{YELLOW}Enter Folder Name to save Session & JSON (e.g. 20, 880): {RESET}").strip()
    folder = folder if folder else "sessions"
    os.makedirs(folder, exist_ok=True)
    two_fa_input = input(f"{YELLOW}Enter 2FA Password to save in JSON (Type 'N' if no password): {RESET}").strip()
    two_fa_pass = "" if two_fa_input.upper() == 'N' else two_fa_input

    session_count = 1
    while True:
        api_pair = random.choice(api_keys)
        chosen_device = random.choice(DESKTOP_DEVICES)
        phone = input(f"\n{YELLOW}Enter Telegram Phone Number (or 'E' to Exit): {RESET}").strip()
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
                    with open(os.path.join(folder, f"{session_name}.json"), "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=4, ensure_ascii=False)
                    session_count += 1
                except Exception as e: print(f"{RED}[✖] Error: {e}{RESET}")
            else: print(f"{GREEN}[✔] Account is already Authorized!{RESET}")
        finally:
            try: await client.disconnect()
            except Exception: pass

# ================= OPTION 6: BREAKUP SESSION (NO AUTO-LOGOUT) =================
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
                    log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Already Logged Out / Dead{RESET}")
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

                log_buffer.append(CYAN + "=" * 58)
                log_buffer.append(f"{CYAN}[{idx}/{total_files}] Breakup Success: {GREEN}{phone} {MAGENTA}[API: {api_pair[0]}]{RESET}")
                log_buffer.append(f"    {WHITE}OTP Code     : {YELLOW}{otp_code}{RESET}")
                log_buffer.append(f"    {GREEN}✔ Saved to   : {CYAN}'{target_folder}'{RESET}")
                log_buffer.append(f"    {YELLOW}⚡ Old Session is STILL ALIVE (No Auto Logout)!{RESET}")

                account_success = True
                stats_dict['success'] += 1
                break 

        except (errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError, errors.AuthKeyInvalidError, errors.SessionExpiredError, errors.SessionRevokedError, errors.UserDeactivatedBanError, errors.UserDeactivatedError):
            log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Already Logged Out / Dead{RESET}")
            is_already_dead = True
            break
        except Exception as e:
            if attempt == 3: log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Failed: {str(e)[:40]}{RESET}")
        finally:
            try: await old_client.disconnect()
            except Exception: pass
            try: await new_client.disconnect()
            except Exception: pass

    # ব্রেকআপ হলেও ফাইল ডিলিট না হয়ে প্রসেসড ফোল্ডারে যাবে (যেহেতু অটো লগআউট বন্ধ)
    if account_success or is_already_dead:
        target_processed_folder = "Dead_Sessions" if is_already_dead else "Processed_Old_Sessions"
        os.makedirs(target_processed_folder, exist_ok=True)
        try:
            if os.path.exists(session_file):
                shutil.move(session_file, os.path.join(target_processed_folder, os.path.basename(session_file)))
            old_json = session_file.replace('.session', '.json')
            if os.path.exists(old_json):
                shutil.move(old_json, os.path.join(target_processed_folder, os.path.basename(old_json)))
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
        await clone_single_session_task(s_file, idx, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip)
        queue.task_done()

async def breakup_session():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             B R E A K U P   S E S S I O N                " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════════════╝")
    mode = input(f"\n{YELLOW}[1] Local IP / VPN  [2] Proxies \n[#] Select Mode: {RESET}").strip()
    
    proxies = []
    if mode == "2":
        proxies = load_proxies("proxies.txt")
        if not proxies:
            print(f"\n{RED}[✖] No proxies found in 'proxies.txt'!{RESET}")
            return
    elif mode != "1": return

    api_keys = load_api_keys("api_keys.txt")
    default_ip = get_current_network_info()['ip']
    folder = input(f"\n{YELLOW}Enter Folder Name (e.g. 20, 880): {RESET}").strip()
    if not os.path.exists(folder): return

    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0: return

    pwd_input = input(f"{YELLOW}Enter global 2FA Password (type 'N' to skip): {RESET}").strip()
    two_fa_password = None if pwd_input.upper() == 'N' or not pwd_input else pwd_input
    
    concurrency = 30
    target_folder = "breakup_session"
    os.makedirs(target_folder, exist_ok=True)

    print(f"\n{CYAN}⚡ Breakup Started (Old Sessions will NOT be killed)...{RESET}")
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1): queue.put_nowait((idx, s_file))

    stats_dict = {'success': 0, 'fail': 0}
    results_buffer = {}
    workers = [asyncio.create_task(breakup_worker(queue, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip)) for _ in range(min(concurrency, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task
    print(f"\n{GREEN}✔ Breakup Session Completed! Success: {stats_dict['success']}{RESET}")

# ================= OPTION 4: JOIN PUBLIC CHANNEL =================
async def join_single_channel_task(session_file, idx, total_count, api_keys, target_channel, results_buffer):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file
    await asyncio.sleep(random.uniform(0.5, 2.0))
    
    api_pair = random.choice(api_keys)
    client = create_telethon_client(session_base, api_pair, timeout=10)
    out = []
    is_corrupt = False

    try:
        async with get_connect_semaphore(20):
            await asyncio.wait_for(client.connect(), timeout=10.0)
        if not await client.is_user_authorized():
            out.append(f"{RED}[{idx}/{total_count}] {s_name} -> Dead / Unauthorized{RESET}")
            is_corrupt = True
        else:
            await client(functions.channels.JoinChannelRequest(channel=target_channel))
            out.append(f"{GREEN}[{idx}/{total_count}] {s_name} -> Successfully Joined {target_channel}!{RESET}")
    except errors.UserBannedInChannelError:
        out.append(f"{YELLOW}[{idx}/{total_count}] {s_name} -> Banned from this channel!{RESET}")
    except Exception as e:
        out.append(f"{RED}[{idx}/{total_count}] {s_name} -> Failed: {str(e)[:30]}{RESET}")
    finally:
        try: await client.disconnect()
        except Exception: pass

    results_buffer[idx] = (out, is_corrupt, session_file)

async def join_channel_worker(queue, total_count, api_keys, target_channel, results_buffer):
    while True:
        try: item = queue.get_nowait()
        except asyncio.QueueEmpty: break
        idx, session_file = item
        await join_single_channel_task(session_file, idx, total_count, api_keys, target_channel, results_buffer)
        queue.task_done()

async def join_public_channel():
    api_keys = load_api_keys("api_keys.txt")
    folder = input(f"\n{YELLOW}Enter Folder Name with sessions (e.g. 20, 880): {RESET}").strip()
    if not os.path.exists(folder):
        print(f"{RED}[✖] Folder not found!{RESET}")
        return
        
    target_channel = input(f"{YELLOW}Enter Channel Link or @username (e.g. WORLD_UPDATE_TOP1): {RESET}").strip()
    if not target_channel: return
    if "t.me/" in target_channel: target_channel = target_channel.split("t.me/")[1].split("/")[0]
    if not target_channel.startswith("@"): target_channel = "@" + target_channel

    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0: return

    print(f"\n{CYAN}⚡ Joining {target_channel} with {total_files} accounts...{RESET}")
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1): queue.put_nowait((idx, s_file))
    
    results_buffer = {}
    workers = [asyncio.create_task(join_channel_worker(queue, total_files, api_keys, target_channel, results_buffer)) for _ in range(min(20, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task
    print(f"\n{GREEN}✔ Join Channel Process Completed!{RESET}")

# ================= PLACEHOLDERS =================
async def run_2fa_manager(): print(f"\n{YELLOW}[!] 2FA Manager is loaded in original script.{RESET}")
async def check_folder_sessions(): print(f"\n{YELLOW}[!] Folder Session Checker loaded.{RESET}")
async def clear_all_history(): print(f"\n{YELLOW}[!] History Cleaner loaded.{RESET}")
async def run_kill_session(): print(f"\n{YELLOW}[!] Kill Session loaded.{RESET}")
def spam_check_menu(): print(f"\n{YELLOW}[!] Spam Check loaded.{RESET}")

def main():
    # 🚀 স্ক্রিপ্ট রান হওয়ার সাথে সাথে চ্যানেল ওপেন করবে এবং গিটহাব থেকে প্রক্সি ডাউনলোড করবে
    startup_channel_prompt()
    
    while True:
        show_banner()
        choice = input(f"\n{YELLOW}[#] Select Option: {RESET}").strip().upper()

        if choice in ["1"]: asyncio.run(create_session())
        elif choice in ["2"]: upload_and_check_proxies()
        elif choice in ["4"]: asyncio.run(join_public_channel())
        elif choice in ["5"]: asyncio.run(check_folder_sessions())
        elif choice in ["6"]: asyncio.run(breakup_session())
        elif choice in ["7"]: asyncio.run(run_2fa_manager())
        elif choice in ["9"]: asyncio.run(clear_all_history())
        elif choice in ["11"]: spam_check_menu()
        elif choice in ["12"]: asyncio.run(run_kill_session())
        elif choice in ["0", "E", "EXIT"]:
            print(f"\n{RED}[!] Exiting Tools. Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}[✖] Feature not integrated in this preview or invalid option!{RESET}")

        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Exiting...{RESET}")
        sys.exit(0)