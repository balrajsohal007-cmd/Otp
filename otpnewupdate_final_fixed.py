#!/usr/bin/env python3
"""⚡ BALRAJ OTP BOT — FINAL v14 | OWNER: BALRAP1 ⚡"""
import os, re, json, time, asyncio, logging, gc, random, sqlite3, tempfile, urllib.parse
from io import BytesIO
from html import escape as html_escape
from collections import Counter
from datetime import datetime

import aiohttp
from telegram import (Bot, Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler,
                          MessageHandler, filters, ContextTypes)
from telegram.error import (NetworkError, TimedOut, RetryAfter, Conflict, BadRequest)

try:
    from telegram import ReactionTypeEmoji
    REACTION_OK = True
except ImportError:
    ReactionTypeEmoji = None; REACTION_OK = False

# ═══════════════════════════ CONFIG ═══════════════════════════
BOT_TOKEN = "8944809064:AAFex4DSh08UIFKFM_JaGnRCGSSTRQWOnNE"
ADMIN_IDS = [8872448185]
OWNER_NAME = "BALRAP1"; BOT_BRAND = "BALRAJ"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("Bot")

FB_TIMEOUT = 10; FB_MAX = 400; FB_PAGE = 10; FB_CONC = 80
SMS_INTERVAL = 1; SMS_DURATION = 300; SMS_IDLE = 600
ADMIN_REFRESH = 180; ADMIN_LIVE = 5; GIFT_MAX_H = 8760
MAX_USER_FB = 20; LEADER_TOP = 15; AUTO_BK = [6, 12, 24]
SPIN_CD = 86400; UL_PAGE = 10; WATCHDOG = 240; MEM_CHECK = 300
HB_INTERVAL = 30; RX_PAGE = 30; RX_COLS = 6; ACCESS_CHK = 30
DEV_PAGE = 6
BASELINE_RECENT_SEC = 90  # OTP arriving within last 90s shown even if in baseline

# ═══════════════════════════ SHARED HTTP SESSION ═══════════════════════════
_HTTP_SESSION = None

def get_session():
    global _HTTP_SESSION
    if _HTTP_SESSION is None or _HTTP_SESSION.closed:
        _HTTP_SESSION = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=FB_TIMEOUT),
            connector=aiohttp.TCPConnector(
                limit=150, limit_per_host=25, ttl_dns_cache=300, enable_cleanup_closed=True,
            ),
        )
    return _HTTP_SESSION

async def close_session():
    global _HTTP_SESSION
    if _HTTP_SESSION is not None and not _HTTP_SESSION.closed:
        try: await _HTTP_SESSION.close()
        except Exception: pass
    _HTTP_SESSION = None

FORCE_JOIN_FILE = "force_join_channels.json"
USER_IDS_FILE = "bot_users.json"
MAINT_FILE = "maintenance_mode.json"
GLOBAL_FB_FILE = "global_firebases.json"
DEV_CACHE_FILE = "global_devices_cache.json"
CAPTCHA_FILE = "captcha_state.json"
REFERRAL_FILE = "referrals.json"
USER_FB_FILE = "user_custom_fbs.json"
LOGGER_FILE = "logger_settings.json"
SETTINGS_FILE = "bot_settings.json"
CREDITS_FILE = "user_credits.json"

DEFAULT_CH = [{"id": "@aura_gc4", "label": "BACKUP 2", "url": "https://t.me/aura_gc4"}]

ALLOWED_REACTIONS = ["👍","👎","❤","🔥","🥰","👏","😁","🤔","🤯","😱","🤬","😢","🎉","🤩","🤮","💩","🙏","👌","🕊","🤡","🥱","🥴","😍","🐳","❤‍🔥","🌚","🌭","💯","🤣","⚡","🍌","🏆","💔","🤨","😐","🍓","🍾","💋","🖕","😈","😴","😭","🤓","👻","👨‍💻","👀","🎃","🙈","😇","😨","🤝","✍","🤗","🫡","🎅","🎄","☃","💅","🤪","🗿","🆒","💘","🙉","🦄","😘","💊","🙊","😎","👾","🤷‍♂","🤷","🤷‍♀","😡"]

ALLOWED_EFFECTS = {
    "fire": {"emoji": "🔥", "label": "Fire", "id": "5104841245755180586"},
    "like": {"emoji": "👍", "label": "Like", "id": "5107584321108051014"},
    "dislike": {"emoji": "👎", "label": "Dislike", "id": "5104858069142078462"},
    "heart": {"emoji": "❤️", "label": "Heart", "id": "5159385139981059251"},
    "party": {"emoji": "🎉", "label": "Party", "id": "5046509860389126442"},
    "poop": {"emoji": "💩", "label": "Poop", "id": "5046589136895476101"},
}

_BM = {'A':'𝗔','B':'𝗕','C':'𝗖','D':'𝗗','E':'𝗘','F':'𝗙','G':'𝗚','H':'𝗛','I':'𝗜','J':'𝗝','K':'𝗞','L':'𝗟','M':'𝗠','N':'𝗡','O':'𝗢','P':'𝗣','Q':'𝗤','R':'𝗥','S':'𝗦','T':'𝗧','U':'𝗨','V':'𝗩','W':'𝗪','X':'𝗫','Y':'𝗬','Z':'𝗭','a':'𝗮','b':'𝗯','c':'𝗰','d':'𝗱','e':'𝗲','f':'𝗳','g':'𝗴','h':'𝗵','i':'𝗶','j':'𝗷','k':'𝗸','l':'𝗹','m':'𝗺','n':'𝗻','o':'𝗼','p':'𝗽','q':'𝗾','r':'𝗿','s':'𝘀','t':'𝘁','u':'𝘂','v':'𝘃','w':'𝘄','x':'𝘅','y':'𝘆','z':'𝘇','0':'𝟬','1':'𝟭','2':'𝟮','3':'𝟯','4':'𝟰','5':'𝟱','6':'𝟲','7':'𝟳','8':'𝟴','9':'𝟵'}
_REV_BM = {v: k for k, v in _BM.items()}
def bold(t): return ''.join(_BM.get(c, c) for c in t)
def _unbold(s): return ''.join(_REV_BM.get(c, c) for c in s)
def _has(text, word): return word in text or bold(word) in text

def _ld(p, d):
    try:
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    except: return d

def _sv(p, d):
    try:
        t = f"{p}.tmp"
        with open(t, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)
        os.replace(t, p)
    except Exception as e: logger.warning(f"save {p}: {e}")

async def _sv_async(p, d):
    await asyncio.to_thread(_sv, p, d)

DEFAULT_SETTINGS = {
    "referral_system": True, "credit_system": False,
    "referral_seconds": 10800,          # 3h default
    "credits_per_number": 1,
    "daily_spin_reward_min": 1, "daily_spin_reward_max": 5,
    "auto_stop_seconds": 0,             # 0 = disabled (idle-timeout only)
    "button_colors": {"primary": "primary", "success": "success", "danger": "danger"},
    "enabled_reactions": list(ALLOWED_REACTIONS),
    "enabled_effects": list(ALLOWED_EFFECTS.keys()),
}
bot_settings = {**DEFAULT_SETTINGS, **_ld(SETTINGS_FILE, {})}
# migrate old referral_hours → referral_seconds
if "referral_hours" in bot_settings and "referral_seconds" not in bot_settings:
    bot_settings["referral_seconds"] = int(float(bot_settings.pop("referral_hours", 3)) * 3600)
bot_settings.pop("referral_hours", None)
bot_settings["button_colors"] = {**DEFAULT_SETTINGS["button_colors"], **bot_settings.get("button_colors", {})}
bot_settings.setdefault("enabled_reactions", list(ALLOWED_REACTIONS))
bot_settings.setdefault("enabled_effects", list(ALLOWED_EFFECTS.keys()))
def save_settings(): _sv(SETTINGS_FILE, bot_settings)

def ref_sec(): return int(bot_settings.get("referral_seconds", 10800))
def ref_h():   return ref_sec() / 3600          # float hours for display
def ref_label():
    """Returns a short human label e.g. '3h', '30m', '1d'"""
    s = ref_sec()
    if s < 60:   return f"{s}s"
    if s < 3600: return f"{s//60}m"
    if s < 86400:return f"{s//3600}h"
    if s < 2592000: return f"{s//86400}d"
    return f"{s//2592000}mo"

def auto_stop_sec(): return int(bot_settings.get("auto_stop_seconds", 0))
def auto_stop_label():
    s = auto_stop_sec()
    if s <= 0: return "OFF"
    if s < 60: return f"{s}s"
    if s < 3600: return f"{s//60}m"
    if s < 86400: return f"{s//3600}h"
    if s < 2592000: return f"{s//86400}d"
    return f"{s//2592000}mo"

def parse_duration(s):
    """Parse '30s','30m','2h','1d','1mo' → total seconds. Returns None on error."""
    s = str(s).strip().lower()
    m = re.fullmatch(r'(\d+(?:\.\d+)?)(mo|s|m|h|d)', s)
    if not m: return None
    v, u = float(m.group(1)), m.group(2)
    mult = {'s':1,'m':60,'h':3600,'d':86400,'mo':2592000}
    return int(v * mult[u])

user_credits = _ld(CREDITS_FILE, {})
if not isinstance(user_credits, dict): user_credits = {}
def _uc(uid):
    s = str(uid)
    if s not in user_credits or not isinstance(user_credits[s], dict):
        user_credits[s] = {"credits": 0, "last_spin": 0, "banned": False, "numbers_generated": 0}
    u = user_credits[s]
    u.setdefault("credits", 0); u.setdefault("last_spin", 0)
    u.setdefault("banned", False); u.setdefault("numbers_generated", 0)
    return u
def save_credits(): _sv(CREDITS_FILE, user_credits)
def is_banned(uid): return bool(user_credits.get(str(uid), {}).get("banned", False))

REQUIRED_CHANNELS = _ld(FORCE_JOIN_FILE, list(DEFAULT_CH)) or list(DEFAULT_CH)
if not isinstance(REQUIRED_CHANNELS, list): REQUIRED_CHANNELS = list(DEFAULT_CH)
def _sv_ch(): _sv(FORCE_JOIN_FILE, REQUIRED_CHANNELS)

known_users = {int(v) for v in _ld(USER_IDS_FILE, []) if str(v).isdigit()}
def _sv_uids(): _sv(USER_IDS_FILE, sorted(known_users))

maintenance_mode = bool(_ld(MAINT_FILE, {}).get("enabled", False))
def _sv_maint(): _sv(MAINT_FILE, {"enabled": maintenance_mode})

captcha_enabled = bool(_ld(CAPTCHA_FILE, {"enabled": True}).get("enabled", True))
def _sv_cap(): _sv(CAPTCHA_FILE, {"enabled": captcha_enabled})

def _ld_fb():
    out = []
    for i, x in enumerate(_ld(GLOBAL_FB_FILE, [])):
        if isinstance(x, dict) and x.get("url"):
            u = str(x["url"]).strip().rstrip("/")
            while u.endswith(".json"): u = u[:-5].rstrip("/")
            if "firebaseio.com" in u or "firebasedatabase.app" in u:
                out.append((u, str(x.get("tag") or f"FB{i+1}")))
    return out
global_fb_list = _ld_fb()
def _sv_fb(): _sv(GLOBAL_FB_FILE, [{"url": u, "tag": t} for u, t in global_fb_list])
def _retag():
    global global_fb_list
    global_fb_list = [(u, f"FB{i+1}") for i, (u, _) in enumerate(global_fb_list)]

REFERRAL_DB = _ld(REFERRAL_FILE, {})
if not isinstance(REFERRAL_DB, dict): REFERRAL_DB = {}
def _sv_ref(): _sv(REFERRAL_FILE, REFERRAL_DB)

USER_CUSTOM_FBS = _ld(USER_FB_FILE, {})
if not isinstance(USER_CUSTOM_FBS, dict): USER_CUSTOM_FBS = {}
def _sv_ufb(): _sv(USER_FB_FILE, USER_CUSTOM_FBS)

LOGGER_SETTINGS = _ld(LOGGER_FILE, {"channel": "", "auto_backup": True, "interval_hours": 6, "last_backup_at": 0.0})
def _sv_log(): _sv(LOGGER_FILE, LOGGER_SETTINGS)

_last_refresh = time.monotonic()
user_access_state = {}
verified_users = set()
_ref_lock = None   # lazy-init inside async context (fix: asyncio.Lock() at module level crashes Python 3.12+)
user_sessions = {}
sms_tasks = {}
sms_state = {}
admin_live_tasks = {}
BOT_USERNAME = "Bot"
_PHONE_RX = [re.compile(r'\b(?:\+91|91|0)?([6-9]\d{9})\b'),
             re.compile(r'\b(?:phone|mobile|number)[\s:]*([6-9]\d{9})\b', re.I),
             re.compile(r'[^0-9]([6-9]\d{9})[^0-9]'),
             re.compile(r'(\+91[-\s]?[6-9][0-9]{9})'),
             re.compile(r'(?:\b91)([6-9][0-9]{9})\b'),
             re.compile(r'(?:^|\s|:)([6-9][0-9]{9})(?:\s|$|\.)')]

def kbtn(text, style=None):
    try:
        if style: return KeyboardButton(text, api_kwargs={"style": style})
        return KeyboardButton(text)
    except: return KeyboardButton(text)

# ═══════════════════════════ BUTTON LABELS ═══════════════════════════
BT_GEN = f"🎲 {bold('GENERATE NUMBER')}"
BT_NEW = f"🎲 {bold('NEW NUMBER')}"
BT_SCAN = f"🔎 {bold('SCAN ACTIVE')}"
BT_REFER = f"👥 {bold('REFER & EARN')}"
BT_SPIN = f"🎁 {bold('DAILY SPIN')}"
BT_CUSTOM = f"🎯 {bold('CUSTOM PANEL')}"
BT_LB = f"🏆 {bold('LEADERBOARD')}"
BT_PROF = f"ℹ️ {bold('MY PROFILE')}"
BT_ADMIN = f"⚙️ {bold('ADMIN PANEL')}"
BT_BACK = f"🔙 {bold('MAIN MENU')}"
BT_SMS = f"📩 {bold('LAST 5 SMS')}"
BT_RFSMS = f"🔄 {bold('REFRESH SMS')}"
BT_STOPMON = f"⛔ {bold('STOP MONITOR')}"
BT_RX = f"💬 {bold('REACTIONS')}"
BT_FX = f"✨ {bold('EFFECTS')}"
BT_REFHRS = f"⏰ {bold('REFERRAL TIME')}"
BT_AUTOSTOP = f"⏲ {bold('AUTO STOP MONITOR')}"
BT_FBTIERS = f"🎚 {bold('DEVICE TIERS')}"
BT_TIER_LOW = f"🟢 {bold('LOW TIER')}"
BT_TIER_MID = f"🟡 {bold('MID TIER')}"
BT_TIER_HIGH = f"🔴 {bold('HIGH TIER')}"
BT_CREDCFG = f"💎 {bold('CREDITS/NUMBER')}"
BT_ADDFB = f"➕ {bold('ADD FIREBASE')}"
BT_BULK = f"📤 {bold('BULK ADD (.txt)')}"
BT_MNGFB = f"📋 {bold('MANAGE FBs')}"
BT_REFRESH = f"🔄 {bold('REFRESH')}"
BT_TOTAL = f"📈 {bold('TOTAL DEVICES')}"
BT_USERS = f"👥 {bold('USER LIST')}"
BT_UFBS = f"🎯 {bold('USER CUSTOM FBs')}"
BT_LOGGER = f"📁 {bold('LOGGER & BACKUP')}"
BT_STATS = f"📊 {bold('STATISTICS')}"
BT_GIFT = f"🎁 {bold('GIFT ACCESS')}"
BT_BCAST = f"📢 {bold('BROADCAST')}"
BT_COLORS = f"🎨 {bold('BUTTON COLORS')}"
BT_ADDCH = f"➕ {bold('ADD CHANNEL')}"
BT_MNGCH = f"📋 {bold('CHANNELS')}"
BT_ADMINBACK = f"🔙 {bold('ADMIN PANEL')}"
BT_BACKBTN = f"🔙 {bold('BACK')}"
BT_SELALL = f"✅ {bold('SELECT ALL')}"
BT_DESELALL = f"❌ {bold('DESELECT ALL')}"
BT_PREV = f"◀️ {bold('PREV')}"
BT_NEXT = f"▶️ {bold('NEXT')}"
BT_UDGIFT = f"🎁 {bold('GIFT HOURS')}"
BT_UADDREF = f"➕ {bold('ADD REFER')}"
BT_UGIFTCRED = f"💎 {bold('GIFT CREDITS')}"
BT_UBAN = f"🚫 {bold('BAN USER')}"
BT_UUNBAN = f"✅ {bold('UNBAN USER')}"
BT_UBACK = f"🔙 {bold('BACK TO LIST')}"
BT_GSINGLE = f"👤 {bold('GIFT SINGLE USER')}"
BT_GALL = f"👥 {bold('GIFT ALL USERS')}"
BT_VERIFY = f"✅ {bold('VERIFY MEMBERSHIP')}"
BT_LOGSET = f"🔗 {bold('SET CHANNEL')}"
BT_LOGBK = f"💾 {bold('BACKUP NOW')}"
BT_LOGRES = f"📥 {bold('RESTORE FROM .db')}"
BT_LOG6 = "⏰ 6h"; BT_LOG12 = "⏰ 12h"; BT_LOG24 = "⏰ 24h"
BT_CANCEL = f"❌ {bold('CANCEL')}"
BT_PAGE = "📄"

