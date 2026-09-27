import os
import sys
import types
import socket
import webbrowser
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

# PYTHON 3.13+ COMPATIBILITY FIX
if 'imghdr' not in sys.modules:
    imghdr_mock = types.ModuleType('imghdr')
    imghdr_mock.what = lambda file, h=None: 'jpeg'
    sys.modules['imghdr'] = imghdr_mock

try:
    import telethon
    import python_socks
    from colorama import Fore, Style, init
    if telethon.__version__ < '1.30.0':
        raise ImportError("Telethon too old")
except ImportError:
    print("\n[!] Installing required libraries (Telethon, Python-Socks, Colorama)...")
    os.system(f"{sys.executable} -m pip install --upgrade telethon python-socks colorama")
    print("\n[✔] Setup complete! Restarting script...\n")
    os.execv(sys.executable, ['python'] + sys.argv)

from telethon import TelegramClient, errors, functions
from telethon.network import ConnectionTcpIntermediate, ConnectionTcpAbridged

# Disable Telethon background logging
logging.getLogger('telethon').setLevel(logging.CRITICAL)
init(autoreset=True)

# ================= 🔴 GITHUB URLs (PROXIES & API KEYS) 🔴 =================
GITHUB_PROXY_URL = "https://raw.githubusercontent.com/wptg880-sketch/wp_tg/main/proxies.txt"
GITHUB_API_URL = "https://raw.githubusercontent.com/wptg880-sketch/wp_tg/main/api_keys.txt"

# Default API Key (Fallback if GitHub fails)
DEFAULT_API_ID = 25762761
DEFAULT_API_HASH = "f6712ac15fa56c713451eede724261eb"

# ================= 📁 BASE DIRECTORY FOR PHONE STORAGE 📁 =================
BASE_DIR = "/storage/emulated/0/termux"

try:
    os.makedirs(BASE_DIR, exist_ok=True)
except PermissionError:
    print(f"\n\033[1;31m[!] PERMISSION ERROR: Please run 'termux-setup-storage' in termux first!\033[0m\n")
    BASE_DIR = "termux_sessions"
    os.makedirs(BASE_DIR, exist_ok=True)

