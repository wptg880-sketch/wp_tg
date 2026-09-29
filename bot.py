#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  C H E C K E R   V 6  +  S E S S I O N  →  T D A T A          ║
║  Premium Edition  ·  Offline Engine  ·  Ultra Fast            ║
╚══════════════════════════════════════════════════════════════╝
"""

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
import time
import threading
import zipfile
import sqlite3
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ═══════════════════════════════════════════════════════════════
#                PYTHON 3.13+ COMPATIBILITY FIX
# ═══════════════════════════════════════════════════════════════
if 'imghdr' not in sys.modules:
    imghdr_mock = types.ModuleType('imghdr')
    imghdr_mock.what = lambda file, h=None: 'jpeg'
    sys.modules['imghdr'] = imghdr_mock

# ═══════════════════════════════════════════════════════════════
#                AUTO-INSTALLER FOR LIBRARIES
# ═══════════════════════════════════════════════════════════════
try:
    import telethon
    import python_socks
    from colorama import Fore, Style, init
    if telethon.__version__ < '1.30.0':
        raise ImportError("Telethon too old")
except ImportError:
    print("\n[!] Installing required libraries (Telethon, Python-Socks, Colorama, opentele-ng)...")
    os.system(f"{sys.executable} -m pip install --upgrade telethon python-socks colorama opentele-ng")
    print("\n[✔] Setup complete! Restarting script...\n")
    os.execv(sys.executable, ['python'] + sys.argv)

# ═══════════════════════════════════════════════════════════════
#                OPENTELE IMPORTS (for TData)
# ═══════════════════════════════════════════════════════════════
try:
    from opentele.td import TDesktop, Account, AuthKey
    from opentele.api import API
except ImportError:
    print("\n[!] Installing opentele-ng for TData converter...")
    os.system(f"{sys.executable} -m pip install --upgrade opentele-ng")
    print("\n[✔] Setup complete! Restarting script...\n")
    os.execv(sys.executable, ['python'] + sys.argv)

TD_DcId = None
TD_AuthKeyType = None
try:
    from opentele.td.configs import DcId as TD_DcId, AuthKeyType as TD_AuthKeyType
except ImportError:
    try:
        from opentele.td import DcId as TD_DcId
    except ImportError:
        pass
    try:
        from opentele.td.auth import AuthKeyType as TD_AuthKeyType
    except ImportError:
        pass

from telethon import TelegramClient, errors, functions
from telethon.network import ConnectionTcpIntermediate, ConnectionTcpAbridged

# Disable background logging
logging.getLogger('telethon').setLevel(logging.CRITICAL)
logging.getLogger('opentele').setLevel(logging.CRITICAL)
init(autoreset=True)

# ═══════════════════════════════════════════════════════════════
#                  GITHUB URLs (Proxies & APIs)
# ═══════════════════════════════════════════════════════════════
GITHUB_PROXY_URL = "https://raw.githubusercontent.com/wptg880-sketch/wp_tg/main/proxies.txt"
GITHUB_API_URL = "https://raw.githubusercontent.com/wptg880-sketch/wp_tg/main/api_keys.txt"

DEFAULT_API_ID = 25762761
DEFAULT_API_HASH = "f6712ac15fa56c713451eede724261eb"

# ═══════════════════════════════════════════════════════════════
#              BASE DIRECTORY FOR PHONE STORAGE
# ═══════════════════════════════════════════════════════════════
BASE_DIR = "/storage/emulated/0/termux"

try:
    os.makedirs(BASE_DIR, exist_ok=True)
except PermissionError:
    print(f"\n\033[1;31m[!] PERMISSION ERROR: Please run 'termux-setup-storage' first!\033[0m\n")
    BASE_DIR = "termux_sessions"
    os.makedirs(BASE_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
#                    AUTO NAMES & DEVICES
# ═══════════════════════════════════════════════════════════════
AUTO_NAMES_LIST = [
    "RK", "ER", "RJ", "JEB", "Alex", "Sam", "Max", "Leo", "Ray", "Tom", "Bob", "Tim", "Jay", "Roy",
    "Jon", "Dan", "Eli", "Ian", "Mac", "Abe", "Ben", "Cal", "Hal", "Sal", "Vic", "Zak", "Kai", "Jax",
    "Fox", "Rex", "Ash", "Cid", "Dax", "Gus", "Kip", "Lex", "Ned", "Paz", "Taj", "Van", "Wes", "Zed",
    "John", "David", "Michael", "James", "Robert", "William", "Mary", "Patricia", "Jennifer", "Linda"
]

DESKTOP_DEVICES = [
    {"device_model": "Windows 10 x64", "system_version": "10.0.19045", "app_version": "4.8.4 x64"},
    {"device_model": "Windows 11 x64", "system_version": "10.0.22621", "app_version": "4.11.2 x64"},
    {"device_model": "Ubuntu 22.04 LTS", "system_version": "Linux 5.15", "app_version": "4.9.1 x64"},
    {"device_model": "MacBook Pro M1", "system_version": "macOS 13.5", "app_version": "4.10.0 arm64"},
    {"device_model": "Windows 8.1 x64", "system_version": "6.3.9600", "app_version": "4.7.1 x64"}
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

# ═══════════════════════════════════════════════════════════════
#                    COLOR PALETTE
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
#                    GITHUB FETCHERS
# ═══════════════════════════════════════════════════════════════
def fetch_online_proxies():
    if not GITHUB_PROXY_URL: return
    try:
        req = urllib.request.Request(GITHUB_PROXY_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            proxy_data = resp.read().decode('utf-8')
            if proxy_data.strip():
                with open("proxies.txt", "w", encoding="utf-8") as f:
                    f.write(proxy_data)
    except Exception:
        pass

def get_github_apis():
    api_list = []
    if GITHUB_API_URL:
        try:
            req = urllib.request.Request(GITHUB_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = resp.read().decode('utf-8')
                for line in data.split('\n'):
                    match = re.search(r'(\d{5,10})\s*[:\s,\t]+\s*([a-fA-F0-9]{32})', line)
                    if match:
                        pair = (int(match.group(1)), match.group(2))
                        if pair not in api_list:
                            api_list.append(pair)
        except Exception:
            pass
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
        elif sys.platform == 'win32':
            os.system(f"start {url}")
        elif sys.platform == 'darwin':
            os.system(f"open {url}")
        else:
            webbrowser.open(url)
    except Exception:
        pass

    fetch_online_proxies()
    input(f"\n{YELLOW} [?] Press ENTER to continue to Main Menu... {RESET}")

# ═══════════════════════════════════════════════════════════════
#                    LOCATION & NETWORK
# ═══════════════════════════════════════════════════════════════
def resolve_ip_geo(ip):
    if not ip or ip.lower() in ['unknown', 'localhost', '127.0.0.1']:
        return "Unknown"
    if ip in GEO_CACHE:
        return GEO_CACHE[ip]
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=status,country,city",
                                     headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('status') == 'success':
                loc = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
                if loc:
                    GEO_CACHE[ip] = loc
                    return loc
    except Exception:
        pass
    return "Unknown"

def get_current_network_info():
    try:
        req = urllib.request.Request("http://ip-api.com/json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            isp = data.get('isp', '')
            isp_short = isp[:15] + '..' if len(isp) > 15 else isp
            loc = f"{data.get('city', '')}, {data.get('country', '')}".strip(', ')
            return {
                'ip': data.get('query', 'Unknown'),
                'location': loc if loc else "Unknown",
                'isp': isp_short,
                'status': True
            }
    except Exception:
        return {'ip': 'Local IP', 'location': 'Local Network', 'isp': 'Direct', 'status': False}

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
    print(f"{CYAN} [2] {GREEN}📦 {MAGENTA}Session to TData (Offline){RESET}")
    print(f"{CYAN} [3] {GREEN}🌐 {GREEN}Check Extracted Proxies{RESET}")
    print(f"{CYAN} [4] {GREEN}🔑 {MAGENTA}API Keys (Auto Fetched from GitHub){RESET}")
    print(f"{CYAN} [5] {GREEN}👥 {BLUE}Join Public Channel / Group{RESET}")
    print(f"{CYAN} [6] {GREEN}🔰 {GREEN}Check Folder Sessions (Advanced Mode){RESET}")
    print(f"{CYAN} [7] {GREEN}💔 {YELLOW}Breakup Session (Fast Mode){RESET}")
    print(f"{CYAN} [8] {GREEN}🔐 {MAGENTA}2FA Manager (Change/Disable/Reset){RESET}")
    print(f"{CYAN} [9] {GREEN}🔥 {RED}Kill Session (Self Logout){RESET}")
    print(f"{CYAN} [0] {GREEN}🚨 {RED}Exit Tools{RESET}")
    print(CYAN + "════════════════════════════════════════════════════" + RESET)
    print(f"{WHITE}[*] Base Storage Path: {GREEN}{BASE_DIR}{RESET}")

# ═══════════════════════════════════════════════════════════════
#                         UTILS
# ═══════════════════════════════════════════════════════════════
def load_proxies(file_path="proxies.txt"):
    if not os.path.exists(file_path):
        return []
    proxy_list = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            geo_tag = ""
            if "#" in line:
                line, geo_tag = line.split("#", 1)
            proto = "socks5"
            if "://" in line:
                proto, line = line.split("://", 1)

            if "@" in line:
                auth, ip_port = line.split("@", 1)
                user, pwd = auth.split(":", 1) if ":" in auth else (auth, "")
                if ":" in ip_port:
                    ip, port = ip_port.split(":", 1)
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port),
                                       'user': user, 'pwd': pwd, 'geo': loc})
            else:
                parts = line.split(":")
                if len(parts) >= 4:
                    ip, port, user, pwd = parts[0], int(parts[1]), parts[2], parts[3]
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port),
                                       'user': user, 'pwd': pwd, 'geo': loc})
                elif len(parts) == 2:
                    ip, port = parts[0], int(parts[1])
                    loc = geo_tag.strip() if geo_tag.strip() and geo_tag.strip() != "Unknown" else resolve_ip_geo(ip)
                    proxy_list.append({'proto': proto.lower(), 'ip': ip, 'port': int(port),
                                       'user': None, 'pwd': None, 'geo': loc})
    return proxy_list

def move_session_files(session_file_path, target_dir_name):
    target_dir = os.path.join(BASE_DIR, target_dir_name)
    os.makedirs(target_dir, exist_ok=True)
    try:
        dest_path = os.path.join(target_dir, os.path.basename(session_file_path))
        if os.path.exists(dest_path):
            os.remove(dest_path)
        shutil.move(session_file_path, dest_path)

        json_file = session_file_path.replace('.session', '.json')
        if os.path.exists(json_file):
            j_dest = os.path.join(target_dir, os.path.basename(json_file))
            if os.path.exists(j_dest):
                os.remove(j_dest)
            shutil.move(json_file, j_dest)
    except Exception:
        pass

def update_json_2fa(session_file, new_2fa):
    json_file = session_file.replace('.session', '.json')
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['twoFA'] = new_2fa
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
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

    dm = device_config['device_model'] if device_config else "Windows PC"
    sv = device_config['system_version'] if device_config else "Windows 10"
    av = device_config['app_version'] if device_config else "4.8.4"

    return TelegramClient(
        session_base, api_pair[0], api_pair[1],
        device_model=dm, system_version=sv, app_version=av,
        lang_code="en", system_lang_code="en-US",
        proxy=proxy_dict,
        connection=ConnectionTcpAbridged if proxy_dict else ConnectionTcpIntermediate,
        timeout=timeout, auto_reconnect=False, connection_retries=1, retry_delay=1,
        flood_sleep_threshold=20
    )

def format_telegram_date(dt):
    if not dt:
        return "Unknown"
    tz_bd = timezone(timedelta(hours=6))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz_bd).strftime("%Y-%m-%d %H:%M:%S UTC+06:00")

def create_expert_json(session_name, phone, user_id, first_name, last_name, username,
                       api_id, api_hash, two_fa, device_config=None, proxy_info=None):
    current_time = datetime.now(timezone(timedelta(hours=7))).isoformat()
    dev_model = device_config['device_model'] if device_config else "Windows PC"
    app_ver = device_config['app_version'] if device_config else "4.8.4"
    sys_ver = device_config['system_version'] if device_config else "Windows 10"

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
        output_buffer = results_buffer.pop(next_idx)
        for line in output_buffer:
            print(line)
        await asyncio.sleep(0.02)
        next_idx += 1

# ═══════════════════════════════════════════════════════════════
#        [2] SESSION TO TDATA — OFFLINE CONVERTER
# ═══════════════════════════════════════════════════════════════

TD_MAX_WORKERS = 50

TD_DC_IP_MAP = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}

# TD-specific colors
TD_R     = Style.RESET_ALL
TD_B     = Style.BRIGHT
TD_CYAN  = Fore.LIGHTCYAN_EX
TD_MINT  = Fore.LIGHTGREEN_EX
TD_ROSE  = Fore.LIGHTRED_EX
TD_GOLD  = Fore.LIGHTYELLOW_EX
TD_LILAC = Fore.LIGHTMAGENTA_EX
TD_WHITE = Fore.LIGHTWHITE_EX
TD_GRAY  = Fore.LIGHTBLACK_EX

TD_ANSI_RE = re.compile(r'\033\[[0-9;]*m')

def td_vlen(s):
    return len(TD_ANSI_RE.sub('', s))

def td_pad(s, w):
    return s + ' ' * max(0, w - td_vlen(s))

def td_center(s, w):
    v = td_vlen(s)
    if v >= w:
        return s
    left = (w - v) // 2
    right = w - v - left
    return ' ' * left + s + ' ' * right

def td_get_dc_id(i):
    if TD_DcId is None:
        return i
    for a in (f'_{i}', f'Production{i}', str(i)):
        if hasattr(TD_DcId, a):
            try:
                return getattr(TD_DcId, a)
            except Exception:
                pass
    try:
        return TD_DcId(i)
    except Exception:
        return i

def td_safe_name(path):
    n = os.path.splitext(os.path.basename(path))[0]
    c = n.replace("+", "").replace(" ", "")
    if c.isdigit() and 7 <= len(c) <= 15:
        return "+" + c
    return n

def td_read_session(path):
    try:
        con = sqlite3.connect(path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        if not cur.fetchone():
            con.close()
            return None, "no-table"
        cur.execute("PRAGMA table_info(sessions)")
        cols = [c[1] for c in cur.fetchall()]
        if 'auth_key' not in cols or 'dc_id' not in cols:
            con.close()
            return None, "no-cols"
        cur.execute("SELECT dc_id, auth_key FROM sessions WHERE dc_id > 0 ORDER BY dc_id ASC LIMIT 1")
        row = cur.fetchone()
        con.close()
        if not row or not row[1]:
            return None, "empty"
        dc_id = int(row[0])
        auth_key = bytes(row[1])
        if dc_id not in TD_DC_IP_MAP:
            return None, f"dc-{dc_id}"
        if len(auth_key) != 256:
            return None, "bad-key"
        return (dc_id, auth_key), "OK"
    except Exception:
        return None, "sql-error"

def td_build_offline(dc_id, auth_key_bytes, tdata_dir):
    os.makedirs(tdata_dir, exist_ok=True)
    try:
        tdesk = TDesktop()
    except Exception:
        return False, "engine"

    dc_enum = td_get_dc_id(dc_id)

    # AuthKey
    ak_type = TD_AuthKeyType.ReadFromFile if TD_AuthKeyType is not None else None
    mtp_key = None
    if ak_type is not None:
        try:
            mtp_key = AuthKey(key=auth_key_bytes, type=ak_type, dcId=dc_enum)
        except Exception:
            pass
    if mtp_key is None:
        for attempt in (
            lambda: AuthKey(key=auth_key_bytes, dcId=dc_enum),
            lambda: AuthKey(key=auth_key_bytes),
            lambda: AuthKey(auth_key_bytes),
        ):
            try:
                mtp_key = attempt()
            except Exception:
                continue
            if mtp_key:
                break
    if mtp_key is None:
        return False, "authkey"

    try:
        setattr(mtp_key, '_AuthKey__dcId', dc_enum)
    except Exception:
        pass

    # Account
    acc = None
    for kw in (
        {'owner': tdesk, 'api': API.TelegramDesktop},
        {'owner': tdesk},
        {'api': API.TelegramDesktop},
        {}
    ):
        try:
            acc = Account(**kw)
            break
        except TypeError:
            continue
        except Exception:
            continue
    if acc is None:
        return False, "account"

    # LocalKey
    local_key = None
    for gen in ('RandomGenerate', 'Generate', 'CreateLocalKey', 'Random'):
        fn = getattr(AuthKey, gen, None)
        if callable(fn):
            try:
                local_key = fn()
            except Exception:
                continue
            if local_key:
                break
    if local_key is None:
        try:
            local_key = AuthKey(os.urandom(256))
        except Exception:
            return False, "localkey"

    # Set private attributes
    try:
        setattr(acc, '_Account__isLoaded', True)
        setattr(acc, '_Account__isAuthorized', True)
        setattr(acc, '_Account__UserId', 1)
        setattr(acc, '_Account__MainDcId', dc_enum)
        setattr(acc, '_Account__mtpKeys', [mtp_key])
        setattr(acc, '_Account__mtpKeysToDestroy', [])
        setattr(acc, '_Account__authKey', mtp_key)
        setattr(acc, '_Account__localKey', local_key)
        setattr(acc, '_Account__owner', tdesk)
        if hasattr(acc, '_local'):
            try:
                setattr(acc._local, '_StorageAccount__localKey', local_key)
            except Exception:
                pass
    except Exception:
        return False, "attrs"

    # Attach
    try:
        tdesk._TDesktop__accounts = [acc]
    except Exception:
        return False, "attach"
    try:
        tdesk._TDesktop__mainAccount = acc
    except Exception:
        pass

    # Save
    try:
        tdesk.SaveTData(tdata_dir)
    except Exception:
        return False, "save"

    # Flatten nested
    key_path = os.path.join(tdata_dir, "key_datas")
    if not os.path.exists(key_path):
        nested = os.path.join(tdata_dir, "tdata")
        if os.path.exists(os.path.join(nested, "key_datas")):
            for item in os.listdir(nested):
                src = os.path.join(nested, item)
                dst = os.path.join(tdata_dir, item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst, ignore_errors=True)
                    else:
                        try:
                            os.remove(dst)
                        except Exception:
                            pass
                shutil.move(src, dst)
            shutil.rmtree(nested, ignore_errors=True)
            key_path = os.path.join(tdata_dir, "key_datas")

    if not os.path.exists(key_path):
        return False, "broken"

    files = os.listdir(tdata_dir)
    has_map = any(len(f) == 17 and f.endswith('s') and f != 'key_datas' for f in files)
    if not has_map:
        return False, "no-map"

    return True, "ok"

def td_create_zip_inside(folder_path, zip_name):
    final_zip = os.path.join(folder_path, f"{zip_name}.zip")
    if os.path.exists(final_zip):
        try:
            os.remove(final_zip)
        except Exception:
            pass

    tmp_zip = os.path.join(os.path.dirname(folder_path), f"__tmp_{int(time.time()*1000)}__.zip")
    try:
        with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            base_name = os.path.basename(folder_path)
            for root, dirs, fnames in os.walk(folder_path):
                for fname in fnames:
                    if fname.endswith('.zip'):
                        continue
                    full = os.path.join(root, fname)
                    rel = os.path.relpath(full, folder_path)
                    arc = os.path.join(base_name, rel)
                    try:
                        zf.write(full, arc)
                    except Exception:
                        pass
        shutil.move(tmp_zip, final_zip)
        return final_zip
    except Exception:
        if os.path.exists(tmp_zip):
            try:
                os.remove(tmp_zip)
            except Exception:
                pass
        return None


class TDDashboard:
    """Serial line printer — clean, no messy cursor movements."""

    def __init__(self, total, folder, dest):
        self.total = total
        self.folder = folder
        self.dest = dest
        self.ok = 0
        self.fail = 0
        self.done = 0
        self.start = time.time()
        self.reasons = {}
        self.lock = threading.Lock()

    def _short(self, r):
        return {
            "authkey": "invalid authkey",
            "account": "account init",
            "localkey": "localkey fail",
            "attach": "attach failed",
            "save": "save failed",
            "broken": "incomplete",
            "no-map": "no map file",
            "no-table": "no table",
            "no-cols": "missing cols",
            "empty": "empty session",
            "sql-error": "db error",
            "engine": "engine error",
            "bad-key": "corrupt key",
        }.get(r, f"bad dc ({r[3:]})" if r.startswith("dc-") else r)

    def update(self, success, reason, phone):
        with self.lock:
            self.done += 1
            idx = self.done
            total = self.total
            num_width = len(str(total))

            if success:
                self.ok += 1
                line = (
                    f"  {TD_MINT}[{idx:>{num_width}}/{total}]{TD_R}"
                    f"  {TD_MINT}✔{TD_R}"
                    f"  {TD_WHITE}{phone:<18}{TD_R}"
                    f"  {TD_MINT}ready{TD_R}"
                )
            else:
                self.fail += 1
                self.reasons[reason] = self.reasons.get(reason, 0) + 1
                short = self._short(reason)
                line = (
                    f"  {TD_ROSE}[{idx:>{num_width}}/{total}]{TD_R}"
                    f"  {TD_ROSE}✖{TD_R}"
                    f"  {TD_WHITE}{phone:<18}{TD_R}"
                    f"  {TD_ROSE}{short}{TD_R}"
                )

            print(line, flush=True)

    def finish(self):
        pass

    def elapsed(self):
        return time.time() - self.start


TD_LOGO = [
    "████████╗ █████╗  ██████╗████████╗██╗██╗   ██╗███████╗",
    "╚══██╔══╝██╔══██╗██╔════╝╚══██╔══╝██║██║   ██║██╔════╝",
    "   ██║   ███████║██║        ██║   ██║██║   ██║█████╗  ",
    "   ██║   ██╔══██║██║        ██║   ██║╚██╗ ██╔╝██╔══╝  ",
    "   ██║   ██║  ██║╚██████╗   ██║   ██║ ╚████╔╝ ███████╗",
    "   ╚═╝   ╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝",
]

def td_show_header():
    clear_screen()
    print()
    for line in TD_LOGO:
        print(f"    {TD_CYAN}{TD_B}{line}{TD_R}")
    print()
    print(f"    {TD_GRAY}session  →  tdata  converter{TD_R}")
    print(f"    {TD_LILAC}◆  premium  edition  ◆{TD_R}")
    print()

def td_show_info(folder, total, threads, dest):
    print(f"    {TD_GRAY}folder{TD_R}      {TD_WHITE}{folder}{TD_R}")
    print(f"    {TD_GRAY}sessions{TD_R}    {TD_WHITE}{total}{TD_R}")
    print(f"    {TD_GRAY}threads{TD_R}     {TD_WHITE}{threads}{TD_R}   {TD_GRAY}·{TD_R}   {TD_LILAC}offline{TD_R}")
    print(f"    {TD_GRAY}output{TD_R}      {TD_GRAY}{dest}{TD_R}")
    print()
    print(f"    {TD_GRAY}{'·' * 58}{TD_R}")
    print()

def td_process_one(session_file, dest, dashboard):
    phone = td_safe_name(session_file)
    phone_dir = os.path.join(dest, phone)
    tdata_dir = os.path.join(phone_dir, "tdata")

    if os.path.exists(phone_dir):
        try:
            shutil.rmtree(phone_dir)
        except Exception:
            pass

    data, msg = td_read_session(session_file)
    if not data:
        dashboard.update(False, msg, phone)
        return

    dc_id, auth_key = data
    success, reason = td_build_offline(dc_id, auth_key, tdata_dir)
    dashboard.update(success, reason, phone)


def td_show_summary(dash, elapsed, total):
    print()
    W = 44
    print(f"  {TD_CYAN}╭{'─' * W}╮{TD_R}")
    print(f"  {TD_CYAN}│{TD_R}{td_center(f'{TD_MINT}{TD_B}✓ COMPLETED{TD_R}', W)}{TD_CYAN}│{TD_R}")
    print(f"  {TD_CYAN}│{TD_R}{' ' * W}{TD_CYAN}│{TD_R}")

    l1 = f"  {TD_MINT}✓{TD_R} {TD_WHITE}{dash.ok:>4}{TD_R} {TD_GRAY}converted{TD_R}"
    l2 = f"  {TD_ROSE}✗{TD_R} {TD_WHITE}{dash.fail:>4}{TD_R} {TD_GRAY}failed{TD_R}"
    l3 = f"  {TD_CYAN}⏱{TD_R} {TD_WHITE}{elapsed:>5.1f}s{TD_R} {TD_GRAY}total{TD_R}"
    spd = total / elapsed if elapsed else 0
    l4 = f"  {TD_GOLD}⚡{TD_R} {TD_WHITE}{spd:>5.1f}/s{TD_R} {TD_GRAY}speed{TD_R}"

    print(f"  {TD_CYAN}│{TD_R}" + td_pad(l1, W // 2) + td_pad(l2, W - W // 2) + f"{TD_CYAN}│{TD_R}")
    print(f"  {TD_CYAN}│{TD_R}" + td_pad(l3, W // 2) + td_pad(l4, W - W // 2) + f"{TD_CYAN}│{TD_R}")
    print(f"  {TD_CYAN}╰{'─' * W}╯{TD_R}")

def td_show_failures(dash):
    if not dash.reasons:
        return
    print()
    print(f"    {TD_GRAY}failure breakdown{TD_R}")
    print()
    mx = max(dash.reasons.values())
    for r, c in sorted(dash.reasons.items(), key=lambda x: -x[1]):
        bar = f"{TD_ROSE}{'▬' * int(c / mx * 20)}{TD_R}"
        short = TDDashboard._short(None, r)
        print(f"      {TD_GRAY}·{TD_R}  {TD_WHITE}{short:<18}{TD_R}  {bar}  {TD_WHITE}{c}{TD_R}")


def run_session_to_tdata():
    """Option 2 — Session to TData offline converter (serial output)."""
    td_show_header()

    base = BASE_DIR
    os.makedirs(base, exist_ok=True)

    folder = input(f"    {TD_GOLD}▸{TD_R}  {TD_WHITE}session folder{TD_R}  {TD_GRAY}:{TD_R}  ").strip()
    target = os.path.join(base, folder)
    print()

    if not os.path.exists(target):
        print(f"    {TD_ROSE}✗{TD_R}  {TD_WHITE}folder not found{TD_R}   {TD_GRAY}{target}{TD_R}\n")
        return

    files = sorted(glob.glob(os.path.join(target, "*.session")))
    if not files:
        print(f"    {TD_ROSE}✗{TD_R}  {TD_WHITE}no .session files{TD_R}\n")
        return

    dest = os.path.join(base, f"__temp_{folder}_tdata__")
    if os.path.exists(dest):
        try:
            shutil.rmtree(dest)
        except Exception:
            pass
    os.makedirs(dest, exist_ok=True)

    td_show_info(folder, len(files), TD_MAX_WORKERS, f"{folder}(?) TDATA")

    # Header row
    print(f"    {TD_GRAY}{'─' * 58}{TD_R}")
    print(f"    {TD_GRAY}  {'#':<9}  {'':<2}  {'account':<18}  status{TD_R}")
    print(f"    {TD_GRAY}{'─' * 58}{TD_R}")

    dash = TDDashboard(len(files), folder, dest)

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        with ThreadPoolExecutor(max_workers=TD_MAX_WORKERS) as ex:
            futures = [ex.submit(td_process_one, f, dest, dash) for f in files]
            for _ in as_completed(futures):
                pass
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()
        print(f"\n    {TD_GOLD}⚠{TD_R}  {TD_GRAY}interrupted{TD_R}\n")
        return
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    dash.finish()
    elapsed = dash.elapsed()

    print(f"    {TD_GRAY}{'─' * 58}{TD_R}")
    print()

    td_show_summary(dash, elapsed, len(files))
    td_show_failures(dash)

    # Rename folder
    final_dir_name = f"{folder}({dash.ok}) TDATA"
    final_dir = os.path.join(base, final_dir_name)

    if os.path.exists(final_dir) and final_dir != dest:
        try:
            shutil.rmtree(final_dir)
        except Exception:
            pass

    try:
        if os.path.exists(dest):
            os.rename(dest, final_dir)
    except Exception:
        try:
            shutil.move(dest, final_dir)
        except Exception:
            final_dir = dest

    if dash.ok > 0:
        print()
        print(f"    {TD_GRAY}packaging{TD_R}")
        print()

        zip_name = f"T ACTIVE ({dash.ok})"
        print(f"      {TD_GOLD}▸{TD_R}  {TD_GRAY}creating{TD_R}  {TD_WHITE}{zip_name}.zip{TD_R}   {TD_GRAY}...{TD_R}")

        zt = time.time()
        final_zip = td_create_zip_inside(final_dir, zip_name)
        zt = time.time() - zt

        if final_zip and os.path.exists(final_zip):
            size_mb = os.path.getsize(final_zip) / (1024 * 1024)
            print()
            W = 44
            print(f"  {TD_LILAC}╭{'─' * W}╮{TD_R}")
            print(f"  {TD_LILAC}│{TD_R}{td_center(f'{TD_LILAC}{TD_B}◆ PACKAGE READY{TD_R}', W)}{TD_LILAC}│{TD_R}")
            print(f"  {TD_LILAC}│{TD_R}{' ' * W}{TD_LILAC}│{TD_R}")
            print(f"  {TD_LILAC}│{TD_R}" + td_pad(f" {TD_GRAY}file{TD_R}   {TD_WHITE}{TD_B}{zip_name}.zip{TD_R}", W) + f"{TD_LILAC}│{TD_R}")
            print(f"  {TD_LILAC}│{TD_R}" + td_pad(f" {TD_GRAY}size{TD_R}   {TD_WHITE}{size_mb:.2f} MB{TD_R}", W) + f"{TD_LILAC}│{TD_R}")
            print(f"  {TD_LILAC}│{TD_R}" + td_pad(f" {TD_GRAY}time{TD_R}   {TD_WHITE}{zt:.1f}s{TD_R}", W) + f"{TD_LILAC}│{TD_R}")
            print(f"  {TD_LILAC}│{TD_R}" + td_pad(f" {TD_GRAY}folder{TD_R} {TD_WHITE}{final_dir_name[:24]}{TD_R}", W) + f"{TD_LILAC}│{TD_R}")
            print(f"  {TD_LILAC}│{TD_R}{' ' * W}{TD_LILAC}│{TD_R}")
            sp = final_zip if len(final_zip) <= W - 8 else "..." + final_zip[-(W - 11):]
            print(f"  {TD_LILAC}│{TD_R}" + td_pad(f" {TD_GRAY}path{TD_R}   {TD_MINT}{sp}{TD_R}", W) + f"{TD_LILAC}│{TD_R}")
            print(f"  {TD_LILAC}╰{'─' * W}╯{TD_R}")
            print()
            print(f"    {TD_MINT}✓{TD_R}  {TD_WHITE}done{TD_R}")
            print()
        else:
            print(f"\n    {TD_ROSE}✗{TD_R}  {TD_WHITE}zip creation failed{TD_R}\n")
    else:
        print()
        print(f"    {TD_ROSE}✗{TD_R}  {TD_WHITE}no tdata was created{TD_R}\n")

# ═══════════════════════════════════════════════════════════════
#              [6] ADVANCED CHECK FOLDER SESSIONS
# ═══════════════════════════════════════════════════════════════
async def fast_check_session_task(session_file, idx, total_count, api_keys, proxies,
                                  default_ip, results_buffer, stats):
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

            me_res, auth_res = await asyncio.gather(
                client.get_me(),
                client(functions.account.GetAuthorizationsRequest()),
                return_exceptions=True
            )

            if isinstance(me_res, (errors.UserDeactivatedBanError, errors.UserDeactivatedError,
                                   errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError,
                                   errors.AuthKeyInvalidError, errors.SessionPasswordNeededError,
                                   errors.SessionRevokedError, errors.SessionExpiredError)) or me_res is None:
                is_corrupt = True
                output_buffer.append(f"{RED}[{idx}/{total_count}] {s_name} [💀 Banned / Logged Out]{RESET}")
                break

            if not isinstance(me_res, Exception) and me_res:
                try:
                    msg = await asyncio.wait_for(client.send_message('me', 'hi'), timeout=7.0)
                    await client.delete_messages('me', [msg.id])
                    is_alive = True
                except Exception:
                    is_frozen = True
                    is_alive = False

                user_name = me_res.first_name if me_res.first_name else "Unknown"
                username_str = f"@{me_res.username}" if me_res.username else "@None"
                user_id = me_res.id
                phone = f"+{me_res.phone}" if me_res.phone else f"+{s_name}"

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

                elif is_frozen:
                    output_buffer.append(f"{YELLOW}[{idx}/{total_count}] User: {s_name} [❄️ FROZEN - Message Failed]{RESET}")
                break

        except Exception:
            await asyncio.sleep(0.3 * attempt)
            continue
        finally:
            try:
                await client.disconnect()
            except Exception:
                pass

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
        if not output_buffer:
            output_buffer.append(f"{RED}[{idx}/{total_count}] {s_name} [Timeout/Error]{RESET}")

    results_buffer[idx] = output_buffer

async def check_queue_worker(queue, total_count, api_keys, proxies, default_ip, results_buffer, stats):
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        idx, session_file = item
        try:
            await fast_check_session_task(session_file, idx, total_count, api_keys,
                                          proxies, default_ip, results_buffer, stats)
        except Exception:
            results_buffer[idx] = []
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
            print(f"{RED}[✖] No proxies found in proxies.txt!{RESET}")
            return

    w_input = input(f"\n{YELLOW}Worker Count [Recommended: 20-50]: {RESET}").strip()
    workers_count = int(w_input) if w_input.isdigit() and 1 <= int(w_input) <= 100 else 30

    api_keys = get_github_apis()
    default_ip = get_current_network_info()['ip']

    print(f"\n{CYAN}⚡ Starting Checker on {total_files} accounts...{RESET}\n")
    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1):
        queue.put_nowait((idx, s_file))

    stats = {'alive': 0, 'corrupt': 0, 'frozen': 0, 'error': 0}
    results_buffer = {}

    workers = [asyncio.create_task(check_queue_worker(queue, total_files, api_keys, proxies,
                                                       default_ip, results_buffer, stats))
               for _ in range(min(workers_count, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task
    print(f"\n{GREEN}✔ Completed! Alive: {stats['alive']} | Dead: {stats['corrupt']} | Frozen: {stats['frozen']}{RESET}")

# ═══════════════════════════════════════════════════════════════
#              [7] BREAKUP SESSION
# ═══════════════════════════════════════════════════════════════
async def clone_single_session_task(session_file, idx, total_files, api_keys, proxies,
                                    two_fa_password, target_folder, stats_dict,
                                    results_buffer, default_ip):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file
    target_session_base = os.path.join(target_folder, s_name)
    temp_session_file = f"{target_session_base}.session"

    log_buffer = []
    account_success, is_already_dead = False, False

    await asyncio.sleep(random.uniform(0.1, 0.8))

    for attempt in range(1, 4):
        api_pair = random.choice(api_keys)
        chosen_device = random.choice(DESKTOP_DEVICES)
        chosen_proxy = random.choice(proxies) if proxies else None

        if os.path.exists(temp_session_file):
            try:
                os.remove(temp_session_file)
            except Exception:
                pass

        proxy_timeout = 7.0 if chosen_proxy else 10.0
        old_client = create_telethon_client(session_base, api_pair, timeout=8)
        new_client = create_telethon_client(target_session_base, api_pair, timeout=proxy_timeout,
                                            device_config=chosen_device, proxy_info=chosen_proxy)

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
                if otp_code:
                    break
                await asyncio.sleep(1.0)

            if not otp_code:
                if attempt == 3:
                    log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> OTP Not Received!{RESET}")
                continue

            try:
                await asyncio.wait_for(
                    new_client.sign_in(phone=phone, code=otp_code, phone_code_hash=sent_code.phone_code_hash),
                    timeout=12.0
                )
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

                json_data = create_expert_json(
                    s_name, phone.replace("+", ""), me_old.id, me_old.first_name,
                    me_old.last_name, me_old.username, api_pair[0], api_pair[1],
                    two_fa_password, chosen_device, proxy_str
                )
                with open(os.path.join(target_folder, f"{s_name}.json"), "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)

                log_buffer.append(CYAN + "=" * 58)
                log_buffer.append(f"{CYAN}[{idx}/{total_files}] Breakup Success: {GREEN}{phone} {MAGENTA}[API: {api_pair[0]}]{RESET}")
                log_buffer.append(f"    {WHITE}OTP Code     : {YELLOW}{otp_code}{RESET}")
                log_buffer.append(f"    {WHITE}Login IP     : {YELLOW}{used_ip}{WHITE} ({GREEN}{loc_string}{WHITE}){RESET}")
                log_buffer.append(f"    {YELLOW}⚡ Old Session is STILL ALIVE!{RESET}")

                account_success = True
                stats_dict['success'] += 1
                break

        except (errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError,
                errors.AuthKeyInvalidError, errors.SessionExpiredError,
                errors.SessionRevokedError, errors.UserDeactivatedBanError,
                errors.UserDeactivatedError):
            log_buffer.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Dead (Auth Invalid){RESET}")
            is_already_dead = True
            break
        except Exception as e:
            if attempt == 3:
                log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Failed: {str(e)[:40]}{RESET}")
        finally:
            try:
                await old_client.disconnect()
            except:
                pass
            try:
                await new_client.disconnect()
            except:
                pass

    if account_success or is_already_dead:
        dest_folder = "Dead_Sessions" if is_already_dead else "Processed_Old_Sessions"
        move_session_files(session_file, dest_folder)

    if not account_success and not is_already_dead:
        stats_dict['fail'] += 1
        if not log_buffer:
            log_buffer.append(f"{RED}[{idx}/{total_files}] {s_name} -> Breakup Failed{RESET}")
        if os.path.exists(temp_session_file):
            try:
                os.remove(temp_session_file)
            except:
                pass

    results_buffer[idx] = log_buffer

async def breakup_worker(queue, total_files, api_keys, proxies, two_fa_password,
                        target_folder, stats_dict, results_buffer, default_ip):
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        idx, s_file = item
        try:
            await clone_single_session_task(s_file, idx, total_files, api_keys, proxies,
                                            two_fa_password, target_folder, stats_dict,
                                            results_buffer, default_ip)
        except Exception:
            results_buffer[idx] = []
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
    elif mode != "1":
        return

    folder_input = input(f"\n{YELLOW}Enter Folder Name (e.g. 20, +62): {RESET}").strip()
    folder = os.path.join(BASE_DIR, folder_input)
    if not os.path.exists(folder):
        print(f"{RED}[✖] Folder '{folder_input}' not found!{RESET}")
        return

    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0:
        return

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
    for idx, s_file in enumerate(session_files, start=1):
        queue.put_nowait((idx, s_file))

    stats_dict = {'success': 0, 'fail': 0}
    results_buffer = {}

    workers = [asyncio.create_task(breakup_worker(queue, total_files, api_keys, proxies,
                                                   two_fa_password, target_folder, stats_dict,
                                                   results_buffer, default_ip))
               for _ in range(min(concurrency, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task

    print(CYAN + "=" * 58)
    print(f"\n{GREEN}✔ Breakup Completed! Saved in 'Breakup_Success' folder.{RESET}")
    print(f"{GREEN}[*] Success: {stats_dict['success']} {RED}| Failed/Skipped: {stats_dict['fail']}{RESET}")

# ═══════════════════════════════════════════════════════════════
#              [8] 2FA MANAGER
# ═══════════════════════════════════════════════════════════════
async def check_2fa_task(session_file, idx, total_files, api_keys, proxies,
                        mode, old_pwd, new_pwd, stats, results_buffer):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file

    out = []
    api_pair = random.choice(api_keys)
    chosen_proxy = random.choice(proxies) if proxies else None
    timeout_sec = 8.0 if chosen_proxy else 10.0

    client = create_telethon_client(session_base, api_pair, timeout=timeout_sec, proxy_info=chosen_proxy)

    await asyncio.sleep(random.uniform(0.5, 1.5))

    try:
        async with get_connect_semaphore(20):
            await asyncio.wait_for(client.connect(), timeout=timeout_sec)

        if not await client.is_user_authorized():
            out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Unauthorized{RESET}")
            stats['error'] += 1
            results_buffer[idx] = out
            return

        pwd_info = await client(functions.account.GetPasswordRequest())

        if mode == "1":
            if pwd_info.has_password:
                try:
                    await client.edit_2fa(current_password=old_pwd, new_password=new_pwd)
                    update_json_2fa(session_file, new_pwd)
                    out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> 2FA Changed to '{new_pwd}'!{RESET}")
                    move_session_files(session_file, f"Pass_{new_pwd}")
                    stats['success'] += 1
                except errors.PasswordHashInvalidError:
                    out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Wrong Current Password!{RESET}")
                    stats['error'] += 1
            else:
                await client.edit_2fa(new_password=new_pwd)
                update_json_2fa(session_file, new_pwd)
                out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> New 2FA Set!{RESET}")
                move_session_files(session_file, f"Pass_{new_pwd}")
                stats['success'] += 1

        elif mode == "2":
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
                out.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> No 2FA{RESET}")
                stats['success'] += 1

        elif mode == "3":
            if not pwd_info.has_password:
                out.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> No 2FA{RESET}")
                stats['success'] += 1
            else:
                try:
                    await client(functions.account.ResetPasswordRequest())
                    update_json_2fa(session_file, "")
                    out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> Password Reset!{RESET}")
                    stats['success'] += 1
                except errors.ResetWaitError as e:
                    days = e.seconds // 86400
                    hours = (e.seconds % 86400) // 3600
                    out.append(f"{MAGENTA}[{idx}/{total_files}] {s_name} -> Reset Pending: {days}d {hours}h{RESET}")
                    move_session_files(session_file, "Reset_Pending")
                    stats['pending'] += 1

    except Exception as ex:
        err_msg = str(ex).strip()[:40] if str(ex).strip() else ex.__class__.__name__
        out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Failed: {err_msg}{RESET}")
        stats['error'] += 1
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass

    results_buffer[idx] = out

async def two_fa_worker(queue, total_files, api_keys, proxies, mode, old_pwd, new_pwd, stats, results_buffer):
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        idx, session_file = item
        await check_2fa_task(session_file, idx, total_files, api_keys, proxies,
                             mode, old_pwd, new_pwd, stats, results_buffer)
        queue.task_done()

async def run_2fa_manager():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "             2 F A   M A N A G E R                " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")

    print(f"\n{WHITE}Select Network Mode:{RESET}")
    print(f"{CYAN}[1] Local IP / Direct Internet{RESET}")
    print(f"{CYAN}[2] Use Proxies from GitHub{RESET}")
    net_mode = input(f"{YELLOW}[#] Option: {RESET}").strip()

    proxies = []
    if net_mode == "2":
        proxies = load_proxies("proxies.txt")
        if not proxies:
            print(f"{RED}[✖] No proxies found in proxies.txt!{RESET}")
            return

    folder_input = input(f"\n{YELLOW}Enter Folder Name (e.g. 20, +62): {RESET}").strip()
    folder = os.path.join(BASE_DIR, folder_input)
    if not os.path.exists(folder):
        print(f"{RED}[✖] Folder not found!{RESET}")
        return

    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0:
        print(f"{RED}[✖] No sessions found!{RESET}")
        return

    print(f"\n{WHITE}Select 2FA Action:{RESET}")
    print(f"{CYAN}[1] Change 2FA{RESET}")
    print(f"{CYAN}[2] Disable 2FA{RESET}")
    print(f"{CYAN}[3] Reset 2FA{RESET}")
    print(f"{CYAN}[0] Back{RESET}")
    mode = input(f"{YELLOW}[#] Option: {RESET}").strip()

    if mode not in ["1", "2", "3"]:
        return

    old_pwd, new_pwd = "", ""
    if mode == "1":
        old_pwd = input(f"{YELLOW}Current 2FA Password (empty if none): {RESET}").strip()
        new_pwd = input(f"{YELLOW}New 2FA Password: {RESET}").strip()
    elif mode == "2":
        old_pwd = input(f"{YELLOW}Current 2FA Password: {RESET}").strip()

    api_keys = get_github_apis()
    w_input = input(f"\n{YELLOW}Worker Count [Recommended: 15-30]: {RESET}").strip()
    concurrency = int(w_input) if w_input.isdigit() and 1 <= int(w_input) <= 50 else 20

    print(f"\n{CYAN}⚡ Starting 2FA Manager...{RESET}\n")

    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1):
        queue.put_nowait((idx, s_file))

    stats = {'success': 0, 'pending': 0, 'error': 0}
    results_buffer = {}

    workers = [asyncio.create_task(two_fa_worker(queue, total_files, api_keys, proxies,
                                                  mode, old_pwd, new_pwd, stats, results_buffer))
               for _ in range(min(concurrency, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task

    print(CYAN + "=" * 58)
    if mode == "3":
        print(f"\n{GREEN}✔ Completed! Success: {stats['success']} | Pending: {stats['pending']} | Errors: {stats['error']}{RESET}")
    else:
        print(f"\n{GREEN}✔ Completed! Success: {stats['success']} | Errors: {stats['error']}{RESET}")

# ═══════════════════════════════════════════════════════════════
#              [9] KILL SESSION
# ═══════════════════════════════════════════════════════════════
async def kill_single_session_task(session_file, idx, total_files, api_keys, proxies,
                                   killed_folder, stats, results_buffer):
    s_name = os.path.splitext(os.path.basename(session_file))[0]
    session_base = session_file[:-8] if session_file.endswith(".session") else session_file

    out = []
    api_pair = random.choice(api_keys)
    chosen_proxy = random.choice(proxies) if proxies else None
    timeout_sec = 8.0 if chosen_proxy else 10.0

    client = create_telethon_client(session_base, api_pair, timeout=timeout_sec, proxy_info=chosen_proxy)

    is_already_dead = False
    kill_success = False

    try:
        await asyncio.sleep(random.uniform(0.5, 2.0))
        async with get_connect_semaphore(20):
            await asyncio.wait_for(client.connect(), timeout=timeout_sec)

        if not await client.is_user_authorized():
            is_already_dead = True
            out.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Already Dead{RESET}")
        else:
            await asyncio.wait_for(client(functions.auth.LogOutRequest()), timeout=timeout_sec)
            kill_success = True
            out.append(f"{GREEN}[{idx}/{total_files}] {s_name} -> Logged Out (Killed)!{RESET}")

    except (errors.AuthKeyUnregisteredError, errors.AuthKeyDuplicatedError,
            errors.AuthKeyInvalidError, errors.SessionExpiredError,
            errors.SessionRevokedError, errors.UserDeactivatedBanError,
            errors.UserDeactivatedError):
        is_already_dead = True
        out.append(f"{YELLOW}[{idx}/{total_files}] {s_name} -> Dead (Auth Invalid){RESET}")
    except Exception as ex:
        err_msg = str(ex).strip()[:40] if str(ex).strip() else ex.__class__.__name__
        out.append(f"{RED}[{idx}/{total_files}] {s_name} -> Kill Failed: {err_msg}{RESET}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass

    if kill_success or is_already_dead:
        if kill_success:
            stats['killed'] += 1
        else:
            stats['already_dead'] += 1
        move_session_files(session_file, killed_folder)
    else:
        stats['error'] += 1

    results_buffer[idx] = out

async def kill_session_worker(queue, total_files, api_keys, proxies, killed_folder, stats, results_buffer):
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        idx, session_file = item
        await kill_single_session_task(session_file, idx, total_files, api_keys, proxies,
                                       killed_folder, stats, results_buffer)
        queue.task_done()

async def run_kill_session():
    clear_screen()
    print(CYAN + "╔══════════════════════════════════════════════════╗")
    print(CYAN + "║" + MAGENTA + "         K I L L   S E S S I O N   (L O G O U T)  " + CYAN + "║")
    print(CYAN + "╚══════════════════════════════════════════════════╝")

    print(f"\n{WHITE}Select Network Mode:{RESET}")
    print(f"{CYAN}[1] Local IP / Direct Internet{RESET}")
    print(f"{CYAN}[2] Use Proxies from GitHub{RESET}")
    net_mode = input(f"{YELLOW}[#] Option: {RESET}").strip()

    proxies = []
    if net_mode == "2":
        proxies = load_proxies("proxies.txt")
        if not proxies:
            print(f"{RED}[✖] No proxies found!{RESET}")
            return

    folder_input = input(f"\n{YELLOW}Enter Folder Name (e.g. 20, +62): {RESET}").strip()
    folder = os.path.join(BASE_DIR, folder_input)
    if not os.path.exists(folder):
        print(f"{RED}[✖] Folder not found!{RESET}")
        return

    session_files = sorted(glob.glob(os.path.join(folder, "*.session")))
    total_files = len(session_files)
    if total_files == 0:
        print(f"{RED}[✖] No sessions!{RESET}")
        return

    killed_folder = "Killed_Sessions"
    api_keys = get_github_apis()

    w_input = input(f"\n{YELLOW}Worker Count [Recommended: 15-30]: {RESET}").strip()
    concurrency = int(w_input) if w_input.isdigit() and 1 <= int(w_input) <= 50 else 20

    print(f"\n{CYAN}🔥 Starting Self-Logout for {total_files} accounts...{RESET}\n")

    queue = asyncio.Queue()
    for idx, s_file in enumerate(session_files, start=1):
        queue.put_nowait((idx, s_file))

    stats = {'killed': 0, 'already_dead': 0, 'error': 0}
    results_buffer = {}

    workers = [asyncio.create_task(kill_session_worker(queue, total_files, api_keys, proxies,
                                                        killed_folder, stats, results_buffer))
               for _ in range(min(concurrency, total_files))]
    printer_task = asyncio.create_task(ordered_output_printer(results_buffer, total_files))

    await queue.join()
    await printer_task

    print(CYAN + "=" * 58)
    print(f"\n{GREEN}✔ Completed! Killed: {stats['killed']} | Already Dead: {stats['already_dead']} | Errors: {stats['error']}{RESET}")

# ═══════════════════════════════════════════════════════════════
#              OTHER MODULES
# ═══════════════════════════════════════════════════════════════
def api_keys_info():
    clear_screen()
    print(f"\n{GREEN}✔ API Keys are strictly auto-fetched from your GitHub URL:{RESET}")
    print(f"{CYAN}{GITHUB_API_URL}{RESET}")
    print(f"\n{WHITE}You do not need to upload keys locally.{RESET}")

def check_proxies():
    proxies = load_proxies("proxies.txt")
    clear_screen()
    if proxies:
        print(f"\n{GREEN}✔ Loaded {len(proxies)} proxies from GitHub.{RESET}")
    else:
        print(f"\n{RED}✖ No proxies found.{RESET}")

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
        if phone.upper() in ['E', 'EXIT']:
            break
        if not phone:
            continue

        session_name = phone.replace("+", "")
        session_path = os.path.join(folder, session_name)
        client = create_telethon_client(session_path, api_pair, timeout=10, device_config=chosen_device)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                try:
                    await client.send_code_request(phone)
                    code = input(f"{GREEN}Enter Telegram OTP code: {RESET}").strip()
                    try:
                        await client.sign_in(phone, code)
                    except errors.SessionPasswordNeededError:
                        pwd = input(f"{YELLOW}Enter 2FA Login Password: {RESET}").strip()
                        await client.sign_in(password=pwd)
                        two_fa_pass = pwd
                    print(f"{GREEN}[✔] Session created in {folder}!{RESET}")
                    me = await client.get_me()
                    json_data = create_expert_json(session_name, session_name, me.id,
                                                    me.first_name, me.last_name, me.username,
                                                    api_pair[0], api_pair[1], two_fa_pass, chosen_device)
                    with open(os.path.join(folder, f"{session_name}.json"), "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    print(f"{RED}[✖] Error: {e}{RESET}")
            else:
                print(f"{GREEN}[✔] Already Authorized!{RESET}")
        finally:
            try:
                await client.disconnect()
            except Exception:
                pass

# ═══════════════════════════════════════════════════════════════
#                          MAIN MENU
# ═══════════════════════════════════════════════════════════════
def main():
    startup_channel_prompt()

    while True:
        show_banner()
        choice = input(f"\n{YELLOW}[#] Select Option: {RESET}").strip().upper()

        if choice == "1":
            asyncio.run(create_session())
        elif choice == "2":
            run_session_to_tdata()
        elif choice == "3":
            check_proxies()
        elif choice == "4":
            api_keys_info()
        elif choice == "5":
            print(f"{YELLOW}[!] Feature under construction{RESET}")
        elif choice == "6":
            asyncio.run(check_folder_sessions())
        elif choice == "7":
            asyncio.run(breakup_session())
        elif choice == "8":
            asyncio.run(run_2fa_manager())
        elif choice == "9":
            asyncio.run(run_kill_session())
        elif choice in ["0", "E", "EXIT"]:
            print(f"\n{RED}[!] Exiting Tools. Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}[✖] Invalid Option!{RESET}")
        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