# ═══════════════════════════ KEYBOARDS ═══════════════════════════
def kb_main(uid):
    rows = [
        [kbtn(BT_GEN, "primary")],
        [kbtn(BT_SCAN, "primary"), kbtn(BT_REFER, "success")],
        [kbtn(BT_SPIN, "success"), kbtn(BT_CUSTOM, "primary")],
        [kbtn(BT_LB, "primary"), kbtn(BT_PROF, "primary")],
    ]
    if uid in ADMIN_IDS: rows.append([kbtn(BT_ADMIN, "danger")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def kb_device():
    return ReplyKeyboardMarkup([
        [kbtn(BT_NEW, "primary")],
        [kbtn(BT_SMS, "primary"), kbtn(BT_RFSMS, "success")],
        [kbtn(BT_STOPMON, "danger")],
        [kbtn(BT_SCAN, "primary"), kbtn(BT_BACK, "danger")],
    ], resize_keyboard=True)

def kb_sms():
    return ReplyKeyboardMarkup([
        [kbtn(BT_RFSMS, "success")],
        [kbtn(BT_NEW, "primary")],
        [kbtn(BT_STOPMON, "danger")],
        [kbtn(BT_BACK, "danger")],
    ], resize_keyboard=True)

def kb_devlist(devs, page=0):
    items = list(devs.items())[:80]
    total = len(items)
    tp = max(1, (total + DEV_PAGE - 1) // DEV_PAGE)
    page = max(0, min(page, tp - 1))
    start = page * DEV_PAGE
    rows = []
    for dev_id, info in items[start:start + DEV_PAGE]:
        phone = info.get("phone") or ""
        label = f"🟢 {dev_id[:35]}"
        if phone: label += f" | {phone}"
        rows.append([kbtn(label[:60], "success")])
    nav = []
    if page > 0: nav.append(kbtn(BT_PREV, "primary"))
    nav.append(kbtn(f"{BT_PAGE} {page+1}/{tp}", "primary"))
    if page < tp - 1: nav.append(kbtn(BT_NEXT, "primary"))
    rows.append(nav)
    rows.append([kbtn(BT_SCAN, "primary"), kbtn(BT_BACK, "danger")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def kb_admin():
    ref_lbl = f"🟢 {bold('REFERRAL ON')}" if bot_settings["referral_system"] else f"🔴 {bold('REFERRAL OFF')}"
    cred_lbl = f"🟢 {bold('CREDIT ON')}" if bot_settings["credit_system"] else f"🔴 {bold('CREDIT OFF')}"
    maint_lbl = f"🟢 {bold('BOT ON')}" if maintenance_mode else f"🔴 {bold('BOT OFF')}"
    cap_lbl = f"🔐 {bold('CAPTCHA ON')}" if captcha_enabled else f"🔓 {bold('CAPTCHA OFF')}"
    return ReplyKeyboardMarkup([
        [kbtn(BT_RX, "primary"), kbtn(BT_FX, "success")],
        [kbtn(ref_lbl, "success"), kbtn(cred_lbl, "success")],
        [kbtn(BT_REFHRS, "primary"), kbtn(BT_CREDCFG, "primary")],
        [kbtn(BT_AUTOSTOP, "primary")],
        [kbtn(BT_ADDFB, "success"), kbtn(BT_BULK, "success")],
        [kbtn(BT_MNGFB, "primary"), kbtn(BT_TOTAL, "primary")],
        [kbtn(BT_FBTIERS, "primary")],
        [kbtn(BT_USERS, "primary"), kbtn(BT_UFBS, "primary")],
        [kbtn(BT_LOGGER, "success"), kbtn(BT_STATS, "primary")],
        [kbtn(BT_GIFT, "success"), kbtn(BT_BCAST, "success")],
        [kbtn(BT_COLORS, "primary"), kbtn(cap_lbl, "primary")],
        [kbtn(BT_ADDCH, "success"), kbtn(BT_MNGCH, "primary")],
        [kbtn(maint_lbl, "danger")],
        [kbtn(BT_BACK, "danger")],
    ], resize_keyboard=True)

def kb_rx(page=0):
    total = len(ALLOWED_REACTIONS)
    tp = max(1, (total + RX_PAGE - 1) // RX_PAGE)
    page = max(0, min(page, tp - 1))
    start = page * RX_PAGE; end = min(start + RX_PAGE, total)
    en = bot_settings.get("enabled_reactions", [])
    rows = []
    for i in range(start, end, RX_COLS):
        row = []
        for j in range(RX_COLS):
            idx = i + j
            if idx >= end: break
            e = ALLOWED_REACTIONS[idx]
            mark = "✅" if e in en else "❌"
            row.append(kbtn(f"{mark}{e}", "success" if e in en else "danger"))
        rows.append(row)
    rows.append([kbtn(BT_PREV, "primary"), kbtn(f"{BT_PAGE} {page+1}/{tp}", "primary"), kbtn(BT_NEXT, "primary")])
    rows.append([kbtn(BT_SELALL, "success"), kbtn(BT_DESELALL, "danger")])
    rows.append([kbtn(BT_BACKBTN, "danger")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def kb_fx():
    en = bot_settings.get("enabled_effects", [])
    rows = []
    for k, info in ALLOWED_EFFECTS.items():
        is_on = k in en
        mark = "✅" if is_on else "❌"
        rows.append([kbtn(f"{mark} {info['emoji']} {bold(info['label'])}", "success" if is_on else "danger")])
    rows.append([kbtn(BT_SELALL, "success"), kbtn(BT_DESELALL, "danger")])
    rows.append([kbtn(BT_BACKBTN, "danger")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def kb_users(page=0):
    users = sorted(known_users)
    tp = max(1, (len(users) + UL_PAGE - 1) // UL_PAGE)
    page = max(0, min(page, tp - 1))
    start = page * UL_PAGE
    rows = []
    for uid in users[start:start + UL_PAGE]:
        rec = REFERRAL_DB.get(str(uid), {})
        un = rec.get("username") or ""
        mark = "🚫" if is_banned(uid) else "👤"
        label = f"{mark} {('@'+un) if un else bold('User')} · {uid}"
        rows.append([kbtn(label[:60], "danger" if is_banned(uid) else "primary")])
    rows.append([kbtn(BT_PREV, "primary"), kbtn(f"{BT_PAGE} {page+1}/{tp}", "primary"), kbtn(BT_NEXT, "primary")])
    rows.append([kbtn(BT_ADMINBACK, "danger")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def kb_user_detail(uid):
    uc = _uc(uid); banned = uc.get("banned", False)
    return ReplyKeyboardMarkup([
        [kbtn(BT_UDGIFT, "success")],
        [kbtn(BT_UADDREF, "primary"), kbtn(BT_UGIFTCRED, "primary")],
        [kbtn(BT_UUNBAN if banned else BT_UBAN, "success" if banned else "danger")],
        [kbtn(BT_UBACK, "danger")],
    ], resize_keyboard=True)

def kb_fb(page=0):
    total = len(global_fb_list)
    if total == 0:
        return ReplyKeyboardMarkup([
            [kbtn(BT_ADDFB, "success"), kbtn(BT_BULK, "success")],
            [kbtn(BT_ADMINBACK, "danger")],
        ], resize_keyboard=True)
    tp = max(1, (total + FB_PAGE - 1) // FB_PAGE)
    page = max(0, min(page, tp - 1))
    start = page * FB_PAGE
    rows = []
    for i in range(start, min(start + FB_PAGE, total)):
        url, tag = global_fb_list[i]
        rows.append([kbtn(f"🔄 {tag}", "success"), kbtn(f"🗑 {tag}", "danger")])
    rows.append([kbtn(BT_PREV, "primary"), kbtn(f"{BT_PAGE} {page+1}/{tp}", "primary"), kbtn(BT_NEXT, "primary")])
    rows.append([kbtn(BT_REFRESH, "success")])
    rows.append([kbtn(BT_ADDFB, "success"), kbtn(BT_BULK, "success")])
    rows.append([kbtn(BT_ADMINBACK, "danger")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

TIER_LOW_MAX = 10      # 1-10 online devices
TIER_MID_MAX = 50      # 11-50 online devices  (51+ = HIGH)

def _fb_tier_buckets():
    per = dev_cache.get("per_fb", {}) or {}
    low, mid, high = [], [], []
    for u, t in global_fb_list:
        on = int((per.get(t) or {}).get("online", 0))
        off = int((per.get(t) or {}).get("offline", 0))
        row = (u, t, on, off)
        if on <= TIER_LOW_MAX: low.append(row)
        elif on <= TIER_MID_MAX: mid.append(row)
        else: high.append(row)
    for b in (low, mid, high): b.sort(key=lambda r: r[2])
    return low, mid, high

def kb_fb_tiers():
    low, mid, high = _fb_tier_buckets()
    return ReplyKeyboardMarkup([
        [kbtn(f"{BT_TIER_LOW} ({len(low)})", "success")],
        [kbtn(f"{BT_TIER_MID} ({len(mid)})", "primary")],
        [kbtn(f"{BT_TIER_HIGH} ({len(high)})", "danger")],
        [kbtn(BT_ADMINBACK, "danger")],
    ], resize_keyboard=True)

def cap_fb_tiers():
    low, mid, high = _fb_tier_buckets()
    return (
        f"🎚 <b>DEVICE TIERS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 <b>LOW</b> (1–{TIER_LOW_MAX} online): <b>{len(low)}</b> FBs\n"
        f"🟡 <b>MID</b> ({TIER_LOW_MAX+1}–{TIER_MID_MAX} online): <b>{len(mid)}</b> FBs\n"
        f"🔴 <b>HIGH</b> ({TIER_MID_MAX+1}+ online): <b>{len(high)}</b> FBs\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 {dev_cache.get('updated_at','—')}\n"
        f"<i>Tap a tier to see the list, sorted low → high</i>"
    )

def cap_fb_tier_list(tier):
    low, mid, high = _fb_tier_buckets()
    rows, label, emoji = {"low": (low, "LOW", "🟢"), "mid": (mid, "MID", "🟡"),
                           "high": (high, "HIGH", "🔴")}[tier][0], \
                          {"low": "LOW", "mid": "MID", "high": "HIGH"}[tier], \
                          {"low": "🟢", "mid": "🟡", "high": "🔴"}[tier]
    lines = [f"{emoji} <b>{label} TIER</b>", "━━━━━━━━━━━━━━━━━━━━━━━━"]
    if not rows:
        lines.append("<i>— Empty —</i>")
    else:
        for u, t, on, off in rows:
            lines.append(f"<b>{t}</b>  🟢{on} | 🔴{off} | 📊{on+off}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"<b>Total in tier:</b> {len(rows)}")
    return "\n".join(lines)

def kb_colors():
    c = bot_settings["button_colors"]
    return ReplyKeyboardMarkup([
        [kbtn(f"🔵 {bold('PRIMARY')}: {c.get('primary','primary')}", "primary")],
        [kbtn(f"🟢 {bold('SUCCESS')}: {c.get('success','success')}", "success")],
        [kbtn(f"🔴 {bold('DANGER')}: {c.get('danger','danger')}", "danger")],
        [kbtn(BT_ADMINBACK, "danger")],
    ], resize_keyboard=True)

def kb_gift():
    return ReplyKeyboardMarkup([
        [kbtn(BT_GSINGLE, "primary")],
        [kbtn(BT_GALL, "success")],
        [kbtn(BT_ADMINBACK, "danger")],
    ], resize_keyboard=True)

def kb_logger():
    auto = "🔴 AUTO OFF" if LOGGER_SETTINGS.get("auto_backup") else "🟢 AUTO ON"
    return ReplyKeyboardMarkup([
        [kbtn(BT_LOGSET, "primary")],
        [kbtn(BT_LOGBK, "success"), kbtn(BT_LOGRES, "danger")],
        [kbtn(auto, "danger")],
        [kbtn(BT_LOG6, "primary"), kbtn(BT_LOG12, "primary"), kbtn(BT_LOG24, "primary")],
        [kbtn(BT_ADMINBACK, "danger")],
    ], resize_keyboard=True)

def kb_verify():
    return ReplyKeyboardMarkup([[kbtn(BT_VERIFY, "success")]], resize_keyboard=True)

def kb_cancel():
    return ReplyKeyboardMarkup([[kbtn(BT_CANCEL, "danger")]], resize_keyboard=True)

def _custom_kb(uid):
    r = _ufb(uid)
    rows = []
    if r["mode"] == "on": rows.append([kbtn(f"🔴 {bold('TURN PRIVATE OFF')}", "danger")])
    else: rows.append([kbtn(f"🟢 {bold('TURN PRIVATE ON')}", "success")])
    if len(r["fbs"]) < MAX_USER_FB:
        rows.append([kbtn(f"➕ {bold('ADD FIREBASE')}", "success")])
    for i in range(len(r["fbs"])):
        rows.append([kbtn(f"🗑 {bold('DELETE')} #{i+1}", "danger")])
    rows.append([kbtn(BT_BACK, "danger")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

ALL_BTNS = {BT_GEN, BT_NEW, BT_SCAN, BT_REFER, BT_SPIN, BT_CUSTOM, BT_LB, BT_PROF,
            BT_ADMIN, BT_BACK, BT_SMS, BT_RFSMS, BT_STOPMON, BT_RX, BT_FX,
            BT_REFHRS, BT_CREDCFG, BT_ADDFB, BT_BULK, BT_MNGFB, BT_TOTAL, BT_REFRESH,
            BT_AUTOSTOP, BT_FBTIERS, BT_TIER_LOW, BT_TIER_MID, BT_TIER_HIGH,
            BT_USERS, BT_UFBS, BT_LOGGER, BT_STATS, BT_GIFT, BT_BCAST,
            BT_COLORS, BT_ADDCH, BT_MNGCH, BT_ADMINBACK, BT_BACKBTN,
            BT_SELALL, BT_DESELALL, BT_PREV, BT_NEXT, BT_UDGIFT, BT_UADDREF,
            BT_UGIFTCRED, BT_UBAN, BT_UUNBAN, BT_UBACK, BT_GSINGLE, BT_GALL,
            BT_VERIFY, BT_LOGSET, BT_LOGBK, BT_LOGRES, BT_LOG6, BT_LOG12,
            BT_LOG24, BT_CANCEL}

def _is_btn(text):
    if text in ALL_BTNS: return True
    if text.startswith(BT_PAGE): return True
    if text.startswith("🔄 FB") or text.startswith("🗑 FB"): return True
    if text.startswith(("✅", "❌", "👤", "🚫", "🔵", "🟢", "🔴", "🟡", "🔓", "🔐", "⏰", "⏲", "🎚", "💎", "🛠", "➕", "🗑", "🔄")): return True
    if " FBs" in text or " | " in text: return True
    return False

def _uid_from_user_btn(text):
    try:
        m = re.search(r"·\s*(\d+)\s*$", text)
        return int(m.group(1)) if m else None
    except: return None

def _uid_from_cfb_btn(text):
    try:
        m = re.search(r"User\s+(\d+)", text)
        return int(m.group(1)) if m else None
    except: return None

def _dev_id_from_button(text):
    try:
        t = text.lstrip("🟢 ").strip()
        if " | " in t: return t.split(" | ")[0].strip()
        return t
    except: return None

# ═══════════════════════════ REFERRAL ═══════════════════════════
def _urec(uid):
    s = str(uid)
    if s not in REFERRAL_DB:
        REFERRAL_DB[s] = {"access_expires_at": 0.0, "referrals": [], "referred_by": None,
                          "pending_referrer": None, "referral_count": 0,
                          "expired_notified": False, "cooldown_until": 0.0,
                          "captcha_verified": False, "is_verified": False, "username": ""}
    r = REFERRAL_DB[s]
    for k, v in [("access_expires_at", 0.0), ("referrals", []), ("referred_by", None),
                 ("pending_referrer", None), ("referral_count", len(r.get("referrals", []))),
                 ("expired_notified", False), ("cooldown_until", 0.0),
                 ("captcha_verified", False), ("is_verified", False), ("username", "")]:
        r.setdefault(k, v)
    return r

def remaining_sec(uid):
    if uid in ADMIN_IDS: return float("inf")
    return max(0.0, _urec(uid).get("access_expires_at", 0.0) - time.time())

def has_access(uid):
    if uid in ADMIN_IDS: return True
    return remaining_sec(uid) > 0

def fmt_time(uid):
    if uid in ADMIN_IDS: return "Unlimited ♾️"
    r = remaining_sec(uid)
    if r <= 0: return "Expired"
    m = int(r // 60); h = m // 60; m = m % 60
    if h > 0 and m > 0: return f"{h}h {m}m"
    if h > 0: return f"{h}h"
    return f"{m}m"

def grant(uid, sec):
    r = _urec(uid); now = time.time()
    cur = r.get("access_expires_at", 0.0)
    r["access_expires_at"] = (now if cur < now else cur) + sec
    r["expired_notified"] = False; _sv_ref()

async def proc_ref(ref_id, new_id):
    global _ref_lock
    if _ref_lock is None: _ref_lock = asyncio.Lock()
    async with _ref_lock:
        if ref_id == new_id: return {"success": False}
        rr = _urec(ref_id); nr = _urec(new_id)
        if nr.get("referred_by") is not None or new_id in rr.get("referrals", []):
            return {"success": False}
        if ref_id not in ADMIN_IDS and bot_settings.get("referral_system"):
            now = time.time(); cur = rr.get("access_expires_at", 0.0)
            rr["access_expires_at"] = (now if cur < now else cur) + ref_sec()
            rr["expired_notified"] = False
        rr.setdefault("referrals", []).append(new_id)
        rr["referral_count"] = len(rr["referrals"])
        nr["referred_by"] = ref_id; nr["pending_referrer"] = None; nr["is_verified"] = True
        _sv_ref()
        return {"success": True, "remaining": fmt_time(ref_id), "count": rr["referral_count"]}

async def fin_ref(bot, new_id, uname):
    r = _urec(new_id); r["username"] = uname; _sv_ref()
    ref_id = r.get("pending_referrer")
    if not ref_id: return False
    res = await proc_ref(ref_id, new_id)
    r["pending_referrer"] = None; r["is_verified"] = True; _sv_ref()
    if res.get("success"):
        try:
            await bot.send_message(chat_id=ref_id, text=(
                f"🎉 <b>REFERRAL VERIFIED!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <code>{new_id}</code>\n"
                f"🎁 <b>+{ref_h()} Hours</b>\n"
                f"⏳ <b>Total:</b> {res.get('remaining')}\n"
                f"👥 <b>Refers:</b> {res.get('count')}"), parse_mode="HTML")
        except: pass
    return True

async def check_left(uid):
    try:
        rec = REFERRAL_DB.get(str(uid))
        if not rec: return None
        ref_id = rec.get("referred_by")
        if not ref_id or str(ref_id) not in REFERRAL_DB: return None
        rr = REFERRAL_DB[str(ref_id)]
        if uid not in rr.get("referrals", []): return None
        rr["referrals"] = [r for r in rr.get("referrals", []) if r != uid]
        rr["referral_count"] = len(rr["referrals"])
        if ref_id not in ADMIN_IDS:
            cur = rr.get("access_expires_at", 0.0)
            rr["access_expires_at"] = max(time.time(), cur - ref_sec())
        rec["referred_by"] = None; _sv_ref()
        return ref_id
    except: return None

def _ufb(uid):
    r = USER_CUSTOM_FBS.get(str(uid))
    if not isinstance(r, dict): r = {"mode": "off", "fbs": []}; USER_CUSTOM_FBS[str(uid)] = r
    r.setdefault("mode", "off"); r.setdefault("fbs", [])
    return r

def is_private(uid):
    r = USER_CUSTOM_FBS.get(str(uid))
    return bool(r and r.get("mode") == "on")

# ═══════════════════════════ BACKUP ═══════════════════════════
BACKUP_FILES = [
    ("referrals.json", lambda: REFERRAL_DB),
    ("global_firebases.json", lambda: [{"url": u, "tag": t} for u, t in global_fb_list]),
    ("bot_users.json", lambda: sorted(known_users)),
    ("user_custom_fbs.json", lambda: USER_CUSTOM_FBS),
    ("force_join_channels.json", lambda: REQUIRED_CHANNELS),
    ("maintenance_mode.json", lambda: {"enabled": maintenance_mode}),
    ("captcha_state.json", lambda: {"enabled": captcha_enabled}),
    ("logger_settings.json", lambda: LOGGER_SETTINGS),
    ("bot_settings.json", lambda: bot_settings),
    ("user_credits.json", lambda: user_credits),
]

def _mk_backup():
    fd, tmp = tempfile.mkstemp(suffix=".db"); os.close(fd)
    c = sqlite3.connect(tmp)
    try:
        c.execute("CREATE TABLE backup (filename TEXT PRIMARY KEY, content TEXT, updated_at TEXT)")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for fn, gt in BACKUP_FILES:
            try:
                content = json.dumps(gt(), ensure_ascii=False, default=str)
                c.execute("INSERT OR REPLACE INTO backup VALUES (?, ?, ?)", (fn, content, now))
            except: pass
        c.commit()
    finally: c.close()
    with open(tmp, "rb") as f: d = f.read()
    try: os.unlink(tmp)
    except: pass
    return d

async def _send_backup(bot, manual=False):
    ch = (LOGGER_SETTINGS.get("channel") or "").strip()
    if not ch: return False, "No channel set"
    try:
        data = _mk_backup()
        fn = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        await bot.send_document(chat_id=ch, document=BytesIO(data), filename=fn,
            caption=(f"📁 *{BOT_BRAND} BACKUP* {'(Manual)' if manual else '(Auto)'}\n"
                     f"🕒 `{datetime.now().strftime('%d-%m-%Y %I:%M %p')}`\n📦 `{len(data)}` bytes"),
            parse_mode="Markdown")
        LOGGER_SETTINGS["last_backup_at"] = time.time(); _sv_log()
        return True, fn
    except Exception as e: return False, str(e)

async def _auto_bk_loop(bot):
    while True:
        try:
            await asyncio.sleep(60)
            if not LOGGER_SETTINGS.get("auto_backup"): continue
            ch = (LOGGER_SETTINGS.get("channel") or "").strip()
            if not ch: continue
            if time.time() - float(LOGGER_SETTINGS.get("last_backup_at", 0) or 0) >= int(LOGGER_SETTINGS.get("interval_hours", 6) or 6) * 3600:
                await _send_backup(bot)
        except asyncio.CancelledError: raise
        except: await asyncio.sleep(60)

# ═══════════════════════════ FIREBASE ═══════════════════════════
def norm_fb(u):
    try:
        if not u or not isinstance(u, str): return None
        u = u.strip()
        if not u.startswith("http"): return None
        if "firebaseio.com" not in u and "firebasedatabase.app" not in u: return None
        u = u.rstrip("/")
        while u.endswith(".json"): u = u[:-5].rstrip("/")
        return u
    except: return None

dev_cache = _ld(DEV_CACHE_FILE, {"devices": {}, "online_count": 0, "offline_count": 0, "per_fb": {}, "updated_at": ""})
if not isinstance(dev_cache.get("devices"), dict):
    dev_cache = {"devices": {}, "online_count": 0, "offline_count": 0, "per_fb": {}, "updated_at": ""}
dev_cache.setdefault("per_fb", {})
def _sv_cache(): _sv(DEV_CACHE_FILE, dev_cache)

def ep(base, path="", q=""):
    b = base.rstrip("/"); p = (path or "").strip("/"); qq = (q or "").strip().lstrip("?")
    u = f"{b}/{p}/.json" if p else f"{b}/.json"
    if qq: u += f"?{qq}"
    return u

async def fb_get(url, *, t=FB_TIMEOUT, mb=50*1024*1024, retries=1):
    sess = get_session()
    err = ""
    for att in range(retries + 1):
        try:
            async with sess.get(url, timeout=aiohttp.ClientTimeout(total=t)) as r:
                s = r.status
                if s == 413: return None, "TOO_LARGE", "413"
                cl = r.headers.get("Content-Length")
                if cl and cl.isdigit() and int(cl) > mb: return None, "TOO_LARGE", "big"
                body = b""
                async for ch in r.content.iter_chunked(8192):
                    body += ch
                    if len(body) > mb: return None, "TOO_LARGE", "big"
                txt = body.decode("utf-8", errors="ignore").strip()
                if s in (401, 403): return None, "DENIED", str(s)
                if s == 404: return None, "NF", "404"
                if s in (408, 504) or s == 429 or 500 <= s < 600:
                    err = str(s)
                    if att < retries: await asyncio.sleep(1.2 ** att); continue
                    return None, "HTTP", err
                if s >= 400: return None, "HTTP", str(s)
                if not txt or txt == "null": return None, "EMPTY", "null"
                try: return json.loads(txt), "OK", ""
                except: return None, "JSON", "decode"
        except asyncio.TimeoutError:
            err = "to"
            if att < retries: await asyncio.sleep(1.2 ** att); continue
            return None, "TO", err
        except Exception as e: return None, "OTHER", str(e)[:60]
    return None, "OTHER", err

def _dname(info, cid):
    if not isinstance(info, dict): return cid
    for k in ("modelName", "model", "deviceName", "name"):
        v = info.get(k)
        if v and str(v).strip() and str(v) != "-": return str(v).strip()
    return cid

def _mob(info):
    if not isinstance(info, dict): return ""
    raw = (info.get("mobNo") or info.get("mob_no") or info.get("mobile") or
           info.get("phoneNumber") or info.get("phone") or "")
    if not raw: return ""
    d = re.sub(r"\D", "", str(raw))
    if len(d) == 12 and d.startswith("91"): d = d[2:]
    elif len(d) == 11 and d.startswith("0"): d = d[1:]
    return d if len(d) == 10 and d[0] in "6789" else ""

def _newkeys(m, lim=5):
    if isinstance(m, list):
        out = []
        for i, v in list(enumerate(m))[-lim:][::-1]:
            if isinstance(v, dict): out.append((str(i), v))
        return out
    if not isinstance(m, dict): return []
    def tok(k):
        s = str(k)
        try: return (0, int(s), "")
        except: return (1, 0, s)
    return [(str(k), m[k]) for k in sorted(m.keys(), key=tok, reverse=True)[:lim] if isinstance(m.get(k), dict)]

def _body(m):
    if not isinstance(m, dict): return ""
    for k in ("body","message","msg","text","content","sms","smsBody","messageBody","SMS","msgBody"):
        v = m.get(k)
        if v and str(v).strip(): return str(v).strip()
    return ""

def _sender(m):
    if not isinstance(m, dict): return "Unknown"
    for k in ("sender","from","address","number","phone","phoneNumber","mobile","mobNo","src","originator","senderNumber","fromNumber"):
        v = m.get(k)
        if not v: continue
        s = str(v).strip()
        if not s: continue
        low = s.lower()
        if low in ("webhookevent", "null", "none", "undefined", "true", "false"): continue
        if len(s) == 1 and s.isdigit(): continue
        return s
    return "Unknown"

def _ftime(ts):
    if not ts: return "Unknown"
    try:
        s = str(ts).strip()
        if re.fullmatch(r"\d+", s):
            n = int(s)
            if n > 10**12: n //= 1000
            elif n < 10**9: return s
            return datetime.fromtimestamp(n).strftime("%d-%m-%Y | %I:%M %p")
        return s
    except: return str(ts)

def _mtime(m, fb=""):
    if isinstance(m, dict):
        for k in ("time","timestamp","date","receivedTime","received_at","sentTime","dateTime","createdAt"):
            v = m.get(k)
            if v and str(v).strip():
                ft = _ftime(v)
                if ft and ft != "Unknown" and ft.lower() not in ("webhookevent","null","none"):
                    return ft
    if fb:
        ft = _ftime(fb)
        if ft and (re.match(r"\d{2}-\d{2}-\d{4}", ft) or re.match(r"\d{4}-\d{2}-\d{2}", ft)):
            return ft
    return "Unknown"

def _extract_msg_time_sec(m):
    """Extract message timestamp as seconds since epoch, or None."""
    if not isinstance(m, dict): return None
    for k in ("time","timestamp","date","receivedTime","received_at","sentTime","dateTime","createdAt"):
        v = m.get(k)
        if not v: continue
        try:
            n = int(str(v).strip())
            if n > 10**12: return n // 1000  # ms
            if n > 10**9: return n           # sec
            return None
        except: pass
    return None

def _otp(body):
    if not body: return None
    txt = str(body).replace("\u200b", " ").replace("\u00a0", " ").replace("\u2060", " ")
    # Strong patterns: OTP keyword + nearby digits
    strong = [
        r"\b(?:OTP|code|verification|verify|login|passcode|pin)\D{0,30}(\d{4,8})\b",
        r"\b(\d{4,8})\D{0,30}(?:OTP|code|verification|verify|login|passcode|pin)\b",
    ]
    for pat in strong:
        mm = re.search(pat, txt, re.I)
        if mm and mm.group(1).isdigit() and 4 <= len(mm.group(1)) <= 8:
            return mm.group(1)
    # "is <code>" only if OTP-ish keyword present
    if re.search(r"\b(?:OTP|code|verify|login|pin|verification)\b", txt, re.I):
        mm = re.search(r"\b(?:is|hai|are|:)\s*(\d{4,8})\b", txt, re.I)
        if mm and mm.group(1).isdigit() and 4 <= len(mm.group(1)) <= 8:
            return mm.group(1)
    return None

def _fp(k, m): return f"{k}|{_sender(m)}|{_body(m)}"

def _phone_from_msgs(msgs):
    try:
        if not isinstance(msgs, dict): return None
        cnt = Counter()
        for _, m in _newkeys(msgs, 15):
            if not isinstance(m, dict): continue
            txt = _body(m)
            for pat in _PHONE_RX:
                for n in pat.findall(txt):
                    d = re.sub(r'\D', '', n)
                    if len(d) == 10 and d[0] in '6789': cnt[d] += 1
                    elif len(d) == 12 and d.startswith('91') and d[2] in '6789': cnt[d[2:]] += 1
        return cnt.most_common(1)[0][0] if cnt else None
    except: return None

async def _try_clients(fb, retries=1):
    d, s, _ = await fb_get(ep(fb, ""), retries=retries)
    if s == "OK" and isinstance(d, dict):
        cl = d.get("clients") if isinstance(d.get("clients"), dict) else \
             d.get("devices") if isinstance(d.get("devices"), dict) else None
        ms = d.get("messages") if isinstance(d.get("messages"), dict) else {}
        if cl: return cl, ms
    (cd, cs, _), (dd, ds, _) = await asyncio.gather(
        fb_get(ep(fb, "clients"), retries=0),
        fb_get(ep(fb, "devices"), retries=0))
    if cs == "OK" and isinstance(cd, dict) and cd: return cd, {}
    if ds == "OK" and isinstance(dd, dict) and dd: return dd, {}
    return {}, {}

async def _phone_lookup(fb, cid):
    try:
        m = ep(fb, f"messages/{cid}", 'orderBy="$key"&limitToLast=15')
        f, s, _ = await fb_get(m, t=4, retries=0)
        if s == "OK" and isinstance(f, dict): return cid, _phone_from_msgs(f)
    except: pass
    return cid, None

async def fetch_devs(fb, tag, online=True, pre=None, retries=0):
    out = {}
    try:
        cl, msgs = pre or await _try_clients(fb, retries=retries)
        if not cl: return {}
        pl = {}
        ids = [str(c) for c, info in cl.items()
               if isinstance(info, dict) and (not online or info.get("status") is True)
               and not _mob(info) and not isinstance(msgs.get(c), dict)][:20]
        if ids:
            res = await asyncio.gather(*[_phone_lookup(fb, c) for c in ids], return_exceptions=True)
            pl = {c: p for r in res if isinstance(r, tuple) for c, p in [r] if p}
        for cid, info in cl.items():
            try:
                if not isinstance(info, dict): continue
                on = info.get("status") is True
                if online and not on: continue
                if not online and on: continue
                p = _mob(info)
                if not p:
                    md = msgs.get(cid) if isinstance(msgs, dict) else None
                    if not isinstance(md, dict):
                        e = pl.get(str(cid))
                        if e: p = e
                    if isinstance(md, dict) and md:
                        e = _phone_from_msgs(md)
                        if e: p = e
                if not p: continue
                out[f"{tag}|{cid}"] = {"name": _dname(info, cid), "phone": p, "raw": info,
                                       "online": on, "fb_url": fb, "fb_tag": tag, "real_cid": cid}
            except: continue
        return out
    except Exception:
        return {}

async def fetch_counts(fb, tag, pre=None, retries=0):
    try:
        cl, _ = pre or await _try_clients(fb, retries=retries)
        if not cl: return 0, 0
        on = off = 0
        for _, info in cl.items():
            if not isinstance(info, dict): continue
            if info.get("status") is True: on += 1
            else: off += 1
        return on, off
    except Exception:
        return 0, 0

async def counts_all(fbs, pre=None, retries=0):
    pre = pre or {}
    sem = asyncio.Semaphore(FB_CONC)
    async def lim(u, t):
        async with sem: return await fetch_counts(u, t, pre.get(u), retries=retries)
    res = await asyncio.gather(*[lim(u, t) for u, t in fbs], return_exceptions=True)
    on = off = 0; per = {}
    for (u, t), r in zip(fbs, res):
        if isinstance(r, Exception) or not r: per[t] = {"online": 0, "offline": 0}; continue
        per[t] = {"online": r[0], "offline": r[1]}; on += r[0]; off += r[1]
    return on, off, per

async def devs_all(fbs, online=True, max_per=100, pre=None, retries=0):
    pre = pre or {}
    sem = asyncio.Semaphore(FB_CONC)
    async def lim(u, t):
        async with sem: return await fetch_devs(u, t, online, pre.get(u), retries=retries)
    res = await asyncio.gather(*[lim(u, t) for u, t in fbs], return_exceptions=True)
    out = {}
    for r in res:
        if isinstance(r, Exception) or not r: continue
        for k, v in list(r.items())[:max_per]: out[k] = v
    return out

async def fetch_sms(fb, dev, lim=5):
    try:
        q = urllib.parse.urlencode({"orderBy": '"$key"', "limitToLast": lim})
        d, s, _ = await fb_get(ep(fb, f"messages/{dev}", q), t=4, retries=0)
        if s == "OK" and isinstance(d, (dict, list)) and d: return _newkeys(d, lim)
        d, s, _ = await fb_get(ep(fb, f"messages/{dev}"), t=4, retries=0)
        if s == "OK" and isinstance(d, (dict, list)) and d: return _newkeys(d, lim)
        return []
    except Exception:
        return []

async def refresh_cache(only=None):
    global dev_cache, _last_refresh
    only_set = set(only) if only else None
    targets = ([(u, t) for u, t in global_fb_list if u in only_set]
               if only_set is not None else list(global_fb_list))

    if not targets:
        if only_set is None:
            dev_cache = {"devices": {}, "online_count": 0, "offline_count": 0, "per_fb": {},
                         "updated_at": datetime.now().strftime("%d-%m-%Y %H:%M")}
            await _sv_async(DEV_CACHE_FILE, dev_cache)
            _last_refresh = time.monotonic()
        return
    try:
        dtsk = devs_all(targets, online=True, max_per=150)
        ctsk = counts_all(targets)
        devs, (on, off, per) = await asyncio.gather(dtsk, ctsk)
        per = per or {}
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M")
        if only_set is None:
            dev_cache = {"devices": devs or {}, "online_count": len(devs or {}),
                         "offline_count": off, "per_fb": per, "updated_at": now_str}
            _last_refresh = time.monotonic()
        else:
            merged_devs = dict(dev_cache.get("devices") or {})
            for u, _t in targets:
                for k in [k for k, v in merged_devs.items() if v.get("fb_url") == u]:
                    del merged_devs[k]
            merged_devs.update(devs or {})
            merged_per = dict(dev_cache.get("per_fb") or {})
            merged_per.update(per)
            total_off = sum(int(c.get("offline", 0)) for c in merged_per.values())
            dev_cache = {"devices": merged_devs, "online_count": len(merged_devs),
                         "offline_count": total_off, "per_fb": merged_per, "updated_at": now_str}
        await _sv_async(DEV_CACHE_FILE, dev_cache)
    except Exception:
        pass

async def _refresh_loop():
    global _last_refresh
    while True:
        try:
            await refresh_cache(); _last_refresh = time.monotonic()
            await asyncio.sleep(ADMIN_REFRESH)
        except asyncio.CancelledError: raise
        except: await asyncio.sleep(ADMIN_REFRESH)

def _sec_until_refresh():
    return max(0, int(ADMIN_REFRESH - (time.monotonic() - _last_refresh)))

async def _admin_live_loop(bot, uid, chat_id, msg_id):
    last = ""
    try:
        while True:
            await asyncio.sleep(ADMIN_LIVE)
            if uid not in admin_live_tasks: break
            page = user_sessions.get(uid, {}).get("fb_page", 0)
            text = cap_fb_list(page)
            if text == last: continue
            try:
                await bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                                            text=text, parse_mode="HTML")
                last = text
            except BadRequest as e:
                m = str(e).lower()
                if "not modified" in m: last = text; continue
                if "not found" in m or "can't be edited" in m: break
            except NetworkError: continue
            except Exception as e: logger.debug(f"admin live: {e}")
    except asyncio.CancelledError: raise
    finally: admin_live_tasks.pop(uid, None)

def _stop_admin_live(uid):
    t = admin_live_tasks.pop(uid, None)
    if t and not t.done(): t.cancel()

async def _start_admin_live(bot, uid, chat_id, msg_id):
    _stop_admin_live(uid)
    admin_live_tasks[uid] = asyncio.create_task(_admin_live_loop(bot, uid, chat_id, msg_id))

# ═══════════════════════════ FORCE JOIN ═══════════════════════════
def _is_mem(s): return s in {"member", "administrator", "creator"}
def _skip_err(e):
    e = e.lower()
    return any(x in e for x in ["chat not found", "bot is not a member", "not enough rights",
                                  "user not found", "chat_admin_required", "channel_invalid"])

async def unjoined(bot, uid):
    if uid in ADMIN_IDS: return []
    u = []
    for ch in REQUIRED_CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch["id"], user_id=uid)
            if not _is_mem(m.status): u.append(ch)
        except Exception as e:
            if _skip_err(str(e)): continue
            u.append(ch)
    return u

async def force_ok(bot, uid):
    if uid in ADMIN_IDS or not REQUIRED_CHANNELS: return True
    for ch in REQUIRED_CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch["id"], user_id=uid)
            if not _is_mem(m.status): return False
        except Exception as e:
            if _skip_err(str(e)): continue
            return False
    return True

# ═══════════════════════════ CAPTIONS ═══════════════════════════
def cap_force(name="User"):
    return (f"🔒 <b>ACCESS REQUIRED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> {OWNER_NAME}\n"
            f"👋 <b>Hello:</b> {html_escape((name or 'User')[:30])}\n\n"
            "📢 <b>Join these channels first:</b>\n"
            "Tap each link below, then press ✅ VERIFY")

def cap_main(name, uid):
    rc = _urec(uid).get("referral_count", 0)
    uc = _uc(uid)
    if bot_settings.get("credit_system"):
        cpn = int(bot_settings.get("credits_per_number", 1))
        mode_line = f"💎 <b>Credit Mode</b>  |  {cpn} credit = 1 number"
        earn_line  = f"💎 <b>Credits:</b> {uc.get('credits', 0)}"
    else:
        mode_line = f"👥 <b>Referral Mode</b>  |  1 refer = {ref_label()}"
        earn_line  = f"👥 <b>Refers:</b> {rc}"
    return (f"⚡ <b>{BOT_BRAND} OTP BOT</b> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> {OWNER_NAME}\n"
            f"👋 <b>Hello:</b> {html_escape((name or 'User')[:30])}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ <b>Access:</b> {fmt_time(uid)}\n"
            f"{earn_line}\n"
            f"⚙️ {mode_line}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 <i>Use menu buttons below</i>")

def cap_maint():
    return (f"🛠️ <b>MAINTENANCE MODE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> {OWNER_NAME}\n"
            "🔴 <b>Under maintenance</b>")

def cap_expired(uid):
    link = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
    return (f"🔒 <b>ACCESS EXPIRED</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> {OWNER_NAME}\n\n"
            f"🎁 <b>Refer 1 friend = {ref_label()}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <b>Your link:</b>\n<code>{link}</code>")

def cap_refer(uid):
    link = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
    cnt = _urec(uid).get("referral_count", 0)
    total_sec = cnt * ref_sec()
    if total_sec < 60: earned = f"{total_sec}s"
    elif total_sec < 3600: earned = f"{total_sec//60}m"
    elif total_sec < 86400: earned = f"{total_sec//3600}h"
    else: earned = f"{total_sec//86400}d"
    return (f"👥 <b>REFER & EARN</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> {OWNER_NAME}\n"
            f"🎁 <b>Per Invite:</b> +{ref_label()}\n"
            f"👥 <b>Refers:</b> {cnt}\n"
            f"⏳ <b>Access:</b> {fmt_time(uid)}\n"
            f"⚡ <b>Earned:</b> {earned}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <b>Share this link:</b>\n<code>{link}</code>")

def cap_lb():
    ent = []
    for us, rec in REFERRAL_DB.items():
        if not isinstance(rec, dict): continue
        try: u = int(us)
        except: continue
        c = int(rec.get("referral_count", 0) or 0)
        if c > 0: ent.append((u, c))
    ent.sort(key=lambda x: x[1], reverse=True)
    top = ent[:LEADER_TOP]
    medals = ["🥇", "🥈", "🥉"]
    lines = [f"🏆 <b>TOP {LEADER_TOP} REFERRERS</b>", "━━━━━━━━━━━━━━━━━━━━━━━━",
             f"👑 <b>Owner:</b> {OWNER_NAME}", "━━━━━━━━━━━━━━━━━━━━━━━━"]
    if not top: lines.append("<i>No referrals yet!</i>")
    else:
        for i, (u, c) in enumerate(top, 1):
            b = medals[i - 1] if i <= 3 else f"{i}️⃣"
            rec = REFERRAL_DB.get(str(u), {})
            un = rec.get("username")
            ident = f"@{un} · <code>{u}</code>" if un else f"User <code>{u}</code>"
            lines.append(f"{b} {ident}")
            earned_s = c * ref_sec()
            if earned_s < 3600: el = f"{earned_s//60}m"
            elif earned_s < 86400: el = f"{earned_s//3600}h"
            else: el = f"{earned_s//86400}d"
            lines.append(f"   👥 <b>{c}</b> | ⚡ <b>{el}</b>")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 Total: <b>{len(ent)}</b>")
    return "\n".join(lines)

def cap_custom(uid):
    r = _ufb(uid)
    mode = "🟢 ON" if r["mode"] == "on" else "🔴 OFF"
    lines = ["🎯 <b>CUSTOM PANEL</b>", "━━━━━━━━━━━━━━━━━━━━━━━━",
             f"🔒 <b>Private Mode:</b> {mode}",
             f"📊 <b>FBs:</b> {len(r['fbs'])}/{MAX_USER_FB}",
             "━━━━━━━━━━━━━━━━━━━━━━━━"]
    if r["fbs"]:
        for i, u in enumerate(r["fbs"], 1):
            lines.append(f"<b>{i}.</b> <code>{html_escape(u[:55])}</code>")
    else: lines.append("<i>⚠️ No FB yet</i>")
    return "\n".join(lines)

def cap_profile(uid, name):
    rec = _urec(uid); uc = _uc(uid)
    return (f"👤 <b>MY PROFILE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> {OWNER_NAME}\n"
            f"👋 <b>Name:</b> {html_escape((name or 'User')[:30])}\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ <b>Access:</b> {fmt_time(uid)}\n"
            f"👥 <b>Refers:</b> {rec.get('referral_count', 0)}\n"
            f"💎 <b>Credits:</b> {uc.get('credits', 0)}\n"
            f"📊 <b>Generated:</b> {uc.get('numbers_generated', 0)}")

def cap_settings():
    rs = "🟢 ON" if bot_settings["referral_system"] else "🔴 OFF"
    cs = "🟢 ON" if bot_settings["credit_system"] else "🔴 OFF"
    return (f"⚙️ <b>SETTINGS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 <b>Referral:</b> {rs}\n"
            f"⏰ <b>Referral Time:</b> {ref_label()} (= {ref_sec()}s)\n"
            f"💎 <b>Credit:</b> {cs}\n"
            f"💰 <b>Credits/Number:</b> {bot_settings.get('credits_per_number', 1)}\n"
            f"🎁 <b>Spin Reward:</b> {bot_settings.get('daily_spin_reward_min', 1)}-{bot_settings.get('daily_spin_reward_max', 5)}\n"
            f"💬 <b>Reactions:</b> {len(bot_settings.get('enabled_reactions', []))}/{len(ALLOWED_REACTIONS)}\n"
            f"✨ <b>Effects:</b> {len(bot_settings.get('enabled_effects', []))}/{len(ALLOWED_EFFECTS)}")

def cap_rx(page=0):
    total = len(ALLOWED_REACTIONS)
    tp = max(1, (total + RX_PAGE - 1) // RX_PAGE)
    page = max(0, min(page, tp - 1))
    en = bot_settings.get("enabled_reactions", [])
    return (f"💬 <b>REACTIONS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 Page {page+1}/{tp}\n"
            f"✅ ON: <b>{len(en)}</b> / {total}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Tap ✅/❌ to toggle</i>")

def cap_fx():
    en = bot_settings.get("enabled_effects", [])
    return (f"✨ <b>MESSAGE EFFECTS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ ON: <b>{len(en)}</b> / {len(ALLOWED_EFFECTS)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Tap to toggle. Private chats only.</i>")

def cap_logger():
    ch = LOGGER_SETTINGS.get("channel") or "Not set"
    auto = "🟢 ON" if LOGGER_SETTINGS.get("auto_backup") else "🔴 OFF"
    last = float(LOGGER_SETTINGS.get("last_backup_at", 0) or 0)
    ls = datetime.fromtimestamp(last).strftime("%d-%m-%Y %I:%M %p") if last > 0 else "Never"
    return (f"📁 <b>LOGGER & BACKUP</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📢 <b>Channel:</b> <code>{html_escape(str(ch))}</code>\n"
            f"⏰ <b>Auto:</b> {auto}\n"
            f"🕒 <b>Interval:</b> {LOGGER_SETTINGS.get('interval_hours', 6)}h\n"
            f"📅 <b>Last:</b> {ls}")

def cap_colors():
    c = bot_settings["button_colors"]
    return (f"🎨 <b>BUTTON COLORS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔵 Primary: <code>{c.get('primary')}</code>\n"
            f"🟢 Success: <code>{c.get('success')}</code>\n"
            f"🔴 Danger: <code>{c.get('danger')}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Tap to cycle</i>")

def cap_stats():
    total_cf = sum(len(r.get("fbs", [])) for r in USER_CUSTOM_FBS.values())
    return (f"📊 <b>STATISTICS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 Owner: <code>{OWNER_NAME}</code>\n"
            f"👥 Users: <b>{len(known_users)}</b>\n"
            f"🔗 Firebases: <b>{len(global_fb_list)}</b>\n"
            f"🎯 Custom FBs: <b>{total_cf}</b>\n"
            f"📢 Channels: <b>{len(REQUIRED_CHANNELS)}</b>\n"
            f"💾 Sessions: <b>{len(user_sessions)}</b>\n"
            f"📨 Monitors: <b>{len(sms_tasks)}</b>\n"
            f"🔐 Captcha: <b>{'ON' if captcha_enabled else 'OFF'}</b>\n"
            f"💬 Reactions: <b>{len(bot_settings.get('enabled_reactions', []))}/{len(ALLOWED_REACTIONS)}</b>\n"
            f"✨ Effects: <b>{len(bot_settings.get('enabled_effects', []))}/{len(ALLOWED_EFFECTS)}</b>")

def cap_fb_list(page=0):
    total = len(global_fb_list)
    if total == 0: return "📋 <b>No firebases yet</b>"
    tp = max(1, (total + FB_PAGE - 1) // FB_PAGE)
    page = max(0, min(page, tp - 1))
    start = page * FB_PAGE
    per = dev_cache.get("per_fb", {}) or {}
    lines = [f"📋 <b>MANAGE FBs — {page+1}/{tp}</b>", "━━━━━━━━━━━━━━━━━━━━━━━━"]
    for i in range(start, min(start + FB_PAGE, total)):
        url, tag = global_fb_list[i]
        c = per.get(tag) or {}
        on, off = int(c.get("online", 0)), int(c.get("offline", 0))
        lines.append(f"<b>{tag}</b> 🟢{on} | 🔴{off} | 📊{on+off}")
        lines.append(f"<code>{html_escape(url[:50])}</code>")
    to = sum(int(c.get("online", 0)) for c in per.values())
    tf = sum(int(c.get("offline", 0)) for c in per.values())
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"<b>TOTAL:</b> 🟢{to} | 🔴{tf} | 📊{to+tf}")
    rem = _sec_until_refresh(); mn, sc = divmod(rem, 60)
    lines.append(f"⏳ <b>Auto-refresh:</b> {mn}:{sc:02d}")
    return "\n".join(lines)

def cap_total():
    per = dev_cache.get("per_fb", {})
    to = sum(c.get("online", 0) for c in per.values())
    tf = sum(c.get("offline", 0) for c in per.values())
    lines = ["📈 <b>TOTAL DEVICES</b>", "━━━━━━━━━━━━━━━━━━━━━━━━",
              f"🔎 <b>Total Online Devices:</b> <code>{to}</code>",
              f"🔴 <b>Total Offline Devices:</b> <code>{tf}</code>",
              f"📱 <b>Grand Total:</b> <code>{to+tf}</code>",
              f"🌐 <b>Firebases:</b> <code>{len(global_fb_list)}</code>",
              "━━━━━━━━━━━━━━━━━━━━━━━━",
              "<b>Per-Firebase breakdown:</b>"]
    for u, t in global_fb_list:
        c = per.get(t, {}); on, off = c.get("online", 0), c.get("offline", 0)
        lines.append(f"• <b>{t}:</b> 🟢{on} | 🔴{off} | 📊{on+off}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🕒 {dev_cache.get('updated_at','—')}")
    return "\n".join(lines)

def cap_user_detail(uid):
    rec = REFERRAL_DB.get(str(uid), {})
    uc = _uc(uid)
    un = rec.get("username", "")
    return (f"👤 <b>USER DETAIL</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: @{un if un else '—'}\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"⏳ Access: {fmt_time(uid)}\n"
            f"👥 Refers: {rec.get('referral_count', 0)}\n"
            f"💎 Credits: {uc.get('credits', 0)}\n"
            f"🚫 Banned: {'YES' if uc.get('banned') else 'NO'}")

def cap_users(page=0):
    users = sorted(known_users)
    tp = max(1, (len(users) + UL_PAGE - 1) // UL_PAGE)
    page = max(0, min(page, tp - 1))
    return (f"👥 <b>USER LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 Page {page+1}/{tp}\n"
            f"👥 Total: <b>{len(users)}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Tap a user to manage</i>")

def cap_dev_list(devs, page=0):
    items = list(devs.items())[:80]
    tp = max(1, (len(items) + DEV_PAGE - 1) // DEV_PAGE)
    page = max(0, min(page, tp - 1))
    return (f"🔎 <b>ONLINE DEVICES</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total: <b>{len(items)}</b>\n"
            f"📄 Page {page+1}/{tp}\n\n"
            "<i>Tap a device to view</i>")

# ═══════════════════════════ REACTION & EFFECT ═══════════════════════════
async def start_reaction(bot, chat_id, msg_id):
    if not REACTION_OK: return
    en = bot_settings.get("enabled_reactions", [])
    if not en: return
    try:
        await bot.set_message_reaction(chat_id=chat_id, message_id=msg_id,
                                        reaction=[ReactionTypeEmoji(emoji=random.choice(en))], is_big=True)
    except: pass

async def send_effect(bot, chat_id, text, *, reply_markup=None, parse_mode="HTML"):
    en = bot_settings.get("enabled_effects", [])
    eid = None
    if en:
        ch = random.choice(en)
        if ch in ALLOWED_EFFECTS: eid = ALLOWED_EFFECTS[ch]["id"]
    if eid:
        try:
            return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode,
                                          reply_markup=reply_markup, message_effect_id=eid)
        except: pass
    return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup)

# ═══════════════════════════ ACCESS ═══════════════════════════
async def _require_access(update, context):
    user = update.effective_user; uid = user.id
    if maintenance_mode and uid not in ADMIN_IDS:
        await update.message.reply_text(cap_maint(), parse_mode="HTML", reply_markup=kb_main(uid)); return False
    if is_banned(uid) and uid not in ADMIN_IDS:
        await update.message.reply_text("🚫 <b>BANNED</b>", parse_mode="HTML", reply_markup=kb_main(uid)); return False
    if REQUIRED_CHANNELS and uid not in ADMIN_IDS:
        joined = await force_ok(context.bot, uid)
        if not joined:
            verified_users.discard(uid)
            context.user_data.pop("force_join_captcha", None)
            context.user_data.pop("force_join_verified", None)
            un = await unjoined(context.bot, uid)
            links = "\n".join(f"{i+1}. <a href=\"{c['url']}\">{c['label']}</a>" for i, c in enumerate(un))
            await update.message.reply_text(f"{cap_force(user.first_name or 'User')}\n\n{links}",
                                            parse_mode="HTML", disable_web_page_preview=True,
                                            reply_markup=kb_verify())
            return False
        rec = _urec(uid)
        if (captcha_enabled and uid not in ADMIN_IDS and uid not in verified_users
                and not context.user_data.get("force_join_verified")
                and not rec.get("captcha_verified")):
            a, b = random.randint(2, 20), random.randint(2, 20)
            op = random.choice(("+", "-", "×"))
            ans = a + b if op == "+" else a - b if op == "-" else a * b
            context.user_data["force_join_captcha"] = ans
            await update.message.reply_text(
                f"🔐 <b>HUMAN VERIFICATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👑 <b>Owner:</b> {OWNER_NAME}\n\n"
                f"🧮 <b>Solve:</b> <code>{a} {op} {b} = ?</code>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "<i>Reply with the answer number only</i>", parse_mode="HTML")
            return False
    if uid not in ADMIN_IDS and bot_settings.get("referral_system") and not bot_settings.get("credit_system"):
        if not has_access(uid):
            await update.message.reply_text(cap_expired(uid), parse_mode="HTML", reply_markup=kb_main(uid)); return False
    return True

# ═══════════════════════════ /start ═══════════════════════════
async def start_cmd(update, context):
    uid = update.effective_user.id
    fname = update.effective_user.first_name or "User"
    uname = update.effective_user.username or str(uid)
    try: await start_reaction(context.bot, update.effective_chat.id, update.message.message_id)
    except: pass
    if uid not in known_users: known_users.add(uid); _sv_uids()
    rec = _urec(uid); rec["username"] = uname; _sv_ref()
    context.user_data.pop("force_join_captcha", None)
    context.user_data.pop("force_join_verified", None)
    context.user_data.pop("awaiting_custom_fb", None)
    context.user_data.pop("admin_action", None)
    context.user_data.pop("admin_awaiting", None)
    context.user_data["kb_state"] = "main"
    if update.message and update.message.text and " " in update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1 and parts[1].startswith("ref_"):
            try:
                rid = int(parts[1][4:])
                if rid != uid and rec.get("referred_by") is None:
                    _urec(rid); rec["pending_referrer"] = rid; _sv_ref()
            except: pass
    if not await _require_access(update, context): return
    rec["is_verified"] = True; _sv_ref()
    await fin_ref(context.bot, uid, uname)
    stop_sms(uid); _stop_admin_live(uid)
    sess = await _sess(uid)
    sess.update({"devices": {}, "current_device": "", "mode": "online", "dev_page": 0})
    await send_effect(context.bot, update.effective_chat.id, cap_main(fname, uid), reply_markup=kb_main(uid))

async def _sess(uid):
    s = user_sessions.get(uid)
    if not s:
        s = {"fb_list": [], "devices": {}, "current_device": "", "mode": "online", "dev_page": 0}
        user_sessions[uid] = s
    return s

# ═══════════════════════════ GENERATE (baseline race fixed) ═══════════════════════════
async def do_generate(update, context):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    if not await _require_access(update, context): return
    if bot_settings.get("credit_system") and not bot_settings.get("referral_system"):
        uc = _uc(uid); cost = int(bot_settings.get("credits_per_number", 1))
        if uid not in ADMIN_IDS and uc.get("credits", 0) < cost:
            await update.message.reply_text(
                f"💎 <b>INSUFFICIENT CREDITS</b>\nRequired: {cost}\nYour: {uc.get('credits', 0)}",
                parse_mode="HTML", reply_markup=kb_main(uid)); return
    sess = await _sess(uid)
    private = is_private(uid)
    if private:
        r = _ufb(uid); fbs = r["fbs"]
        if not fbs:
            await update.message.reply_text("⚠️ <b>PRIVATE — NO FBs</b>", parse_mode="HTML",
                                            reply_markup=kb_main(uid)); return
        pairs = [(u, f"USER{i+1}") for i, u in enumerate(fbs)]
        await update.message.reply_text("⏳ <b>Fetching devices...</b>", parse_mode="HTML")
        devs = await devs_all(pairs, online=True, max_per=100)
    else:
        if not global_fb_list:
            await update.message.reply_text("⚠️ <b>NO FIREBASES</b>", parse_mode="HTML",
                                            reply_markup=kb_main(uid)); return
        devs = dict(dev_cache.get("devices") or {})
        if not devs:
            await update.message.reply_text("⚠️ <b>CACHE EMPTY</b>\n\nWait 1 min, cache refreshing...",
                                            parse_mode="HTML", reply_markup=kb_main(uid)); return
    if not devs:
        await update.message.reply_text("⚠️ <b>NO ONLINE DEVICES</b>", parse_mode="HTML",
                                        reply_markup=kb_main(uid)); return
    if bot_settings.get("credit_system") and not bot_settings.get("referral_system") and uid not in ADMIN_IDS:
        uc = _uc(uid); uc["credits"] = max(0, uc.get("credits", 0) - int(bot_settings.get("credits_per_number", 1))); save_credits()
    uc = _uc(uid); uc["numbers_generated"] = uc.get("numbers_generated", 0) + 1; save_credits()
    did, info = random.choice(list(devs.items()))
    sess["devices"] = devs; sess["current_device"] = did; sess["mode"] = "online"
    stop_sms(uid)

    # ★ BASELINE WITH RECENT-CUTOFF (fixes race where OTP arrives during baseline fetch)
    baseline = set()
    try:
        pairs_sms = await fetch_sms(info.get("fb_url", ""), info["real_cid"], 50)
        now_sec = time.time()
        for k, m in pairs_sms:
            fp = _fp(k, m)
            ts = _extract_msg_time_sec(m)
            # If msg is VERY recent (< BASELINE_RECENT_SEC old), don't baseline it
            # so it appears in monitor even if it arrived during this fetch
            if ts is not None and (now_sec - ts) < BASELINE_RECENT_SEC:
                continue
            baseline.add(fp)
    except: pass

    start_sms(context.bot, uid, chat_id, did, unlimited=True, baseline=baseline,
              fb_url=info["fb_url"], phone=info.get("phone", "N/A"), status_msg=True)
    raw = info.get("raw") or {}
    net = raw.get("network") or raw.get("operator") or "—"
    andr = raw.get("android") or raw.get("androidVersion") or "—"
    bat = raw.get("battery") or "—"
    if isinstance(bat, (int, float)): bat = f"{int(bat)}%"
    gen_msg = await update.message.reply_text(
        f"🎉 <b>NUMBER GENERATED!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 <b>Device:</b> <code>{info['real_cid']}</code>\n"
        f"📞 <b>Phone:</b> <code>{info.get('phone','N/A')}</code>\n"
        f"🌐 <b>Panel:</b> {info['fb_tag']}\n"
        f"📡 ONLINE 🟢\n📶 {net}\n🤖 {andr}\n🔋 {bat}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔔 <b>OTP MONITOR: ACTIVE</b>"
        + (f"\n⏲ <b>Auto-stop:</b> {auto_stop_label()}" if auto_stop_sec() > 0 else ""),
        parse_mode="HTML", reply_markup=kb_device())
    # Track this message so it auto-deletes along with the OTP alerts when the
    # monitor is stopped (manually, by timeout, or by generating a new number).
    cur_st = sms_state.get(uid)
    if cur_st is not None:
        cur_st.setdefault("sent_message_ids", []).append(gen_msg.message_id)
    context.user_data["kb_state"] = "device"

# ═══════════════════════════ SCAN ═══════════════════════════
async def do_scan(update, context, page=0):
    uid = update.effective_user.id
    if not await _require_access(update, context): return
    sess = await _sess(uid)
    private = is_private(uid)
    if private:
        r = _ufb(uid); fbs = r["fbs"]
        if not fbs:
            await update.message.reply_text("⚠️ <b>PRIVATE — NO FBs</b>", parse_mode="HTML",
                                            reply_markup=kb_main(uid)); return
        pairs = [(u, f"USER{i+1}") for i, u in enumerate(fbs)]
    else:
        pairs = global_fb_list
        if not pairs:
            await update.message.reply_text("⚠️ <b>NO FIREBASES</b>", parse_mode="HTML",
                                            reply_markup=kb_main(uid)); return
    await update.message.reply_text("⏳ <b>Scanning devices...</b>", parse_mode="HTML")
    devs = await devs_all(pairs, online=True, max_per=100)
    sess["devices"] = devs; sess["dev_page"] = page
    if not devs:
        await update.message.reply_text("⚠️ <b>NO ONLINE DEVICES</b>", parse_mode="HTML",
                                        reply_markup=kb_main(uid)); return
    await update.message.reply_text(cap_dev_list(devs, page), parse_mode="HTML",
                                    reply_markup=kb_devlist(devs, page))
    context.user_data["kb_state"] = "device"

async def do_select_device(update, context, dev_id):
    uid = update.effective_user.id
    sess = await _sess(uid)
    info = sess.get("devices", {}).get(dev_id)
    if not info:
        await update.message.reply_text("❌ <b>Device not found</b>", parse_mode="HTML",
                                        reply_markup=kb_main(uid)); return
    sess["current_device"] = dev_id
    raw = info.get("raw") or {}
    bat = raw.get("battery") or "—"
    if isinstance(bat, (int, float)): bat = f"{int(bat)}%"
    await update.message.reply_text(
        f"📱 <b>DEVICE INFO</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <code>{info.get('real_cid', dev_id)}</code>\n"
        f"📞 <code>{info.get('phone','N/A')}</code>\n"
        f"🌐 <b>{info.get('fb_tag','?')}</b>\n"
        f"📡 ONLINE 🟢\n📶 {raw.get('network','—')}\n"
        f"🤖 {raw.get('android','—')}\n🔋 {bat}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML", reply_markup=kb_device())
    context.user_data["kb_state"] = "device"

# ═══════════════════════════ SPIN ═══════════════════════════
SPIN = ["🍒", "🍋", "⭐", "💎", "🎁", "🔥", "💰", "🎯"]
async def do_spin(update, context):
    uid = update.effective_user.id
    if not await _require_access(update, context): return
    uc = _uc(uid); now = time.time()
    if now - uc.get("last_spin", 0) < SPIN_CD:
        r = int(SPIN_CD - (now - uc.get("last_spin", 0)))
        h, m = r // 3600, (r % 3600) // 60
        await update.message.reply_text(f"⏳ <b>COOLDOWN</b>\n\nCome back in {h}h {m}m",
                                        parse_mode="HTML", reply_markup=kb_main(uid)); return
    msg = await update.message.reply_text("🎰 <b>SPINNING...</b>\n\n0%", parse_mode="HTML")
    try:
        for pct in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            await asyncio.sleep(0.18)
            row = " | ".join(random.choices(SPIN, k=3))
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            try: await msg.edit_text(f"🎰 <b>SPINNING...</b>\n\n<b>{row}</b>\n\n<code>{bar}</code> <b>{pct}%</b>",
                                      parse_mode="HTML")
            except: pass
        rew = random.randint(bot_settings.get("daily_spin_reward_min", 1),
                             bot_settings.get("daily_spin_reward_max", 5))
        nb = uc.get("credits", 0) + rew
        await msg.edit_text(
            f"🎉 <b>JACKPOT!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n💎 | 💎 | 💎\n\n"
            f"🎁 Won <b>{rew}</b> credits!\n💎 Total: <b>{nb}</b>", parse_mode="HTML")
        uc["credits"] = nb; uc["last_spin"] = now; save_credits()
    except: pass

# ═══════════════════════════ SMS MONITOR ═══════════════════════════
async def _del_msgs(bot, uid, chat_id, ids=None):
    st = sms_state.get(uid, {})
    ids = list(ids if ids is not None else st.get("sent_message_ids", []))
    if not ids: return
    for mid in ids:
        try: await bot.delete_message(chat_id=chat_id, message_id=mid)
        except: pass
    if ids is None: st["sent_message_ids"] = []

async def _del_status(bot, uid, chat_id):
    st = sms_state.get(uid, {})
    mid = st.get("monitor_message_id")
    if not mid: return
    try: await bot.delete_message(chat_id=chat_id, message_id=mid)
    except: pass
    st.pop("monitor_message_id", None)

async def _stop_notice(bot, uid, chat_id, reason):
    txt = None
    if reason == "duration": txt = f"⏱️ <b>MONITOR AUTO-STOPPED</b>\n<i>Time limit reached ({auto_stop_label() if auto_stop_sec()>0 else 'duration'})</i>\n\n🔔 Tap NEW NUMBER to generate again"
    elif reason == "idle": txt = "⏰ <b>MONITOR STOPPED</b>\n\n10 min idle"
    elif reason == "revoked": txt = "⚠️ <b>ACCESS REVOKED</b>"
    if txt:
        try: await bot.send_message(chat_id=chat_id, text=txt, parse_mode="HTML", reply_markup=kb_main(uid))
        except: pass

def stop_sms(uid, reason=None):
    task = sms_tasks.pop(uid, None)
    st = sms_state.get(uid)
    if st:
        bot = st.get("bot"); chat_id = st.get("chat_id")
        if bot and chat_id:
            if st.get("sent_message_ids"): asyncio.create_task(_del_msgs(bot, uid, chat_id, list(st.get("sent_message_ids", []))))
            asyncio.create_task(_del_status(bot, uid, chat_id))
            if reason in ("idle", "revoked", "duration"): asyncio.create_task(_stop_notice(bot, uid, chat_id, reason))
    if task and not task.done(): task.cancel()
    sms_state.pop(uid, None)

def touch_sms(uid):
    st = sms_state.get(uid)
    if st: st["last_activity"] = time.monotonic()

async def _sms_loop(bot, uid, chat_id, did, unl, base, fb_url, st, phone):
    reason = None
    try:
        parts = did.split("|", 1)
        cid = parts[1] if len(parts) == 2 else did
        started = time.monotonic(); seen = set(base)
        u = ep(fb_url, f"messages/{cid}", 'orderBy="$key"&limitToLast=50')
        poll_n = 0
        while True:
            cur = sms_state.get(uid)
            if cur is not st: break
            if not unl and time.monotonic() - started >= SMS_DURATION: reason = "duration"; break
            _as = auto_stop_sec()
            if _as > 0 and time.monotonic() - started >= _as: reason = "duration"; break
            if unl and uid not in ADMIN_IDS and time.monotonic() - cur.get("last_activity", started) >= SMS_IDLE:
                reason = "idle"; break
            if uid not in ADMIN_IDS and bot_settings.get("referral_system") and not has_access(uid):
                reason = "revoked"; break
            poll_n += 1
            data, s, _ = await fb_get(u, t=6, retries=0)
            if poll_n % 60 == 0:
                logger.info(f"SMS uid={uid} poll={poll_n} status={s} seen={len(seen)}")
            if s == "OK" and isinstance(data, (dict, list)) and data:
                pairs = _newkeys(data, 50)
                new = [(k, m, _fp(k, m)) for k, m in pairs if _fp(k, m) not in seen]
                new.sort(key=lambda x: str(x[0]))
                for k, m, fp in new:
                    sender = _sender(m); body = _body(m)
                    if not body:
                        seen.add(fp); continue
                    when = _mtime(m, k); otp = _otp(body)
                    if otp:
                        alert = (
                            f"🔑🔑🔑 <b>OTP RECEIVED!</b> 🔑🔑🔑\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"<b>OTP:</b> <code>{otp}</code>\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📱 <code>{cid}</code>\n"
                            f"📞 <code>{phone}</code>\n"
                            f"👤 <b>{html_escape(sender)}</b>\n"
                            f"⏱️ {html_escape(when)}\n"
                            f"💬 <i>{html_escape(body[:180])}</i>"
                        )
                    else:
                        alert = (
                            f"📩 <b>LIVE SMS</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📱 <code>{cid}</code>\n"
                            f"📞 <code>{phone}</code>\n"
                            f"👤 <b>{html_escape(sender)}</b>\n"
                            f"⏱️ {html_escape(when)}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"💬 {html_escape(body)}\n"
                            f"<i>No OTP detected</i>"
                        )
                    try:
                        sent = await bot.send_message(chat_id=chat_id, text=alert, parse_mode="HTML")
                        seen.add(fp)
                        if sms_state.get(uid) is cur:
                            cur.setdefault("sent_message_ids", []).append(sent.message_id)
                    except: pass
                if len(seen) > 500: seen = set(_fp(k, m) for k, m in pairs)
            await asyncio.sleep(SMS_INTERVAL)
    except asyncio.CancelledError: raise
    except Exception as e: logger.warning(f"sms loop uid={uid} died: {e}")
    finally:
        cur = sms_state.get(uid)
        if cur is st:
            await _del_msgs(bot, uid, chat_id, list(cur.get("sent_message_ids", [])))
            await _del_status(bot, uid, chat_id)
            if reason: await _stop_notice(bot, uid, chat_id, reason)
            sms_state.pop(uid, None); sms_tasks.pop(uid, None)
            logger.info(f"SMS monitor stopped uid={uid} reason={reason or 'external'}")

def start_sms(bot, uid, chat_id, did, *, unlimited=False, baseline=None, fb_url="", phone="N/A", status_msg=False):
    stop_sms(uid)
    now = time.monotonic()
    st = {"device_id": did, "chat_id": chat_id, "sent_message_ids": [], "bot": bot,
          "unlimited": unlimited, "fb_url": fb_url, "last_activity": now, "phone": phone,
          "monitor_message_id": None}
    sms_state[uid] = st
    sms_tasks[uid] = asyncio.create_task(_sms_loop(bot, uid, chat_id, did, unlimited, baseline or set(), fb_url, st, phone))
    logger.info(f"SMS monitor started uid={uid} device={did} baseline={len(baseline or set())}")
    if status_msg:
        async def _s():
            try:
                m = await bot.send_message(chat_id=chat_id,
                    text="🟢 <b>SMS Monitor Active</b>\n<i>Waiting for new SMS...</i>", parse_mode="HTML")
                if sms_state.get(uid) is st: st["monitor_message_id"] = m.message_id
            except: pass
        asyncio.create_task(_s())

# ═══════════════════════════ SMS VIEW ═══════════════════════════
async def show_sms(update, context):
    uid = update.effective_user.id
    sess = user_sessions.get(uid) or {}
    dev = sess.get("current_device", "")
    if not dev:
        await update.message.reply_text("❌ <b>No device</b>", parse_mode="HTML", reply_markup=kb_main(uid)); return
    info = sess.get("devices", {}).get(dev, {})
    if not info or not info.get("fb_url"):
        parts = dev.split("|", 1)
        tag = parts[0] if len(parts) == 2 else ""
        cid = parts[1] if len(parts) == 2 else dev
        for u, t in global_fb_list:
            if t == tag: info = {"fb_url": u, "fb_tag": t, "real_cid": cid, "phone": "N/A", "online": True, "raw": {}}; break
    if not info:
        await update.message.reply_text("❌ <b>Device expired</b>", parse_mode="HTML", reply_markup=kb_main(uid)); return
    pairs = await fetch_sms(info["fb_url"], info["real_cid"], 5)
    # ★ filter out empty body + duplicates
    filtered = []
    seen_sig = set()
    for ts, m in pairs:
        body = _body(m)
        if not body: continue
        sig = (body, _sender(m))
        if sig in seen_sig: continue
        seen_sig.add(sig)
        filtered.append((ts, m))
    pairs = filtered
    if not pairs:
        await update.message.reply_text(
            f"📭 <b>NO VALID SMS YET</b>\n📱 <code>{info['real_cid']}</code>\n📞 <code>{info.get('phone','N/A')}</code>\n\n"
            "<i>Tap REFRESH SMS when OTP arrives</i>",
            parse_mode="HTML", reply_markup=kb_sms()); return
    blocks = ["📩 <b>LAST 5 SMS</b>", "━━━━━━━━━━━━━━━━━━━━━━━━",
              f"📱 <code>{info['real_cid']}</code>",
              f"📞 <code>{info.get('phone','N/A')}</code>", "━━━━━━━━━━━━━━━━━━━━━━━━"]
    circled = ("①","②","③","④","⑤")
    for i, (ts, m) in enumerate(pairs, 1):
        sender = _sender(m); body = _body(m); when = _mtime(m, ts); otp = _otp(body)
        badge = circled[i-1] if i <= 5 else f"[{i}]"
        otl = f"🔑 <b>OTP:</b> <code>{otp}</code>" if otp else "<i>No OTP</i>"
        blocks.append(f"\n<b>{badge} {html_escape(sender)}</b> · {html_escape(when)}")
        blocks.append(f"💬 {html_escape(body[:200])}")
        blocks.append(otl)
        blocks.append("────────────────────────")
    await update.message.reply_text("\n".join(blocks), parse_mode="HTML", reply_markup=kb_sms())

# ═══════════════════════════ ADMIN CMD ═══════════════════════════
async def admin_cmd(update, context):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Admin only.", reply_markup=kb_main(uid)); return
    context.user_data["kb_state"] = "admin"
    await update.message.reply_text(
        f"🛠 <b>{BOT_BRAND} ADMIN PANEL</b>\n\n👑 Owner: {OWNER_NAME}\n\n👇 <i>Use menu below</i>",
        parse_mode="HTML", reply_markup=kb_admin())

# ═══════════════════════════ CAPTCHA ═══════════════════════════
async def captcha_in(update, context):
    if "force_join_captcha" not in context.user_data: return
    raw = (update.message.text or "").strip()
    try: a = int(re.sub(r"\D", "", raw))
    except:
        await update.message.reply_text("❌ Send numbers only.", reply_markup=kb_verify()); return
    if a != context.user_data.get("force_join_captcha"):
        x, y = random.randint(2, 20), random.randint(2, 20)
        op = random.choice(("+", "-", "×"))
        ans = x + y if op == "+" else x - y if op == "-" else x * y
        context.user_data["force_join_captcha"] = ans
        await update.message.reply_text(f"❌ Wrong!\n\n🧮 Try: <code>{x} {op} {y} = ?</code>", parse_mode="HTML")
        return
    context.user_data.pop("force_join_captcha", None)
    context.user_data["force_join_verified"] = True
    uid = update.effective_user.id
    verified_users.add(uid)
    rec = _urec(uid); rec["is_verified"] = True; rec["captcha_verified"] = True; _sv_ref()
    await fin_ref(context.bot, uid, update.effective_user.username or str(uid))
    await update.message.reply_text("✅ <b>VERIFIED!</b>", parse_mode="HTML")
    await send_effect(context.bot, update.effective_chat.id,
                       cap_main(update.effective_user.first_name or "User", uid),
                       reply_markup=kb_main(uid))

# ═══════════════════════════ CUSTOM FB INPUT ═══════════════════════════
async def custom_fb_in(update, context):
    uid = update.effective_user.id
    txt = (update.message.text or "").strip()
    context.user_data.pop("awaiting_custom_fb", None)
    url = norm_fb(txt)
    if not url:
        await update.message.reply_text("❌ <b>Invalid URL</b>", parse_mode="HTML", reply_markup=_custom_kb(uid)); return
    r = _ufb(uid)
    if url in r["fbs"]:
        await update.message.reply_text("⚠️ Already added", reply_markup=_custom_kb(uid)); return
    if len(r["fbs"]) >= MAX_USER_FB:
        await update.message.reply_text(f"❌ Max {MAX_USER_FB}", reply_markup=_custom_kb(uid)); return
    msg = await update.message.reply_text("⏳ Validating...")
    try: cl, _ = await asyncio.wait_for(_try_clients(url, retries=1), timeout=30); ok = bool(cl)
    except asyncio.TimeoutError:
        try: await msg.delete()
        except: pass
        await update.message.reply_text("❌ Timeout (30s)", reply_markup=_custom_kb(uid)); return
    except: ok = False
    if not ok:
        try: await msg.delete()
        except: pass
        await update.message.reply_text("❌ Dead/empty", reply_markup=_custom_kb(uid)); return
    r["fbs"].append(url); _sv_ufb()
    ident = f"@{update.effective_user.username}" if update.effective_user.username else f"User {uid}"
    for aid in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=aid,
                text=(f"🔔 <b>NEW CUSTOM FB</b>\n👤 {html_escape(ident)}\n"
                      f"🆔 <code>{uid}</code>\n🔗 <code>{html_escape(url)}</code>\n"
                      f"📊 {len(r['fbs'])}/{MAX_USER_FB}"), parse_mode="HTML")
        except: pass
    try: await msg.delete()
    except: pass
    await update.message.reply_text(f"✅ <b>Added!</b>\n\n📊 {len(r['fbs'])}/{MAX_USER_FB}",
                                    parse_mode="HTML", reply_markup=_custom_kb(uid))

# ═══════════════════════════ ADMIN TEXT INPUT ═══════════════════════════
async def admin_text_in(update, context):
    uid = update.effective_user.id
    act = context.user_data.get("admin_action")
    if uid not in ADMIN_IDS or not act: return
    txt = (update.message.text or "").strip()
    if act == "set_logger":
        context.user_data.pop("admin_action", None)
        ch = txt
        if ch.startswith("https://t.me/"): ch = "@" + ch.rstrip("/").rsplit("/", 1)[-1].split("?", 1)[0]
        try: await context.bot.send_message(chat_id=ch, text="🔗 Test OK")
        except Exception as e: await update.message.reply_text(f"❌ {e}", reply_markup=kb_logger()); return
        LOGGER_SETTINGS["channel"] = ch; _sv_log()
        await update.message.reply_text(f"✅ Set: {ch}", reply_markup=kb_logger()); return
    if act == "gift_hours_user":
        try: h = float(txt)
        except: await update.message.reply_text("❌ Number only", reply_markup=kb_admin()); return
        if h <= 0 or h > GIFT_MAX_H: await update.message.reply_text("❌ Invalid", reply_markup=kb_admin()); return
        t = context.user_data.pop("gift_target", None); context.user_data.pop("admin_action", None)
        if not t: return
        _urec(t); grant(t, int(h * 3600))
        rem = fmt_time(t)
        try: await context.bot.send_message(chat_id=t, text=f"🎁 <b>ACCESS GIFTED</b>\n⏳ {h:g}h\n📊 {rem}", parse_mode="HTML")
        except: pass
        await update.message.reply_text(f"✅ Gifted {h:g}h to <code>{t}</code>\n📊 {rem}",
                                        parse_mode="HTML", reply_markup=kb_user_detail(t)); return
    if act == "gift_single":
        parts = txt.split()
        if len(parts) != 2: await update.message.reply_text("❌ Format: `<uid> <hours>`", parse_mode="Markdown", reply_markup=kb_gift()); return
        try: t, h = int(parts[0]), float(parts[1])
        except: await update.message.reply_text("❌ Invalid", reply_markup=kb_gift()); return
        if h <= 0 or h > GIFT_MAX_H: await update.message.reply_text("❌ Invalid", reply_markup=kb_gift()); return
        _urec(t); grant(t, int(h * 3600))
        context.user_data.pop("admin_action", None)
        rem = fmt_time(t)
        try: await context.bot.send_message(chat_id=t, text=f"🎁 <b>+{h:g}h</b>\n📊 {rem}", parse_mode="HTML")
        except: pass
        await update.message.reply_text(f"✅ Gifted to <code>{t}</code>\n📊 {rem}", parse_mode="HTML",
                                        reply_markup=kb_admin()); return
    if act == "gift_all":
        try: h = float(txt)
        except: await update.message.reply_text("❌ Number only", reply_markup=kb_gift()); return
        if h <= 0 or h > GIFT_MAX_H: await update.message.reply_text("❌ Invalid", reply_markup=kb_gift()); return
        context.user_data.pop("admin_action", None); s = f = 0
        for u in list(known_users):
            _urec(u); grant(u, int(h * 3600))
            try: await context.bot.send_message(chat_id=u, text=f"🎁 <b>+{h:g}h</b>", parse_mode="HTML"); s += 1
            except: f += 1
        await update.message.reply_text(f"✅ Sent: {s} | ❌ Failed: {f}", reply_markup=kb_admin()); return
    if act == "gift_credits_user":
        try: a = int(txt)
        except: await update.message.reply_text("❌ Number only", reply_markup=kb_admin()); return
        t = context.user_data.pop("gift_target", None); context.user_data.pop("admin_action", None)
        if not t: return
        uc = _uc(t); uc["credits"] = uc.get("credits", 0) + a; save_credits()
        try: await context.bot.send_message(chat_id=t, text=f"💎 <b>+{a} credits</b>\n📊 {uc['credits']}", parse_mode="HTML")
        except: pass
        await update.message.reply_text(f"✅ Added {a} credits to <code>{t}</code>\n💎 {uc['credits']}",
                                        parse_mode="HTML", reply_markup=kb_user_detail(t)); return
    if act == "set_ref_time":
        context.user_data.pop("admin_action", None)
        sec = parse_duration(txt)
        if not sec or sec < 30 or sec > 365 * 24 * 3600:
            await update.message.reply_text(
                "❌ <b>Invalid format</b>\n\nExamples: <code>30s  2h  1d  3mo</code>\nMin: 30s | Max: 365d",
                parse_mode="HTML", reply_markup=kb_admin()); return
        bot_settings["referral_seconds"] = sec; save_settings()
        await update.message.reply_text(
            f"✅ <b>Referral time set:</b> <code>{ref_label()}</code> ({sec}s)",
            parse_mode="HTML", reply_markup=kb_admin()); return

    if act == "set_auto_stop":
        context.user_data.pop("admin_action", None)
        if txt.strip() in ("0", "off", "OFF"):
            bot_settings["auto_stop_seconds"] = 0; save_settings()
            await update.message.reply_text(
                "✅ <b>Auto Stop Monitor:</b> <code>OFF</code>\n<i>Idle timeout (10m) will still apply</i>",
                parse_mode="HTML", reply_markup=kb_admin()); return
        sec = parse_duration(txt)
        if not sec or sec < 30 or sec > 365 * 24 * 3600:
            await update.message.reply_text(
                "❌ <b>Invalid format</b>\n\nExamples: <code>1m  5m  2h  1d  1mo</code>\n"
                "Send <code>0</code> to turn OFF.\nMin: 30s | Max: 365d",
                parse_mode="HTML", reply_markup=kb_admin()); return
        bot_settings["auto_stop_seconds"] = sec; save_settings()
        await update.message.reply_text(
            f"✅ <b>Auto Stop Monitor set:</b> <code>{auto_stop_label()}</code> ({sec}s)\n"
            f"<i>Monitors auto-stop after this time, number+OTP auto-delete.</i>",
            parse_mode="HTML", reply_markup=kb_admin()); return

    if act == "set_credits":
        context.user_data.pop("admin_action", None)
        try: n = int(txt)
        except:
            await update.message.reply_text("❌ <b>Number only</b> e.g. <code>10</code>",
                                             parse_mode="HTML", reply_markup=kb_admin()); return
        if n < 1 or n > 10000:
            await update.message.reply_text("❌ Range: 1–10000", reply_markup=kb_admin()); return
        bot_settings["credits_per_number"] = n; save_settings()
        await update.message.reply_text(
            f"✅ <b>Credits/number set:</b> <code>{n}</code>",
            parse_mode="HTML", reply_markup=kb_admin()); return

    if act == "add_fb":
        url = norm_fb(txt)
        if not url: await update.message.reply_text("❌ Invalid", reply_markup=kb_admin()); return
        if any(u == url for u, _ in global_fb_list):
            await update.message.reply_text("⚠️ Already", reply_markup=kb_admin()); context.user_data.pop("admin_action", None); return
        if len(global_fb_list) >= FB_MAX:
            await update.message.reply_text("❌ Max", reply_markup=kb_admin()); context.user_data.pop("admin_action", None); return
        msg = await update.message.reply_text("⏳ Validating...")
        try: cl, _ = await asyncio.wait_for(_try_clients(url, retries=1), timeout=30); ok = bool(cl)
        except asyncio.TimeoutError:
            try: await msg.delete()
            except: pass
            context.user_data.pop("admin_action", None)
            await update.message.reply_text("❌ Timeout (30s)", reply_markup=kb_admin()); return
        except: ok = False
        if not ok:
            try: await msg.delete()
            except: pass
            await update.message.reply_text("❌ Dead", reply_markup=kb_admin()); return
        tag = f"FB{len(global_fb_list)+1}"; global_fb_list.append((url, tag))
        await _sv_async(GLOBAL_FB_FILE, [{"url": u, "tag": t} for u, t in global_fb_list])
        context.user_data.pop("admin_action", None)
        try: await msg.delete()
        except: pass
        # Respond immediately — bot UI stays responsive while the device-count
        # refresh for this one FB runs in the background.
        await update.message.reply_text(
            f"✅ <b>Added as {tag}</b>\n📊 Total FBs: {len(global_fb_list)}\n"
            f"⏳ <i>Counting devices in background...</i>",
            parse_mode="HTML", reply_markup=kb_admin())

        async def _bg_count(bot, chat_id, url=url, tag=tag):
            try:
                await refresh_cache(only=[url])
                per = dev_cache.get("per_fb", {}).get(tag) or {}
                on, off = int(per.get("online", 0)), int(per.get("offline", 0))
                await bot.send_message(chat_id=chat_id,
                    text=f"📊 <b>{tag} READY</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                         f"🟢 Online: <b>{on}</b>\n🔴 Offline: <b>{off}</b>\n📱 Total: <b>{on+off}</b>",
                    parse_mode="HTML")
            except Exception as e: logger.warning(f"bg_count {tag}: {e}")
        asyncio.create_task(_bg_count(context.bot, update.effective_chat.id))
        return
    if act == "add_ch":
        ch = txt
        if ch.startswith("https://t.me/"): ch = "@" + ch.rstrip("/").rsplit("/", 1)[-1].split("?", 1)[0]
        if not re.fullmatch(r"@[A-Za-z0-9_]{5,32}", ch):
            await update.message.reply_text("❌ Invalid @username", reply_markup=kb_admin()); return
        try: c = await context.bot.get_chat(ch); title = c.title or ch
        except: await update.message.reply_text("❌ Not found", reply_markup=kb_admin()); return
        REQUIRED_CHANNELS.append({"id": ch, "label": title, "url": f"https://t.me/{ch.lstrip('@')}"})
        _sv_ch(); context.user_data.pop("admin_action", None)
        await update.message.reply_text(f"✅ Added: {title}", reply_markup=kb_admin()); return
    if act == "broadcast":
        context.user_data.pop("admin_action", None); s = f = 0
        for u in list(known_users):
            try: await context.bot.send_message(chat_id=u, text=txt); s += 1
            except: f += 1
        await update.message.reply_text(f"📢 Sent: {s} | Failed: {f}", reply_markup=kb_admin()); return

# ═══════════════════════════ DOC HANDLER ═══════════════════════════
async def doc_handler(update, context):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS: return
    doc = update.message.document
    if not doc: return
    fn = (doc.file_name or "").lower()
    act = context.user_data.get("admin_action")
    if act == "bulk_firebase" and fn.endswith(".txt"):
        await _bulk_txt(update, context, doc)
    elif act == "restore_db" and fn.endswith(".db"):
        await _restore_db(update, context, doc)
    else:
        if fn.endswith(".txt"): await update.message.reply_text("⚠️ ਪਹਿਲਾਂ BULK ADD ਦਬਾਓ", reply_markup=kb_admin())
        elif fn.endswith(".db"): await update.message.reply_text("⚠️ ਪਹਿਲਾਂ RESTORE .db ਦਬਾਓ", reply_markup=kb_admin())
        else: await update.message.reply_text("❌ ਸਿਰਫ਼ .txt ਜਾਂ .db", reply_markup=kb_main(uid))

# ═══════════════════════════ BULK ADD (progressive + timeout) ═══════════════════════════
async def _bulk_txt(update, context, doc):
    context.user_data.pop("admin_action", None)

    # ── STEP 1: get_file ──
    msg = await update.message.reply_text("📥 <b>Step 1/5:</b> Fetching file info...", parse_mode="HTML")
    try:
        f = await asyncio.wait_for(context.bot.get_file(doc.file_id), timeout=30)
    except asyncio.TimeoutError:
        try: await msg.edit_text("❌ <b>Step 1 timeout</b>: get_file (30s)\n\nRetry karo.")
        except: pass
        return
    except Exception as e:
        try: await msg.edit_text(f"❌ <b>Step 1 error:</b>\n<code>{html_escape(str(e)[:200])}</code>", parse_mode="HTML")
        except: pass
        return

    # ── STEP 2: download ──
    try: await msg.edit_text("📥 <b>Step 2/5:</b> Downloading file bytes...", parse_mode="HTML")
    except: pass
    try:
        raw = await asyncio.wait_for(f.download_as_bytearray(), timeout=120)
    except asyncio.TimeoutError:
        try: await msg.edit_text("❌ <b>Step 2 timeout</b>: download (120s)\n\nFile bahut bada ya network slow. Chhota file try karo.")
        except: pass
        return
    except Exception as e:
        try: await msg.edit_text(f"❌ <b>Step 2 error:</b>\n<code>{html_escape(str(e)[:200])}</code>", parse_mode="HTML")
        except: pass
        return

    # ── STEP 3: parse ──
    try:
        text = raw.decode("utf-8", errors="ignore")
    except:
        text = raw.decode("latin-1", errors="ignore")
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    try: await msg.edit_text(f"🔍 <b>Step 3/5:</b> Parsing {len(lines)} lines...", parse_mode="HTML")
    except: pass

    existing = {u for u, _ in global_fb_list}
    valid = []; dup = inv = 0
    for ln in lines:
        u = norm_fb(ln)
        if not u: inv += 1; continue
        if u in existing: dup += 1; continue
        existing.add(u); valid.append(u)

    avail = FB_MAX - len(global_fb_list)
    sk = 0
    if len(valid) > avail:
        sk = len(valid) - avail
        valid = valid[:avail]

    if not valid:
        try: await msg.delete()
        except: pass
        await update.message.reply_text(
            f"⚠️ <b>NOTHING TO ADD</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 Total lines: <b>{len(lines)}</b>\n"
            f"🔁 Duplicates: <b>{dup}</b>\n"
            f"❌ Invalid: <b>{inv}</b>",
            parse_mode="HTML", reply_markup=kb_admin()); return

    # ── STEP 4: append + save ──
    for u in valid:
        global_fb_list.append((u, f"FB{len(global_fb_list)+1}"))
    try: await msg.edit_text(f"💾 <b>Step 4/5:</b> Saving {len(valid)} new FBs to disk...", parse_mode="HTML")
    except: pass

    save_ok = True
    try:
        await asyncio.wait_for(
            _sv_async(GLOBAL_FB_FILE, [{"url": u, "tag": t} for u, t in global_fb_list]),
            timeout=20
        )
    except (asyncio.TimeoutError, Exception):
        save_ok = False

    # ── STEP 5: respond now, count devices in background ──
    try: await msg.edit_text("🔄 <b>Step 5/5:</b> Counting devices in background...", parse_mode="HTML")
    except: pass
    await asyncio.sleep(0.4)

    try: await msg.delete()
    except: pass

    txt = (
        f"✅ <b>BULK ADD COMPLETE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Added:</b> {len(valid)}\n"
        f"🔁 Duplicates: {dup}\n"
        f"❌ Invalid: {inv}\n"
    )
    if sk: txt += f"⚠️ Skipped (limit): {sk}\n"
    txt += f"📊 <b>Total FBs now:</b> {len(global_fb_list)}\n"
    txt += f"💾 Saved to disk: {'✅' if save_ok else '⚠️ failed (memory only)'}\n"
    txt += f"⏳ <b>Device count:</b> <i>loading below...</i>"

    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=kb_admin())

    valid_tags = [t for u, t in global_fb_list if u in set(valid)]

    async def _bg_bulk_count(bot, chat_id, urls=list(valid), tags=valid_tags):
        try:
            await refresh_cache(only=urls)
            per = dev_cache.get("per_fb", {})
            on = sum(int((per.get(t) or {}).get("online", 0)) for t in tags)
            off = sum(int((per.get(t) or {}).get("offline", 0)) for t in tags)
            await bot.send_message(chat_id=chat_id,
                text=f"📊 <b>NEW FBs — DEVICE COUNT READY</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                     f"🟢 Online: <b>{on}</b>\n🔴 Offline: <b>{off}</b>\n📱 Total: <b>{on+off}</b>",
                parse_mode="HTML")
        except Exception as e: logger.warning(f"bg_bulk_count: {e}")
    asyncio.create_task(_bg_bulk_count(context.bot, update.effective_chat.id))

async def _restore_db(update, context, doc):
    global global_fb_list, maintenance_mode, captcha_enabled, REFERRAL_DB
    global REQUIRED_CHANNELS, USER_CUSTOM_FBS, known_users, LOGGER_SETTINGS, bot_settings, user_credits
    msg = await update.message.reply_text("⏳ Downloading...")
    try:
        f = await asyncio.wait_for(context.bot.get_file(doc.file_id), timeout=30)
        raw = await asyncio.wait_for(f.download_as_bytearray(), timeout=120)
    except asyncio.TimeoutError:
        context.user_data.pop("admin_action", None); await msg.edit_text("❌ Timeout"); return
    except Exception as e:
        context.user_data.pop("admin_action", None); await msg.edit_text(f"❌ {e}"); return
    context.user_data.pop("admin_action", None)
    fd, tmp = tempfile.mkstemp(suffix=".db"); os.close(fd)
    with open(tmp, "wb") as fh: fh.write(raw)
    restored = []; failed = []
    try:
        c = sqlite3.connect(tmp)
        try: rows = c.execute("SELECT filename, content FROM backup").fetchall()
        finally: c.close()
        for fn, content in rows:
            try:
                data = json.loads(content)
                with open(fn, "w", encoding="utf-8") as fh: json.dump(data, fh, ensure_ascii=False, indent=2)
                if fn == "referrals.json" and isinstance(data, dict): REFERRAL_DB.clear(); REFERRAL_DB.update(data)
                elif fn == "global_firebases.json" and isinstance(data, list):
                    global_fb_list.clear()
                    for i, x in enumerate(data):
                        if isinstance(x, dict) and x.get("url"): global_fb_list.append((str(x["url"]), str(x.get("tag", f"FB{i+1}"))))
                elif fn == "bot_users.json" and isinstance(data, list):
                    known_users.clear(); known_users.update({int(v) for v in data if str(v).isdigit()})
                elif fn == "user_custom_fbs.json" and isinstance(data, dict): USER_CUSTOM_FBS.clear(); USER_CUSTOM_FBS.update(data)
                elif fn == "force_join_channels.json" and isinstance(data, list):
                    REQUIRED_CHANNELS.clear(); REQUIRED_CHANNELS.extend([ch for ch in data if isinstance(ch, dict) and ch.get("id")])
                elif fn == "maintenance_mode.json": maintenance_mode = bool(data.get("enabled", False)) if isinstance(data, dict) else bool(data)
                elif fn == "captcha_state.json": captcha_enabled = bool(data.get("enabled", True)) if isinstance(data, dict) else True
                elif fn == "logger_settings.json" and isinstance(data, dict): LOGGER_SETTINGS.clear(); LOGGER_SETTINGS.update(data)
                elif fn == "bot_settings.json" and isinstance(data, dict):
                    bot_settings.clear(); bot_settings.update({**DEFAULT_SETTINGS, **data})
                    bot_settings["button_colors"] = {**DEFAULT_SETTINGS["button_colors"], **bot_settings.get("button_colors", {})}
                    bot_settings.setdefault("enabled_reactions", list(ALLOWED_REACTIONS))
                    bot_settings.setdefault("enabled_effects", list(ALLOWED_EFFECTS.keys()))
                elif fn == "user_credits.json" and isinstance(data, dict): user_credits.clear(); user_credits.update(data)
                restored.append(fn)
            except Exception as exc: failed.append(f"{fn}: {exc}")
    except Exception as exc: await msg.edit_text(f"❌ Restore failed: {exc}"); return
    finally:
        try: os.unlink(tmp)
        except: pass
    txt = f"✅ <b>RESTORE COMPLETE</b>\n✅ Restored: {len(restored)}\n❌ Failed: {len(failed)}"
    if failed: txt += "\n\n" + "\n".join(f"• {f}" for f in failed[:5])
    try: await msg.delete()
    except: pass
    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=kb_admin())

def _cycle_color(key):
    opts = ["primary", "success", "danger", "secondary"]
    cur = bot_settings["button_colors"].get(key, "primary")
    try: i = opts.index(cur)
    except: i = 0
    bot_settings["button_colors"][key] = opts[(i + 1) % len(opts)]; save_settings()

# ═══════════════════════════ TEXT ROUTER ═══════════════════════════
async def text_router(update, context):
    global maintenance_mode, captcha_enabled
    text = (update.message.text or "").strip()
    uid = update.effective_user.id

    if text == BT_CANCEL:
        kb_state = context.user_data.get("kb_state", "main")
        context.user_data.clear()
        context.user_data["kb_state"] = kb_state
        target = kb_admin() if (uid in ADMIN_IDS and kb_state == "admin") else kb_main(uid)
        await update.message.reply_text("❌ Cancelled", reply_markup=target); return

    if _is_btn(text):
        context.user_data.pop("admin_action", None)
        context.user_data.pop("gift_target", None)
        context.user_data.pop("awaiting_custom_fb", None)

    if "force_join_captcha" in context.user_data:
        if text == BT_VERIFY:
            if await force_ok(context.bot, uid):
                rec = _urec(uid)
                if captcha_enabled and uid not in ADMIN_IDS and not rec.get("captcha_verified"):
                    x, y = random.randint(2, 20), random.randint(2, 20)
                    op = random.choice(("+", "-", "×"))
                    ans = x + y if op == "+" else x - y if op == "-" else x * y
                    context.user_data["force_join_captcha"] = ans
                    await update.message.reply_text(f"🔐 <b>VERIFY</b>\n\n<code>{x} {op} {y} = ?</code>",
                                                    parse_mode="HTML"); return
                verified_users.add(uid); rec["is_verified"] = True; rec["captcha_verified"] = True; _sv_ref()
                await fin_ref(context.bot, uid, update.effective_user.username or str(uid))
                await send_effect(context.bot, update.effective_chat.id,
                                   cap_main(update.effective_user.first_name or "User", uid),
                                   reply_markup=kb_main(uid))
            else:
                un = await unjoined(context.bot, uid)
                links = "\n".join(f"{i+1}. <a href=\"{c['url']}\">{c['label']}</a>" for i, c in enumerate(un))
                await update.message.reply_text(f"❌ <b>Join first!</b>\n\n{links}", parse_mode="HTML",
                                                disable_web_page_preview=True, reply_markup=kb_verify())
            return
        if not _is_btn(text):
            await captcha_in(update, context); return
        else: return

    if text == BT_VERIFY:
        if await force_ok(context.bot, uid):
            rec = _urec(uid)
            if captcha_enabled and uid not in ADMIN_IDS and not rec.get("captcha_verified"):
                x, y = random.randint(2, 20), random.randint(2, 20)
                op = random.choice(("+", "-", "×"))
                ans = x + y if op == "+" else x - y if op == "-" else x * y
                context.user_data["force_join_captcha"] = ans
                await update.message.reply_text(f"🔐 <b>VERIFY</b>\n\n<code>{x} {op} {y} = ?</code>",
                                                parse_mode="HTML"); return
            verified_users.add(uid); rec["is_verified"] = True; rec["captcha_verified"] = True; _sv_ref()
            await fin_ref(context.bot, uid, update.effective_user.username or str(uid))
            await send_effect(context.bot, update.effective_chat.id,
                               cap_main(update.effective_user.first_name or "User", uid),
                               reply_markup=kb_main(uid))
        else:
            un = await unjoined(context.bot, uid)
            links = "\n".join(f"{i+1}. <a href=\"{c['url']}\">{c['label']}</a>" for i, c in enumerate(un))
            await update.message.reply_text(f"❌ <b>Join first!</b>\n\n{links}", parse_mode="HTML",
                                            disable_web_page_preview=True, reply_markup=kb_verify())
        return

    if context.user_data.get("awaiting_custom_fb"):
        await custom_fb_in(update, context); return
    if context.user_data.get("admin_action"):
        await admin_text_in(update, context); return

    if text.startswith("🟢 ") and "|" in text:
        dev = _dev_id_from_button(text)
        if dev: await do_select_device(update, context, dev)
        return

    # ═══ MAIN MENU ═══
    if text == BT_GEN or text == BT_NEW: await do_generate(update, context); return
    if text == BT_SCAN: await do_scan(update, context, 0); return
    if text == BT_REFER:
        if await _require_access(update, context):
            await update.message.reply_text(cap_refer(uid), parse_mode="HTML", reply_markup=kb_main(uid))
        return
    if text == BT_SPIN: await do_spin(update, context); return
    if text == BT_LB:
        await update.message.reply_text(cap_lb(), parse_mode="HTML", reply_markup=kb_main(uid)); return
    if text == BT_PROF:
        if await _require_access(update, context):
            await update.message.reply_text(cap_profile(uid, update.effective_user.first_name or "User"),
                                            parse_mode="HTML", reply_markup=kb_main(uid))
        return
    if text == BT_BACK:
        stop_sms(uid); context.user_data.clear(); context.user_data["kb_state"] = "main"
        await send_effect(context.bot, update.effective_chat.id,
                           cap_main(update.effective_user.first_name or "User", uid),
                           reply_markup=kb_main(uid)); return
    if text == BT_SMS or text == BT_RFSMS:
        if await _require_access(update, context): await show_sms(update, context)
        return
    if text == BT_STOPMON:
        stop_sms(uid)
        await update.message.reply_text("⛔ <b>Monitor stopped</b>", parse_mode="HTML",
                                        reply_markup=kb_main(uid)); return

    if text == BT_PREV or text == BT_NEXT:
        delta = -1 if text == BT_PREV else 1
        lt = context.user_data.get("list_type") or ("dev" if context.user_data.get("kb_state") == "device" else "")
        if lt == "rx":
            tp = max(1, (len(ALLOWED_REACTIONS) + RX_PAGE - 1) // RX_PAGE)
            pg = max(0, min(context.user_data.get("rx_page", 0) + delta, tp - 1))
            context.user_data["rx_page"] = pg
            await update.message.reply_text(cap_rx(pg), parse_mode="HTML", reply_markup=kb_rx(pg)); return
        if lt == "fb":
            tp = max(1, (len(global_fb_list) + FB_PAGE - 1) // FB_PAGE)
            pg = max(0, min(context.user_data.get("fb_page", 0) + delta, tp - 1))
            context.user_data["fb_page"] = pg
            sent = await update.message.reply_text(cap_fb_list(pg), parse_mode="HTML", reply_markup=kb_fb(pg))
            await _start_admin_live(context.bot, uid, sent.chat_id, sent.message_id)
            return
        if lt == "user":
            users = sorted(known_users)
            tp = max(1, (len(users) + UL_PAGE - 1) // UL_PAGE)
            pg = max(0, min(context.user_data.get("user_page", 0) + delta, tp - 1))
            context.user_data["user_page"] = pg
            await update.message.reply_text(cap_users(pg), parse_mode="HTML", reply_markup=kb_users(pg)); return
        if lt == "dev":
            sess = user_sessions.get(uid, {})
            devs = sess.get("devices", {})
            tp = max(1, (len(devs) + DEV_PAGE - 1) // DEV_PAGE)
            pg = max(0, min(sess.get("dev_page", 0) + delta, tp - 1))
            sess["dev_page"] = pg
            await update.message.reply_text(cap_dev_list(devs, pg), parse_mode="HTML",
                                            reply_markup=kb_devlist(devs, pg)); return
        return

    # ═══ CUSTOM PANEL ═══
    if text == BT_CUSTOM:
        if await _require_access(update, context):
            context.user_data["kb_state"] = "custom"
            await update.message.reply_text(cap_custom(uid), parse_mode="HTML",
                                            reply_markup=_custom_kb(uid))
        return
    if context.user_data.get("kb_state") == "custom":
        r = _ufb(uid)
        if _has(text, "TURN PRIVATE"):
            r["mode"] = "off" if r["mode"] == "on" else "on"; _sv_ufb()
            await update.message.reply_text(cap_custom(uid), parse_mode="HTML",
                                            reply_markup=_custom_kb(uid)); return
        if text.startswith(f"➕ {bold('ADD FIREBASE')}"):
            context.user_data["awaiting_custom_fb"] = True
            await update.message.reply_text("➕ <b>Send Firebase URL:</b>", parse_mode="HTML",
                                            reply_markup=kb_cancel()); return
        if text.startswith(f"🗑 {bold('DELETE')} #"):
            try:
                idx = int(text.split("#")[-1]) - 1
                if 0 <= idx < len(r["fbs"]): r["fbs"].pop(idx); _sv_ufb()
            except: pass
            await update.message.reply_text(cap_custom(uid), parse_mode="HTML",
                                            reply_markup=_custom_kb(uid)); return

    # ═══ ADMIN ═══
    if uid in ADMIN_IDS:
        if text not in (BT_MNGFB, BT_REFRESH, BT_PREV, BT_NEXT) and not text.startswith(("🔄 FB", "🗑 FB")):
            _stop_admin_live(uid)

        if text == BT_ADMIN:
            context.user_data["kb_state"] = "admin"
            await update.message.reply_text(f"🛠 <b>ADMIN PANEL</b>\n\n👑 {OWNER_NAME}",
                                            parse_mode="HTML", reply_markup=kb_admin()); return

        if text == BT_RX:
            context.user_data["rx_page"] = 0; context.user_data["list_type"] = "rx"
            await update.message.reply_text(cap_rx(0), parse_mode="HTML", reply_markup=kb_rx(0)); return
        if text == BT_FX:
            context.user_data["list_type"] = "fx"
            await update.message.reply_text(cap_fx(), parse_mode="HTML", reply_markup=kb_fx()); return

        if text.startswith("✅") or text.startswith("❌"):
            payload = text[1:].strip()
            if payload in ALLOWED_REACTIONS:
                en = bot_settings.get("enabled_reactions", [])
                if payload in en: en.remove(payload)
                else: en.append(payload)
                bot_settings["enabled_reactions"] = en; save_settings()
                pg = context.user_data.get("rx_page", 0)
                await update.message.reply_text(cap_rx(pg), parse_mode="HTML", reply_markup=kb_rx(pg)); return
            for k, info in ALLOWED_EFFECTS.items():
                if info["emoji"] in payload:
                    en = bot_settings.get("enabled_effects", [])
                    if k in en: en.remove(k)
                    else: en.append(k)
                    bot_settings["enabled_effects"] = en; save_settings()
                    await update.message.reply_text(cap_fx(), parse_mode="HTML", reply_markup=kb_fx()); return
            if text == BT_SELALL:
                if context.user_data.get("list_type") == "rx":
                    bot_settings["enabled_reactions"] = list(ALLOWED_REACTIONS)
                else: bot_settings["enabled_effects"] = list(ALLOWED_EFFECTS.keys())
                save_settings()
                if context.user_data.get("list_type") == "rx":
                    pg = context.user_data.get("rx_page", 0)
                    await update.message.reply_text(cap_rx(pg), parse_mode="HTML", reply_markup=kb_rx(pg))
                else:
                    await update.message.reply_text(cap_fx(), parse_mode="HTML", reply_markup=kb_fx())
                return
            if text == BT_DESELALL:
                if context.user_data.get("list_type") == "rx":
                    bot_settings["enabled_reactions"] = []
                else: bot_settings["enabled_effects"] = []
                save_settings()
                if context.user_data.get("list_type") == "rx":
                    pg = context.user_data.get("rx_page", 0)
                    await update.message.reply_text(cap_rx(pg), parse_mode="HTML", reply_markup=kb_rx(pg))
                else:
                    await update.message.reply_text(cap_fx(), parse_mode="HTML", reply_markup=kb_fx())
                return

        if text == BT_BACKBTN:
            context.user_data.pop("rx_page", None); context.user_data.pop("list_type", None)
            await update.message.reply_text(f"🛠 <b>ADMIN PANEL</b>", parse_mode="HTML", reply_markup=kb_admin()); return

        if text.startswith(("🟢", "🔴")) and _has(text, "REFERRAL"):
            bot_settings["referral_system"] = not bot_settings["referral_system"]
            if bot_settings["referral_system"]: bot_settings["credit_system"] = False
            save_settings()
            await update.message.reply_text(cap_settings(), parse_mode="HTML", reply_markup=kb_admin()); return
        if text.startswith(("🟢", "🔴")) and _has(text, "CREDIT"):
            bot_settings["credit_system"] = not bot_settings["credit_system"]
            if bot_settings["credit_system"]: bot_settings["referral_system"] = False
            save_settings()
            await update.message.reply_text(cap_settings(), parse_mode="HTML", reply_markup=kb_admin()); return
        if text.startswith(("🟢", "🔴")) and _has(text, "BOT"):
            maintenance_mode = not maintenance_mode; _sv_maint()
            notice = cap_maint(); s = f = 0
            for u in list(known_users):
                try: await context.bot.send_message(chat_id=u, text=notice, parse_mode="HTML"); s += 1
                except: f += 1
            await update.message.reply_text(f"{notice}\n\n📨 {s} | ❌ {f}", parse_mode="HTML",
                                            reply_markup=kb_admin()); return
        if text.startswith("🔐") or text.startswith("🔓"):
            captcha_enabled = not captcha_enabled; _sv_cap()
            await update.message.reply_text(f"🔐 Captcha: {'ON' if captcha_enabled else 'OFF'}",
                                            reply_markup=kb_admin()); return

        if text == BT_REFHRS:
            cur = ref_label()
            context.user_data["admin_action"] = "set_ref_time"
            await update.message.reply_text(
                f"⏰ <b>REFERRAL TIME</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚙️ <b>Current:</b> <code>{cur}</code>\n\n"
                f"<b>Quick examples:</b>\n"
                f"<code>30s</code> = 30 sec  |  <code>30m</code> = 30 min\n"
                f"<code>2h</code> = 2 hrs   |  <code>1d</code> = 1 day\n"
                f"<code>1mo</code> = 1 month\n\n"
                f"⌨️ Type your value:",
                parse_mode="HTML", reply_markup=kb_cancel()); return

        if text == BT_CREDCFG:
            cur = int(bot_settings.get("credits_per_number", 1))
            context.user_data["admin_action"] = "set_credits"
            await update.message.reply_text(
                f"💎 <b>CREDITS PER NUMBER</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚙️ <b>Current:</b> <code>{cur}</code> credits = 1 number\n\n"
                f"⌨️ Type new value (1–10000):",
                parse_mode="HTML", reply_markup=kb_cancel()); return

        if text == BT_ADDFB:
            if len(global_fb_list) >= FB_MAX:
                await update.message.reply_text("❌ Max reached", reply_markup=kb_admin()); return
            context.user_data["admin_action"] = "add_fb"
            await update.message.reply_text("➕ Send Firebase URL:", reply_markup=kb_cancel()); return
        if text == BT_BULK:
            context.user_data["admin_action"] = "bulk_firebase"
            await update.message.reply_text("📤 Send `.txt` file", parse_mode="Markdown",
                                            reply_markup=kb_cancel()); return
        if text == BT_AUTOSTOP:
            cur = auto_stop_label()
            context.user_data["admin_action"] = "set_auto_stop"
            await update.message.reply_text(
                f"⏲ <b>AUTO STOP MONITOR</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚙️ <b>Current:</b> <code>{cur}</code>\n\n"
                f"Monitor is auto-stopped (number+OTP auto-deleted) after this much time.\n\n"
                f"<b>Examples:</b>\n"
                f"<code>1m</code> = 1 min | <code>5m</code> = 5 min\n"
                f"<code>2h</code> = 2 hrs | <code>1d</code> = 1 day | <code>1mo</code> = 1 month\n"
                f"<code>0</code> = OFF (idle-timeout only)\n\n"
                f"⌨️ Type new value:",
                parse_mode="HTML", reply_markup=kb_cancel()); return

        if text == BT_FBTIERS:
            await update.message.reply_text(cap_fb_tiers(), parse_mode="HTML", reply_markup=kb_fb_tiers()); return
        if text.startswith(BT_TIER_LOW):
            await update.message.reply_text(cap_fb_tier_list("low"), parse_mode="HTML", reply_markup=kb_fb_tiers()); return
        if text.startswith(BT_TIER_MID):
            await update.message.reply_text(cap_fb_tier_list("mid"), parse_mode="HTML", reply_markup=kb_fb_tiers()); return
        if text.startswith(BT_TIER_HIGH):
            await update.message.reply_text(cap_fb_tier_list("high"), parse_mode="HTML", reply_markup=kb_fb_tiers()); return

        if text == BT_MNGFB:
            context.user_data["fb_page"] = 0; context.user_data["list_type"] = "fb"
            sent = await update.message.reply_text(cap_fb_list(0), parse_mode="HTML", reply_markup=kb_fb(0))
            await _start_admin_live(context.bot, uid, sent.chat_id, sent.message_id)
            return
        if text == BT_REFRESH:
            await update.message.reply_text("⏳ <b>Refreshing...</b>", parse_mode="HTML")
            await refresh_cache()
            pg = context.user_data.get("fb_page", 0)
            sent = await update.message.reply_text(cap_fb_list(pg), parse_mode="HTML", reply_markup=kb_fb(pg))
            await _start_admin_live(context.bot, uid, sent.chat_id, sent.message_id)
            return
        if text.startswith("🔄 FB") and len(text) <= 12:
            try:
                idx = int(text.replace("🔄 FB", "")) - 1
                if 0 <= idx < len(global_fb_list):
                    url, tag = global_fb_list[idx]
                    c = dev_cache.get("per_fb", {}).get(tag, {})
                    on, off = int(c.get("online", 0)), int(c.get("offline", 0))
                    await update.message.reply_text(
                        f"📋 <b>{tag}</b>\n🔗 <code>{html_escape(url)}</code>\n"
                        f"🟢 {on} | 🔴 {off} | 📊 {on+off}\n"
                        f"🕒 {dev_cache.get('updated_at','')}", parse_mode="HTML", reply_markup=kb_fb())
            except: pass
            return
        if text.startswith("🗑 FB") and len(text) <= 12:
            try:
                idx = int(text.replace("🗑 FB", "")) - 1
                if 0 <= idx < len(global_fb_list):
                    global_fb_list.pop(idx); _retag()
                    await _sv_async(GLOBAL_FB_FILE, [{"url": u, "tag": t} for u, t in global_fb_list])
            except: pass
            pg = context.user_data.get("fb_page", 0)
            sent = await update.message.reply_text(cap_fb_list(pg), parse_mode="HTML", reply_markup=kb_fb(pg))
            await _start_admin_live(context.bot, uid, sent.chat_id, sent.message_id)
            return

        if text == BT_TOTAL:
            # Show the cached snapshot instantly (never makes the admin panel feel stuck),
            # then refresh in the background and push an updated snapshot after.
            await update.message.reply_text(cap_total(), parse_mode="HTML", reply_markup=kb_admin())
            async def _bg_total(bot, chat_id):
                try:
                    await refresh_cache()
                    await bot.send_message(chat_id=chat_id, text="🔄 <b>REFRESHED</b>\n\n" + cap_total(),
                                           parse_mode="HTML")
                except Exception as e: logger.warning(f"bg_total: {e}")
            asyncio.create_task(_bg_total(context.bot, update.effective_chat.id))
            return

        if text == BT_USERS:
            context.user_data["user_page"] = 0; context.user_data["list_type"] = "user"
            await update.message.reply_text(cap_users(0), parse_mode="HTML", reply_markup=kb_users(0)); return
        if (text.startswith("👤") or text.startswith("🚫")) and "·" in text and " FBs" not in text:
            u = _uid_from_user_btn(text)
            if u:
                context.user_data["selected_user"] = u
                await update.message.reply_text(cap_user_detail(u), parse_mode="HTML",
                                                reply_markup=kb_user_detail(u))
            return
        if text == BT_UBACK:
            pg = context.user_data.get("user_page", 0); context.user_data["list_type"] = "user"
            await update.message.reply_text(cap_users(pg), parse_mode="HTML", reply_markup=kb_users(pg)); return
        if text == BT_UDGIFT:
            t = context.user_data.get("selected_user")
            if t:
                context.user_data["admin_action"] = "gift_hours_user"; context.user_data["gift_target"] = t
                await update.message.reply_text(f"🎁 Send hours for <code>{t}</code>:", parse_mode="HTML",
                                                reply_markup=kb_cancel())
            return
        if text == BT_UADDREF:
            t = context.user_data.get("selected_user")
            if t:
                try:
                    rec = _urec(t); now = time.time()
                    cur = rec.get("access_expires_at", 0.0)
                    rec["access_expires_at"] = (now if cur < now else cur) + ref_sec()
                    rec["referral_count"] = rec.get("referral_count", 0) + 1
                    if not isinstance(rec.get("referrals"), list): rec["referrals"] = []
                    rec["referrals"].append(0); _sv_ref()
                except: pass
                await update.message.reply_text(cap_user_detail(t), parse_mode="HTML",
                                                reply_markup=kb_user_detail(t))
            return
        if text == BT_UGIFTCRED:
            t = context.user_data.get("selected_user")
            if t:
                context.user_data["admin_action"] = "gift_credits_user"; context.user_data["gift_target"] = t
                await update.message.reply_text(f"💎 Send credits for <code>{t}</code>:", parse_mode="HTML",
                                                reply_markup=kb_cancel())
            return
        if text == BT_UBAN or text == BT_UUNBAN:
            t = context.user_data.get("selected_user")
            if t:
                uc = _uc(t); uc["banned"] = not uc.get("banned", False); save_credits()
                await update.message.reply_text(cap_user_detail(t), parse_mode="HTML",
                                                reply_markup=kb_user_detail(t))
            return

        if text == BT_UFBS:
            rows = []
            for uid_str, r in USER_CUSTOM_FBS.items():
                cnt = len(r.get("fbs", []))
                if cnt > 0:
                    try: rows.append([kbtn(f"👤 User {int(uid_str)} · {cnt} FBs", "primary")])
                    except: pass
            if not rows: rows.append([kbtn("— Empty —", "primary")])
            rows.append([kbtn(BT_ADMINBACK, "danger")])
            await update.message.reply_text("🎯 <b>USER CUSTOM FBs</b>", parse_mode="HTML",
                                            reply_markup=ReplyKeyboardMarkup(rows, resize_keyboard=True)); return
        if text.startswith("👤") and " FBs" in text:
            u = _uid_from_cfb_btn(text)
            if u:
                r = USER_CUSTOM_FBS.get(str(u), {"fbs": []})
                lines = [f"👤 <b>User {u}</b>", f"Mode: <b>{r.get('mode','off')}</b>",
                         f"Total: <b>{len(r.get('fbs', []))}</b>", ""]
                for i, url in enumerate(r.get("fbs", []), 1):
                    lines.append(f"{i}. <code>{html_escape(url[:60])}</code>")
                rows = [[kbtn(f"🗑 {bold('DELETE')} #{i+1}", "danger")] for i in range(len(r.get("fbs", [])))]
                rows.append([kbtn(BT_ADMINBACK, "danger")])
                context.user_data["admin_view_uid"] = u
                await update.message.reply_text("<blockquote>" + "\n".join(lines) + "</blockquote>",
                                                parse_mode="HTML",
                                                reply_markup=ReplyKeyboardMarkup(rows, resize_keyboard=True))
            return
        if text.startswith(f"🗑 {bold('DELETE')} #") and "admin_view_uid" in context.user_data:
            try:
                idx = int(text.split("#")[-1]) - 1
                u = context.user_data["admin_view_uid"]
                r = USER_CUSTOM_FBS.get(str(u), {"fbs": []})
                if 0 <= idx < len(r.get("fbs", [])): r["fbs"].pop(idx); _sv_ufb()
                lines = [f"👤 <b>User {u}</b>", f"Mode: <b>{r.get('mode','off')}</b>",
                         f"Total: <b>{len(r.get('fbs', []))}</b>", ""]
                for i, url in enumerate(r.get("fbs", []), 1):
                    lines.append(f"{i}. <code>{html_escape(url[:60])}</code>")
                rows = [[kbtn(f"🗑 {bold('DELETE')} #{i+1}", "danger")] for i in range(len(r.get("fbs", [])))]
                rows.append([kbtn(BT_ADMINBACK, "danger")])
                await update.message.reply_text("<blockquote>" + "\n".join(lines) + "</blockquote>",
                                                parse_mode="HTML",
                                                reply_markup=ReplyKeyboardMarkup(rows, resize_keyboard=True))
            except: pass
            return

        if text == BT_LOGGER:
            await update.message.reply_text(cap_logger(), parse_mode="HTML", reply_markup=kb_logger()); return
        if text == BT_LOGSET:
            context.user_data["admin_action"] = "set_logger"
            await update.message.reply_text("🔗 Send @username or -100...", reply_markup=kb_cancel()); return
        if text == BT_LOGBK:
            await update.message.reply_text("⏳ Creating...")
            ok, info = await _send_backup(context.bot, manual=True)
            await update.message.reply_text(f"{'✅' if ok else '❌'} <code>{info}</code>",
                                            parse_mode="HTML", reply_markup=kb_logger()); return
        if text == BT_LOGRES:
            context.user_data["admin_action"] = "restore_db"
            await update.message.reply_text("📥 Send `.db` file", parse_mode="Markdown",
                                            reply_markup=kb_cancel()); return
        if text == "🔴 AUTO OFF" or text == "🟢 AUTO ON":
            LOGGER_SETTINGS["auto_backup"] = not LOGGER_SETTINGS.get("auto_backup", True); _sv_log()
            await update.message.reply_text(cap_logger(), parse_mode="HTML", reply_markup=kb_logger()); return
        if text in (BT_LOG6, BT_LOG12, BT_LOG24):
            try:
                h = int(text.split()[1].replace("h", ""))
                if h in AUTO_BK: LOGGER_SETTINGS["interval_hours"] = h; _sv_log()
            except: pass
            await update.message.reply_text(cap_logger(), parse_mode="HTML", reply_markup=kb_logger()); return

        if text == BT_STATS:
            await update.message.reply_text(cap_stats(), parse_mode="HTML", reply_markup=kb_admin()); return

        if text == BT_GIFT:
            await update.message.reply_text("🎁 <b>GIFT ACCESS</b>", parse_mode="HTML", reply_markup=kb_gift()); return
        if text == BT_GSINGLE:
            context.user_data["admin_action"] = "gift_single"
            await update.message.reply_text("👤 Format: `<uid> <hours>`", parse_mode="Markdown",
                                            reply_markup=kb_gift()); return
        if text == BT_GALL:
            context.user_data["admin_action"] = "gift_all"
            await update.message.reply_text(f"👥 Send hours. Total: {len(known_users)}",
                                            parse_mode="Markdown", reply_markup=kb_gift()); return

        if text == BT_BCAST:
            context.user_data["admin_action"] = "broadcast"
            await update.message.reply_text("📢 Send message", reply_markup=kb_cancel()); return

        if text == BT_COLORS:
            await update.message.reply_text(cap_colors(), parse_mode="HTML", reply_markup=kb_colors()); return
        if text.startswith("🔵") and _has(text, "PRIMARY"):
            _cycle_color("primary")
            await update.message.reply_text(cap_colors(), parse_mode="HTML", reply_markup=kb_colors()); return
        if text.startswith("🟢") and _has(text, "SUCCESS"):
            _cycle_color("success")
            await update.message.reply_text(cap_colors(), parse_mode="HTML", reply_markup=kb_colors()); return
        if text.startswith("🔴") and _has(text, "DANGER"):
            _cycle_color("danger")
            await update.message.reply_text(cap_colors(), parse_mode="HTML", reply_markup=kb_colors()); return

        if text == BT_ADDCH:
            context.user_data["admin_action"] = "add_ch"
            await update.message.reply_text("➕ Send @username", reply_markup=kb_cancel()); return
        if text == BT_MNGCH:
            lines = ["📋 <b>Force-Join Channels</b>\n"]
            for i, c in enumerate(REQUIRED_CHANNELS, 1):
                lines.append(f"{i}. <code>{c.get('label', c.get('id'))}</code>")
            await update.message.reply_text("\n".join(lines), parse_mode="HTML", reply_markup=kb_admin()); return

        if text == BT_ADMINBACK:
            context.user_data["kb_state"] = "admin"
            context.user_data.pop("admin_awaiting", None)
            await update.message.reply_text("🛠 <b>ADMIN PANEL</b>", parse_mode="HTML", reply_markup=kb_admin()); return

# ═══════════════════════════ LOOPS ═══════════════════════════
async def _maint_loop(bot):
    lc = 0
    while True:
        try:
            await asyncio.sleep(ACCESS_CHK); lc += 1
            if lc % 2 == 0: gc.collect()
            for u, t in list(sms_tasks.items()):
                if t.done(): sms_tasks.pop(u, None)
            for u, t in list(admin_live_tasks.items()):
                if t.done(): admin_live_tasks.pop(u, None)
            for u in list(sms_state.keys()):
                if u in ADMIN_IDS: continue
                if bot_settings.get("referral_system") and not has_access(u): stop_sms(u, reason="revoked")
            if REQUIRED_CHANNELS:
                for u in list(known_users):
                    try:
                        ok = await force_ok(bot, u)
                        prev = user_access_state.get(u); user_access_state[u] = ok
                        if prev is True and not ok:
                            verified_users.discard(u)
                            if u not in ADMIN_IDS: stop_sms(u)
                            ref_id = await check_left(u)
                            if ref_id:
                                try: await bot.send_message(chat_id=ref_id,
                                    text=f"⚠️ <b>ACCESS REDUCED</b>\n\n−{ref_h()}h removed", parse_mode="HTML")
                                except: pass
                    except: pass
        except asyncio.CancelledError: raise
        except: pass

async def _hb_loop(bot):
    while True:
        try:
            await asyncio.sleep(HB_INTERVAL)
            logger.info(f"✅ alive | users={len(known_users)} monitors={len(sms_tasks)} sessions={len(user_sessions)}")
        except asyncio.CancelledError: raise
        except: pass

async def _mem_loop(bot):
    while True:
        try:
            await asyncio.sleep(MEM_CHECK)
            rss = total = 0
            try:
                with open("/proc/self/status", "r") as f:
                    for ln in f:
                        if ln.startswith("VmRSS:"): rss = int(ln.split()[1]) / 1024; break
            except: pass
            try:
                with open("/proc/meminfo", "r") as f:
                    for ln in f:
                        if ln.startswith("MemTotal:"): total = int(ln.split()[1]) / 1024; break
            except: pass
            if total > 0 and rss > 0 and (rss/total)*100 > 80:
                gc.collect()
                for aid in ADMIN_IDS:
                    try: await bot.send_message(chat_id=aid,
                        text=f"⚠️ <b>MEM WARNING</b>\n{rss:.0f}/{total:.0f}MB ({(rss/total)*100:.0f}%)",
                        parse_mode="HTML")
                    except: pass
        except asyncio.CancelledError: raise
        except: pass

async def _watchdog(bot):
    strikes = 0
    while True:
        try:
            await asyncio.sleep(WATCHDOG)
            await asyncio.wait_for(bot.get_me(), timeout=20)
            strikes = 0
        except asyncio.CancelledError: raise
        except: strikes += 1; logger.warning(f"watchdog {strikes}")

async def _post_stop(app):
    for t in list(sms_tasks.values()):
        if not t.done(): t.cancel()
    if sms_tasks: await asyncio.gather(*sms_tasks.values(), return_exceptions=True)
    sms_tasks.clear(); sms_state.clear()
    for t in list(admin_live_tasks.values()):
        if not t.done(): t.cancel()
    if admin_live_tasks: await asyncio.gather(*admin_live_tasks.values(), return_exceptions=True)
    admin_live_tasks.clear()

# ═══════════════════════════ ERROR HANDLER ═══════════════════════════
async def _err_handler(update, context):
    e = context.error
    if isinstance(e, (NetworkError, TimedOut)):
        logger.debug(f"transient net: {type(e).__name__}: {e}")
        return
    if isinstance(e, RetryAfter):
        logger.warning(f"flood wait: retry after {getattr(e, 'retry_after', '?')}s")
        return
    if isinstance(e, Conflict):
        logger.warning(f"conflict (another instance running?): {e}")
        return
    if isinstance(e, BadRequest):
        m = str(e).lower()
        if any(x in m for x in ("not modified", "message is not modified")):
            return
        if any(x in m for x in ("message to edit not found", "message can't be edited",
                                "message_id_invalid", "message to delete not found")):
            return
        logger.warning(f"bad request: {e}")
        return
    u = update
    logger.error(f"err: {type(u).__name__ if u is not None else 'unknown'}: {e}",
                 exc_info=(type(e), e, e.__traceback__) if e else None)

# ═══════════════════════════ MAIN ═══════════════════════════
def main():
    print("=" * 60)
    print(f"  ⚡ {BOT_BRAND} OTP BOT — FINAL v14 ⚡")
    print(f"  FBs: {len(global_fb_list)} | Channels: {len(REQUIRED_CHANNELS)}")
    print(f"  Referral: {'ON' if bot_settings['referral_system'] else 'OFF'} ({ref_h()}h)")
    print(f"  Credit: {'ON' if bot_settings['credit_system'] else 'OFF'}")
    print(f"  Reaction: {REACTION_OK}  |  Auto-refresh: {ADMIN_LIVE}s")
    print("=" * 60)
    app = (Application.builder().token(BOT_TOKEN)
           .read_timeout(30).write_timeout(30).connect_timeout(20).pool_timeout(20).build())
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(MessageHandler(filters.Document.ALL & filters.ChatType.PRIVATE, doc_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, text_router))
    app.add_error_handler(_err_handler)

    async def _post_init(application):
        global BOT_USERNAME
        get_session()
        try:
            me = await application.bot.get_me()
            BOT_USERNAME = me.username or "Bot"
            logger.info(f"Bot: @{BOT_USERNAME}")
        except: pass
        try: await application.bot.set_my_commands([BotCommand("start", "🚀 Start")])
        except: pass
        application.bot_data["maint"] = asyncio.create_task(_maint_loop(application.bot))
        application.bot_data["refresh"] = asyncio.create_task(_refresh_loop())
        application.bot_data["backup"] = asyncio.create_task(_auto_bk_loop(application.bot))
        application.bot_data["watchdog"] = asyncio.create_task(_watchdog(application.bot))
        application.bot_data["mem"] = asyncio.create_task(_mem_loop(application.bot))
        application.bot_data["hb"] = asyncio.create_task(_hb_loop(application.bot))

    async def _post_stop_clean(application):
        for k in ("maint", "refresh", "backup", "watchdog", "mem", "hb"):
            t = application.bot_data.pop(k, None)
            if t and not t.done(): t.cancel(); await asyncio.gather(t, return_exceptions=True)
        await _post_stop(application)
        await close_session()

    app.post_init = _post_init
    app.post_shutdown = _post_stop_clean
    print("Starting polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    import sys
    retry = 0
    while True:
        try:
            retry += 1
            if retry > 1:
                logger.info(f"♻️ Restart attempt #{retry} — waiting 10s...")
                time.sleep(10)
            main()
        except KeyboardInterrupt:
            logger.info("🛑 Stopped by user.")
            sys.exit(0)
        except Exception as _e:
            logger.error(f"💥 Bot crashed: {type(_e).__name__}: {_e} — auto-restarting in 10s...")