# ================= PREMIUM DESKTOP MODELS =================
DESKTOP_DEVICES = [
    {"device_model": "Windows 10 x64", "system_version": "10.0.19045", "app_version": "4.8.4 x64"},
    {"device_model": "Windows 11 x64", "system_version": "10.0.22621", "app_version": "4.11.2 x64"},
    {"device_model": "Ubuntu 22.04 LTS", "system_version": "Linux 5.15", "app_version": "4.9.1 x64"},
    {"device_model": "MacBook Pro M1", "system_version": "macOS 13.5", "app_version": "4.10.0 arm64"},
    {"device_model": "Windows 8.1 x64", "system_version": "6.3.9600", "app_version": "4.7.1 x64"},
    {"device_model": "Linux Mint 21", "system_version": "Linux 5.15", "app_version": "4.9.2 x64"}
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

# ================= GITHUB AUTO FETCHERS =================
def fetch_online_proxies():
    if not GITHUB_PROXY_URL: return
    try:
        req = urllib.request.Request(GITHUB_PROXY_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            proxy_data = resp.read().decode('utf-8')
            if proxy_data.strip():
                with open("proxies.txt", "w", encoding="utf-8") as f: f.write(proxy_data)
    except Exception: pass

def get_github_apis():
    api_list = []
    if GITHUB_API_URL:
        try:
            req = urllib.request.Request(GITHUB_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=7.0) as resp:
                data = resp.read().decode('utf-8')
                for line in data.split('\n'):
                    match = re.search(r'(\d{5,10})\s*[:\s,\t]+\s*([a-fA-F0-9]{32})', line)
                    if match:
                        pair = (int(match.group(1)), match.group(2))
                        if pair not in api_list: api_list.append(pair)
        except Exception: pass
    return api_list if api_list else [(DEFAULT_API_ID, DEFAULT_API_HASH)]

def startup_channel_prompt():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             WELCOME TO CHECKER V6                " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")
    print(f"\n{WHITE} 🚀 Join our Telegram Channel for updates!{RESET}")
    print(f"{GREEN} 👉 https://t.me/WORLD_UPDATE_TOP1 👈{RESET}\n")
    print(f"{YELLOW} [*] Opening channel automatically...{RESET}")
    print(f"{YELLOW} [*] Fetching latest Proxies & APIs from GitHub...{RESET}")
    
    url = "https://t.me/WORLD_UPDATE_TOP1"
    try:
        if "com.termux" in os.environ.get("PREFIX", "") or os.path.exists('/data/data/com.termux/files/usr/bin/termux-open-url'):
            os.system(f"termux-open-url {url} > /dev/null 2>&1")
        elif sys.platform == 'win32': os.system(f"start {url}")
        elif sys.platform == 'darwin': os.system(f"open {url}")
        else: webbrowser.open(url)
    except Exception: pass
        
    fetch_online_proxies()
    input(f"\n{YELLOW} [?] Press ENTER to continue to Main Menu... {RESET}")

# ================= LOCATION & NETWORK =================
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
    print(f"{CYAN} [2] {GREEN}🌐 {GREEN}Check Extracted Proxies{RESET}")
    print(f"{CYAN} [3] {GREEN}🔑 {MAGENTA}API Keys (Auto Fetched from GitHub){RESET}")
    print(f"{CYAN} [4] {GREEN}👥 {BLUE}Join Public Channel / Group{RESET}")
    print(f"{CYAN} [5] {GREEN}🔰 {GREEN}Check Folder Sessions (Advanced Mode){RESET}")
    print(f"{CYAN} [6] {GREEN}💔 {YELLOW}Breakup Session (Fast Mode){RESET}")
    print(f"{CYAN} [7] {GREEN}🔐 {MAGENTA}2FA Manager (Change/Disable/Reset){RESET}")
    print(f"{CYAN} [8] {GREEN}🧹 {RED}Clear All Chat History{RESET}")
    print(f"{CYAN} [9] {GREEN}🔥 {RED}Kill Session (Self Logout){RESET}")
    print(f"{CYAN} [0] {GREEN}🚨 {RED}Exit Tools{RESET}")
    print(CYAN + "════════════════════════════════════════════════════" + RESET)
    print(f"{WHITE}[*] Base Storage Path: {GREEN}{BASE_DIR}{RESET}")

# ================= UTILS =================
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

def move_session_files(session_file_path, target_dir_name):
    target_dir = os.path.join(BASE_DIR, target_dir_name)
    os.makedirs(target_dir, exist_ok=True)
    try:
        dest_path = os.path.join(target_dir, os.path.basename(session_file_path))
        if os.path.exists(dest_path): os.remove(dest_path)
        shutil.move(session_file_path, dest_path)
        
        json_file = session_file_path.replace('.session', '.json')
        if os.path.exists(json_file):
            j_dest = os.path.join(target_dir, os.path.basename(json_file))
            if os.path.exists(j_dest): os.remove(j_dest)
            shutil.move(json_file, j_dest)
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

    dm = device_config['device_model'] if device_config else "Windows PC"
    sv = device_config['system_version'] if device_config else "Windows 10"
    av = device_config['app_version'] if device_config else "4.8.4"

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
    app_ver = device_config['app_version'] if device_config else "4.8.4"
    sys_ver = device_config['system_version'] if device_config else "Windows 10"

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
        output_buffer = results_buffer.pop(next_idx)
        for line in output_buffer: print(line)
        await asyncio.sleep(0.02) 
        next_idx += 1

# ================= 5: ADVANCED CHECK FOLDER SESSIONS =================
async def fast_check_session_task(session_file, idx, total_count, api_keys, proxies, default_ip, results_buffer, stats):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file
    
    output_buffer = []
    is_corrupt, is_alive, is_frozen = False, False, False

    await asyncio.sleep(random.uniform(0.1, 0.5))

    for attempt in range(1, 4):
        api_pair = random.choice(api_keys)
        chosen_proxy = random.choice(proxies) if proxies else None
        timeout_sec = 8.0 if chosen_proxy else 10.0
        
        client = create_telethon_client(session_base, api_pair, timeout=timeout_sec, proxy_info=chosen_proxy)

        try:
            async with get_connect_semaphore(40): 
                await asyncio.wait_for(client.connect(), timeout=timeout_sec)

            me_res, auth_res = await asyncio.gather(client.get_me(), client(functions.account.GetAuthorizationsRequest()), return_exceptions=True)
            
            # 1. Check if Banned / Logged Out
            if isinstance(me_res, (errors.UserDeactivatedBanError, errors.UserDeactivatedError, errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError, errors.AuthKeyInvalidError, errors.SessionPasswordNeededError, errors.SessionRevokedError, errors.SessionExpiredError)) or me_res is None:
                is_corrupt = True
                output_buffer.append(f"{RED}[{idx}/{total_count}] {s_name} [💀 Banned / Logged Out]{RESET}")
                break

            # 2. Check if Alive or Frozen (by sending 'hi' to Saved Messages)
            if not isinstance(me_res, Exception) and me_res:
                try:
                    # Send message to oneself
                    msg = await asyncio.wait_for(client.send_message('me', 'hi'), timeout=7.0)
                    await client.delete_messages('me', [msg.id], revoke=True) # Clean up
                    is_alive = True
                except Exception as e:
                    # If sending fails, consider it Frozen
                    is_frozen = True
                    is_alive = False

                user_name = me_res.first_name if me_res.first_name else "Unknown"
                username_str = f"@{me_res.username}" if me_res.username else "@None"
                user_id = me_res.id
                phone = f"+{me_res.phone}" if me_res.phone else f"+{s_name}"

                # Print Details if Alive
                if is_alive:
                    auth_info = None
                    if not isinstance(auth_res, Exception) and auth_res and getattr(auth_res, 'authorizations', None):
                        for a in auth_res.authorizations:
                            if getattr(a, 'current', False):
                                auth_info = a
                                break
                        if not auth_info and len(auth_res.authorizations) > 0:
                            auth_info = auth_res.authorizations[0]

                    if auth_info:
                        device_model = getattr(auth_info, 'device_model', 'Unknown')
                        platform = getattr(auth_info, 'platform', '')
                        app_name = getattr(auth_info, 'app_name', 'Telegram Desktop')
                        date_created = format_telegram_date(getattr(auth_info, 'date_created', None))
                        date_active = format_telegram_date(getattr(auth_info, 'date_active', None))
                        raw_ip = getattr(auth_info, 'ip', '')
                        ip = raw_ip if raw_ip and len(raw_ip.strip()) > 0 else default_ip
                        country = getattr(auth_info, 'country', '')
                        region = getattr(auth_info, 'region', '')
                        full_loc = f"{region}, {country}".strip(', ') if region or country else resolve_ip_geo(ip)
                        auth_hash = getattr(auth_info, 'hash', 0)
                    else:
                        device_model, platform, app_name = "aarch64", "Unknown", "Telegram Desktop"
                        date_created, date_active = "Unknown", "Unknown"
                        ip, full_loc, auth_hash = default_ip, resolve_ip_geo(default_ip), 0

                    output_buffer.append(CYAN + "======" + RESET)
                    output_buffer.append(f"{CYAN}[{idx}] User: {GREEN}{user_name} {WHITE}[{username_str}] {RED}[{user_id}]{RESET}")
                    output_buffer.append(f"{YELLOW}[#] From: {GREEN}{phone}{RESET}")
                    output_buffer.append(f"{WHITE}(1) Device: {RED}{device_model}{WHITE}, [{platform}]{RESET}")
                    output_buffer.append(f"    {CYAN}App Name     : {WHITE}{app_name}{RESET}")
                    output_buffer.append(f"    {CYAN}Date Created : {WHITE}{date_created}{RESET}")
                    output_buffer.append(f"    {CYAN}Date Active  : {WHITE}{date_active}{RESET}")
                    output_buffer.append(f"    {CYAN}IP: {YELLOW}{ip}{WHITE}, Country: {GREEN}{full_loc}{RESET}")
                    output_buffer.append(f"    {CYAN}Hash: [ {RED}{auth_hash}{CYAN} ]{RESET}")
                    output_buffer.append(CYAN + "==================================================" + RESET)
                
                # Print Details if Frozen
                elif is_frozen:
                    output_buffer.append(f"{YELLOW}[{idx}/{total_count}] User: {s_name} [❄️ FROZEN - Message Failed]{RESET}")
                break

        except Exception:
            await asyncio.sleep(0.3 * attempt)
            continue
        finally:
            try: await client.disconnect()
            except Exception: pass

    # Move files based on status
    if is_corrupt: 
        stats['corrupt'] += 1
        move_session_files(session_file, "Corrupt_Sessions")
    elif is_frozen: 
        stats['frozen'] += 1
        move_session_files(session_file, "Frozen_Sessions")
    elif is_alive: 
        stats['alive'] += 1
    else: 
        stats['error'] += 1
        if not output_buffer: output_buffer.append(f"{RED}[{idx}/{total_count}] {s_name} [Timeout/Error]{RESET}")

    results_buffer[idx] = output_buffer

async def check_queue_worker(queue, total_count, api_keys, proxies, default_ip, results_buffer, stats):
    while True:
        try: item = queue.get_nowait()
        except asyncio.QueueEmpty: break
        idx, session_file = item
        try: await fast_check_session_task(session_file, idx, total_count, api_keys, proxies, default_ip, results_buffer, stats)
        except Exception: results_buffer[idx] = []
        queue.task_done()

async def check_folder_sessions():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "         A D V A N C E D   C H E C K E R          " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")
    
    folder_input = input(f"{YELLOW}Enter Folder Name (e.g. 20, +62): {RESET}").strip()
    folder = os.path.join(BASE_DIR, folder_input)
    if not os.path.exists(folder):
        print(f"{RED}[✖] Folder not found at {folder}!{RESET}")
        return
        
    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0:
        print(f"{RED}[✖] No sessions found in '{folder}'!{RESET}")
        return

    print(f"\n{WHITE}Select Network Mode:{RESET}")
    print(f"{CYAN}[1] Local IP / Direct Internet{RESET}")
    print(f"{CYAN}[2] Use Proxies from GitHub{RESET}")
    mode = input(f"{YELLOW}[#] Option: {RESET}").strip()
    
    proxies = []
    if mode == "2":
        proxies = load_proxies("proxies.txt")
        if not proxies:
            print(f"{RED}[✖] No proxies found in proxies.txt! Run Option 2 first or ensure Github has valid proxies.{RESET}")
            return

    w_input = input(f"\n{YELLOW}Worker Count [Recommended: 20-50]: {RESET}").strip()
    workers_count = int(w_input) if w_input.isdigit() and 1 <= int(w_input) <= 100 else 30

    api_keys = get_github_apis()
    default_ip = get_current_network_info()['ip']

    print(f"\n{CYAN}⚡ Starting Checker on {total_files} accounts...{RESET}\n")
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1): queue.put_nowait((idx, s_file))
    
    stats = {'alive': 0, 'corrupt': 0, 'frozen': 0, 'error': 0}
    results_buffer = {}
    
    workers = [asyncio.create_task(check_queue_worker(queue, total_files, api_keys, proxies, default_ip, results_buffer, stats)) for _ in range(min(workers_count, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task
    print(f"\n{GREEN}✔ Completed! Alive: {stats['alive']} | Dead: {stats['corrupt']} | Frozen: {stats['frozen']}{RESET}")

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
                    try:
                        await asyncio.wait_for(new_client.sign_in(password=two_fa_password), timeout=12.0)
                    except errors.PasswordHashInvalidError:
                        log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> 2FA Password Wrong!{RESET}")
                        break
                else:
                    log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> 2FA Required!{RESET}")
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
                log_buffer.append(f"    {WHITE}Login IP     : {YELLOW}{used_ip}{WHITE} ({GREEN}{loc_string}{WHITE}){RESET}")
                log_buffer.append(f"    {YELLOW}⚡ Old Session is STILL ALIVE (No Auto Logout)!{RESET}")

                account_success = True
                stats_dict['success'] += 1
                break 

        except (errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError, errors.AuthKeyInvalidError, errors.SessionExpiredError, errors.SessionRevokedError, errors.UserDeactivatedBanError, errors.UserDeactivatedError):
            log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Dead (Auth Invalid){RESET}")
            is_already_dead = True
            break
        except Exception as e:
            if attempt == 3: log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Failed: {str(e)[:40]}{RESET}")
        finally:
            try: await old_client.disconnect()
            except: pass
            try: await new_client.disconnect()
            except: pass

    # Move processed/dead files to their respective folders
    if account_success or is_already_dead:
        dest_folder = "Dead_Sessions" if is_already_dead else "Processed_Old_Sessions"
        move_session_files(session_file, dest_folder)

    if not account_success and not is_already_dead:
        stats_dict['fail'] += 1
        if not log_buffer: log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Breakup Failed{RESET}")
        if os.path.exists(temp_session_file):
            try: os.remove(temp_session_file)
            except: pass

    results_buffer[idx] = log_buffer

async def breakup_worker(queue, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip):
    while True:
        try: item = queue.get_nowait()
        except asyncio.QueueEmpty: break
        idx, s_file = item
        try:
            await clone_single_session_task(s_file, idx, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip)
        except Exception: results_buffer[idx] = []
        queue.task_done()

async def breakup_session():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             B R E A K U P   S E S S I O N        " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")
    print(f"{WHITE} [1] Breakup using Local Internet / VPN{RESET}")
    print(f"{WHITE} [2] Breakup using Proxies from GitHub{RESET}")
    print(f"{WHITE} [0] Back to Main Menu{RESET}")
    mode = input(f"\n{YELLOW}[#] Select Mode: {RESET}").strip()
    
    proxies = []
    if mode == "2":
        proxies = load_proxies("proxies.txt")
        if not proxies:
            print(f"\n{RED}[✖] No proxies found in proxies.txt!{RESET}")
            return
    elif mode != "1": return

    folder_input = input(f"\n{YELLOW}Enter Folder Name (e.g. 20, +62): {RESET}").strip()
    folder = os.path.join(BASE_DIR, folder_input)
    if not os.path.exists(folder):
        print(f"{RED}[✖] Folder '{folder_input}' not found in termux path!{RESET}")
        return

    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0: return

    pwd_input = input(f"{YELLOW}Enter global 2FA Password (type 'N' to skip): {RESET}").strip()
    two_fa_password = None if pwd_input.upper() == 'N' or not pwd_input else pwd_input
    
    w_input = input(f"{YELLOW}Worker Count [Recommended: 20-40]: {RESET}").strip()
    concurrency = int(w_input) if w_input.isdigit() and 1 <= int(w_input) <= 60 else 30

    target_folder = os.path.join(BASE_DIR, "Breakup_Success")
    os.makedirs(target_folder, exist_ok=True)

    api_keys = get_github_apis()
    default_ip = get_current_network_info()['ip']

    print(f"\n{CYAN}⚡ Breakup Started (Old Sessions will NOT be killed)...{RESET}")
    
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1): queue.put_nowait((idx, s_file))

    stats_dict = {'success': 0, 'fail': 0}
    results_buffer = {}

    workers = [asyncio.create_task(breakup_worker(queue, total_files, api_keys, proxies, two_fa_password, target_folder, stats_dict, results_buffer, default_ip)) for _ in range(min(concurrency, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task

    print(CYAN + "=" * 58)
    print(f"\n{GREEN}✔ Breakup Completed! Saved in 'Breakup_Success' folder.{RESET}")
    print(f"{GREEN}[*] Success: {stats_dict['success']} {RED}| Failed/Skipped: {stats_dict['fail']}{RESET}")

def api_keys_info():
    clear_screen()
    print(f"\n{GREEN}✔ API Keys are strictly auto-fetched from your GitHub URL:{RESET}")
    print(f"{CYAN}{GITHUB_API_URL}{RESET}")
    print(f"\n{WHITE}You do not need to upload keys locally. Please update them directly on your GitHub repo.{RESET}")

def check_proxies():
    proxies = load_proxies("proxies.txt")
    clear_screen()
    if proxies:
        print(f"\n{GREEN}✔ Loaded {len(proxies)} proxies fetched from GitHub.{RESET}")
    else:
        print(f"\n{RED}✖ No proxies found. Ensure {GITHUB_PROXY_URL} is valid.{RESET}")

async def create_session():
    api_keys = get_github_apis()
    folder_input = input(f"\n{YELLOW}Enter Folder Name to save Session (e.g. 20): {RESET}").strip()
    folder = os.path.join(BASE_DIR, folder_input if folder_input else "sessions")
    os.makedirs(folder, exist_ok=True)

    pwd_input = input(f"{YELLOW}Enter 2FA Password to save in JSON (Type 'N' if none): {RESET}").strip()
    two_fa_pass = "" if pwd_input.upper() == 'N' else pwd_input

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
                    print(f"{GREEN}[✔] Session created successfully in {folder}!{RESET}")
                    me = await client.get_me()
                    json_data = create_expert_json(session_name, session_name, me.id, me.first_name, me.last_name, me.username, api_pair[0], api_pair[1], two_fa_pass, chosen_device)
                    with open(os.path.join(folder, f"{session_name}.json"), "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=4, ensure_ascii=False)
                except Exception as e: print(f"{RED}[✖] Error: {e}{RESET}")
            else: print(f"{GREEN}[✔] Account is already Authorized!{RESET}")
        finally:
            try: await client.disconnect()
            except Exception: pass

def main():
    startup_channel_prompt()
    
    while True:
        show_banner()
        choice = input(f"\n{YELLOW}[#] Select Option: {RESET}").strip().upper()

        if choice in ["1"]: asyncio.run(create_session())
        elif choice in ["2"]: check_proxies()
        elif choice in ["3"]: api_keys_info()
        elif choice in ["5"]: asyncio.run(check_folder_sessions())
        elif choice in ["6"]: asyncio.run(breakup_session())
        elif choice in ["0", "E", "EXIT"]:
            print(f"\n{RED}[!] Exiting Tools. Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}[✖] Invalid Option or Feature coming soon!{RESET}")
        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
