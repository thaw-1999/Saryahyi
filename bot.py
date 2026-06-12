import os
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

try:
    from fragment_api_lib.client import FragmentAPIClient
    fragment = FragmentAPIClient()
except ImportError:
    logging.warning("fragment_api_lib ကို ရှာမတွေ့ပါ။")
    fragment = None

# ==================== .env ဖိုင်ကို ဖတ်ရန် နေရာ ====================
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv library မရှိပါ။ Environment variables များကို တိုက်ရိုက်ဖတ်ပါမည်။")
# =================================================================

# ==== Env မှ တန်ဖိုးများ ဆွဲယူခြင်း ====
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "YOUR_SUPPORT_ACC")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789")) 

TON_SEED = os.getenv("TON_SEED", "word1 word2 ... word24")

STEL_DT = os.getenv("STEL_DT", "")
STEL_SSID = os.getenv("STEL_SSID", "")
STEL_TOKEN = os.getenv("STEL_TOKEN", "")
STEL_TON_TOKEN = os.getenv("STEL_TON_TOKEN", "")

FRAGMENT_COOKIES = f"stel_dt={STEL_DT}; stel_ssid={STEL_SSID}; stel_token={STEL_TOKEN}; stel_ton_token={STEL_TON_TOKEN}"
# ============================================================

# ငွေလွှဲလက်ခံမည့် အချက်အလက်များ
PAYMENT_INFO = """
💵 **ငွေပေးချေရမည့် နည်းလမ်းများ**

ℹ️ **KBZPay**
နံပါတ် - `09444123849`
အမည် - Thaw Zin

ℹ️ **WavePay**
နံပါတ် - `09444123849`
အမည် - Thaw Zin

⚠️ ငွေလွှဲပြီးပါက Screenshot (ဘောင်ချာ) ကို ဒီ Bot ထဲသို့ ပို့ပေးရပါမည်။
"""

# ပက်ကေ့စ်များနှင့် မြန်မာငွေဈေးနှုန်းများ
STAR_PACKAGES = {
    "50":   {"stars": 50,   "price": 3500},
    "75":   {"stars": 75,   "price": 5200},
    "100":  {"stars": 100,  "price": 6900},
    "125":  {"stars": 125,  "price": 8600},
    "150":  {"stars": 150,  "price": 10300},
    "175":  {"stars": 175,  "price": 12000},
    "200":  {"stars": 200,  "price": 13800},
    "250":  {"stars": 250,  "price": 17000},
    "500":  {"stars": 500,  "price": 35000},
    "1000": {"stars": 1000, "price": 70000},
}

PREMIUM_PACKAGES = {
    "3":  {"months": 3,  "price": 56000},
    "6":  {"months": 6,  "price": 75000},
    "12": {"months": 12, "price": 135000},
}
# ============================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class OrderState(StatesGroup):
    waiting_for_username = State()
    waiting_for_screenshot = State()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Telegram Stars ဝယ်ယူရန်", callback_data="buy_stars")],
        [InlineKeyboardButton(text="👑 Telegram Premium ဝယ်ယူရန်", callback_data="buy_premium")],
        [InlineKeyboardButton(text="💬 ကူညီဆောင်ရွက်ရေး (Support)", url=f"https://t.me/{SUPPORT_USERNAME}")],
    ])

def stars_menu():
    buttons = []
    for key, pkg in STAR_PACKAGES.items():
        buttons.append([InlineKeyboardButton(
            text=f"⭐ {pkg['stars']} Stars — {pkg['price']:,} MMK",
            callback_data=f"stars_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ ပင်မမီနူးသို့", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def premium_menu():
    buttons = []
    for key, pkg in PREMIUM_PACKAGES.items():
        buttons.append([InlineKeyboardButton(
            text=f"👑 {pkg['months']} လစာ — {pkg['price']:,} MMK",
            callback_data=f"premium_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ ပင်မမီနူးသို့", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def recipient_menu(key, prefix="stars"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 မိမိကိုယ်တိုင်အတွက်", callback_data=f"self_{prefix}_{key}")],
        [InlineKeyboardButton(text="👥 သူငယ်ချင်းအတွက်", callback_data=f"friend_{prefix}_{key}")],
        [InlineKeyboardButton(
            text="◀️ နောက်သို့",
            callback_data="buy_stars" if prefix == "stars" else "buy_premium"
        )],
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 ** Digital Services Bot မှ ကြိုဆိုပါတယ်!**\n\n"
        "⭐ Telegram Stars နှင့် Premium များကို မြန်မာကျပ်ငွေဖြင့် လွယ်ကူလျင်မြန်စွာ ဝယ်ယူနိုင်ပါပြီ။\n\n"
        "လုပ်ဆောင်လိုသည့် ဝန်ဆောင်မှုကို ရွေးချယ်ပါ -",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 **TZK Digital Services Bot မှ ကြိုဆိုပါတယ်!**\n\n"
        "⭐ Telegram Stars နှင့် Premium များကို မြန်မာကျပ်ငွေဖြင့် လွယ်ကူလျင်မြန်စွာ ဝယ်ယူနိုင်ပါပြီ။\n\n"
        "လုပ်ဆောင်လိုသည့် ဝန်ဆောင်မှုကို ရွေးချယ်ပါ -",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ===== STARS SECTION =====
@dp.callback_query(F.data == "buy_stars")
async def buy_stars(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ **ဝယ်ယူလိုသည့် Stars ပက်ကေ့စ်ကို ရွေးချယ်ပါ -**",
        reply_markup=stars_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("stars_"))
async def stars_selected(callback: CallbackQuery):
    key = callback.data.split("_")[1]
    pkg = STAR_PACKAGES[key]
    await callback.message.edit_text(
        f"⭐ **{pkg['stars']} Stars — {pkg['price']:,} MMK**\n\n"
        f"မည်သူ့ထံသို့ ပို့ဆောင်ရမလဲ ရွေးချယ်ပါ -",
        reply_markup=recipient_menu(key, "stars"),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("self_stars_"))
async def stars_for_self(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    username = callback.from_user.username
    if not username:
        await callback.answer("သင့်အကောင့်မှာ Username (ဥပမာ - @name) မရှိသေးပါသဖြင့် 'သူငယ်ချင်းအတွက်' မှတစ်ဆင့် ကိုယ်တိုင်ရိုက်ထည့်ပေးပါ!", show_alert=True)
        return
    await prompt_payment(callback.message, key, "stars", username, state)

@dp.callback_query(F.data.startswith("friend_stars_"))
async def stars_for_friend(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    await state.update_data(key=key, order_type="stars")
    await state.set_state(OrderState.waiting_for_username)
    await callback.message.edit_text(
        "👥 **လက်ခံမည့်သူ၏ Telegram Username ကို ရိုက်ထည့်ပါ -**\n\n"
        "ဥပမာ: `tzk` သို့မဟုတ် `@tzk`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ နောက်သို့", callback_data=f"stars_{key}")]
        ]),
        parse_mode="Markdown"
    )

# ===== PREMIUM SECTION =====
@dp.callback_query(F.data == "buy_premium")
async def buy_premium(callback: CallbackQuery):
    await callback.message.edit_text(
        "👑 **ဝယ်ယူလိုသည့် Premium သက်တမ်းကို ရွေးချယ်ပါ -**",
        reply_markup=premium_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("premium_"))
async def premium_selected(callback: CallbackQuery):
    key = callback.data.split("_")[1]
    pkg = PREMIUM_PACKAGES[key]
    await callback.message.edit_text(
        f"👑 **Telegram Premium {pkg['months']} လစာ — {pkg['price']:,} MMK**\n\n"
        f"မည်သူ့ထံသို့ ပို့ဆောင်ရမလဲ ရွေးချယ်ပါ -",
        reply_markup=recipient_menu(key, "premium"),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("self_premium_"))
async def premium_for_self(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    username = callback.from_user.username
    if not username:
        await callback.answer("သင့်အကောင့်မှာ Username မရှိပါသဖြင့် 'သူငယ်ချင်းအတွက်' မှတစ်ဆင့် ရိုက်ထည့်ပေးပါ!", show_alert=True)
        return
    await prompt_payment(callback.message, key, "premium", username, state)

@dp.callback_query(F.data.startswith("friend_premium_"))
async def premium_for_friend(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    await state.update_data(key=key, order_type="premium")
    await state.set_state(OrderState.waiting_for_username)
    await callback.message.edit_text(
        "👥 **လက်ခံမည့်သူ၏ Telegram Username ကို ရိုက်ထည့်ပါ -**\n\n"
        "ဥပမာ: `tzk` သို့မဟုတ် `@tzk`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ နောက်သို့", callback_data=f"premium_{key}")]
        ]),
        parse_mode="Markdown"
    )

# ===== USERNAME HANDLING =====
@dp.message(OrderState.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data["key"]
    order_type = data["order_type"]
    username = message.text.replace("@", "").strip()
    await prompt_payment(message, key, order_type, username, state)

# ===== PAYMENT PROMPT =====
async def prompt_payment(message_or_text, key, order_type, username, state: FSMContext):
    if order_type == "stars":
        pkg = STAR_PACKAGES[key]
        item_text = f"⭐ {pkg['stars']} Telegram Stars"
        price = pkg['price']
    else:
        pkg = PREMIUM_PACKAGES[key]
        item_text = f"👑 Telegram Premium ({pkg['months']} လစာ)"
        price = pkg['price']

    await state.update_data(item_text=item_text, price=price, username=username, key=key, order_type=order_type)
    await state.set_state(OrderState.waiting_for_screenshot)

    invoice_text = (
        f"📝 **အော်ဒါအသေးစိတ် အချက်အလက်**\n\n"
        f"📦 ပစ္စည်း: **{item_text}**\n"
        f"👤 လက်ခံမည့်သူ: **@{username}**\n"
        f"💵 ကျသင့်ငွေ: **{price:,} MMK**\n\n"
        f"{PAYMENT_INFO}\n"
        f"⬇️ ငွေလွှဲပြီးပါက Screenshot ကို ပို့ပေးပါရန်။"
    )

    if isinstance(message_or_text, Message):
        await message_or_text.answer(invoice_text, parse_mode="Markdown")
    else:
        await message_or_text.edit_text(invoice_text, parse_mode="Markdown")

# ===== SCREENSHOT VERIFICATION (ADMIN CONTROL) =====
@dp.message(OrderState.waiting_for_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    admin_btn = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ အော်ဒါအတည်ပြုမည်", callback_data=f"approve_{data['order_type']}_{data['key']}_{data['username']}_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ ငြင်းပယ်မည်", callback_data=f"reject_{message.from_user.id}")
        ]
    ])

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"🔔 **အော်ဒါအသစ် ရရှိပါသည်!**\n\n"
                f"👤 ဝယ်သူ ID: `{message.from_user.id}`\n"
                f"📦 အမယ်: {data['item_text']}\n"
                f"👥 ပို့ရမည့်သူ: @{data['username']}\n"
                f"💵 ပမာဏ: {data['price']:,} MMK\n\n"
                f"ဘောင်ချာ မှန်ကန်ပါက အောက်ပါခလုတ်ဖြင့် Fragment စနစ်ကို လုပ်ဆောင်ခိုင်းနိုင်ပါသည်။",
        reply_markup=admin_btn,
        parse_mode="Markdown"
    )

    await message.answer("✅ **ဘောင်ချာ ပို့ဆောင်မှု အောင်မြင်ပါသည်။**\n\nသင့်အော်ဒါကို စစ်ဆေးပြီး အတည်ပြုပေးပါမည်။ ခဏစောင့်ပေးပါရန်။")

@dp.message(OrderState.waiting_for_screenshot)
async def process_not_photo(message: Message):
    await message.answer("⚠️ ကျေးဇူးပြု၍ ငွေလွှဲဘောင်ချာ ဓာတ်ပုံ (Screenshot) ကို သာ ပို့ပေးပါရန်။")

# ===== ADMIN CALLBACK ACTIONS =====
@dp.callback_query(F.data.startswith("approve_"))
async def admin_approve(callback: CallbackQuery):
    parts = callback.data.split("_")
    order_type, key, username, user_id = parts[1], parts[2], parts[3], parts[4]
    
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n⏳ **Fragment သို့ ချိတ်ဆက်နေပါသည်...**", parse_mode="Markdown")
    await bot.send_message(int(user_id), "⏳ **သင့်အော်ဒါကို ငွေလွှဲမှန်ကန်ကြောင်း အတည်ပြုပြီးပါပြီ။ Fragment မှတစ်ဆင့် ပစ္စည်းလွှဲပြောင်းပေးနေပါသည်။**")

    if order_type == "stars":
        pkg = STAR_PACKAGES[key]
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: fragment.buy_stars(
                username=username,
                amount=pkg["stars"],
                seed=TON_SEED,
                fragment_cookies=FRAGMENT_COOKIES
            )
        )
        if result:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ!**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"✅ **အောင်မြင်ပါသည်!**\n\n⭐ {pkg['stars']} Stars ကို @{username} ထံသို့ အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ။ 🎉")
        else:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **Fragment Error ဖြစ်သွားပါသည်။**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"❌ စနစ်အတွင်း ချို့ယွင်းချက်ရှိ၍ ပစ္စည်းမရောက်ပါက support သို့ ဆက်သွယ်ပါ - @{SUPPORT_USERNAME}")

    elif order_type == "premium":
        pkg = PREMIUM_PACKAGES[key]
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: fragment.buy_premium(
                username=username,
                duration=pkg["months"],
                seed=TON_SEED,
                fragment_cookies=FRAGMENT_COOKIES
            )
        )
        if result:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **Premium အောင်မြင်စွာ ပို့ပြီးပါပြီ!**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"✅ **အောင်မြင်ပါသည်!**\n\n👑 Telegram Premium {pkg['months']} လစာကို @{username} ထံသို့ အောင်မြင်စွာ Gift ပေးပြီးပါပြီ။ 🎉")
        else:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **Fragment Error ဖြစ်သွားပါသည်။**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"❌ Premium တင်ရာတွင် ချို့ယွင်းချက်ရှိပါသဖြင့် support သို့ ဆက်သွယ်ပါ - @{SUPPORT_USERNAME}")

@dp.callback_query(F.data.startswith("reject_"))
async def admin_reject(callback: CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **ဒီအော်ဒါကို ငြင်းပယ်လိုက်သည်။**", parse_mode="Markdown")
    await bot.send_message(int(user_id), f"❌ **သင့်အော်ဒါ ငြင်းပယ်ခံရပါသည်။**\n\nငွေလွှဲမှု မှားယွင်းခြင်း သို့မဟုတ် ဘောင်ချာအဟောင်းဖြစ်နိုင်ပါသည်။ အသေးစိတ်ကို support သို့ မေးမြန်းနိုင်ပါသည် - @{SUPPORT_USERNAME}")

# ==================== ADMIN COMMANDS (.star နှင့် .ton) ====================

def is_admin(user_id: int) -> bool:
    """စစ်ဆေးခြင်း - ဒီ user က admin ဟုတ်/မဟုတ်"""
    return user_id == ADMIN_ID

# ရနိုင်သော Stars ပမာဏများ
VALID_STAR_AMOUNTS = [50, 75, 100, 250, 500, 1000]

# ရနိုင်သော TON ပမာဏများ (ဥပမာ - သင်သတ်မှတ်နိုင်သည်)
VALID_TON_AMOUNTS = [0.5, 1, 2, 5, 10, 20, 50]

@dp.message(F.text.startswith(".star"))
async def admin_star_command(message: Message):
    """.star @username amount - Admin အတွက် Stars ချက်ချင်းထည့်ပေးမယ့် command"""
    
    # Admin မဟုတ်ရင် ငြင်းပယ်
    if not is_admin(message.from_user.id):
        await message.reply("❌ သင်သည် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။ (Admin only)")
        return
    
    # Command ကို parse လုပ်ခြင်း
    parts = message.text.strip().split()
    if len(parts) < 3:
        await message.reply(
            "⚠️ **အသုံးပြုပုံ:**\n"
            "`.star @username ကြယ်အရေအတွက်`\n\n"
            "**ဥပမာ:**\n"
            "`.star @tzk 100`\n"
            "`.star tzk 50`\n\n"
            f"**ရနိုင်သော ပမာဏများ:** {', '.join(map(str, VALID_STAR_AMOUNTS))}"
        )
        return
    
    # Username နဲ့ amount ကို ထုတ်ယူခြင်း
    raw_username = parts[1].replace("@", "").strip()
    try:
        amount = int(parts[2])
    except ValueError:
        await message.reply("❌ ကြယ်အရေအတွက်သည် နံပါတ်သာဖြစ်ရပါမည်။ ဥပမာ - 50, 100, 500")
        return
    
    # ရှိတဲ့ package များထဲမှ ရှိမရှိ စစ်ဆေး
    if amount not in VALID_STAR_AMOUNTS:
        await message.reply(f"❌ ရနိုင်သော ကြယ်အရေအတွက်များ: {', '.join(map(str, VALID_STAR_AMOUNTS))}")
        return
    
    # Processing message ပို့ခြင်း
    processing_msg = await message.reply(f"⏳ `@{raw_username}` ထံသို့ ⭐ {amount} Stars ပို့ဆောင်နေပါသည်...", parse_mode="Markdown")
    
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: fragment.buy_stars(
                username=raw_username,
                amount=amount,
                seed=TON_SEED,
                fragment_cookies=FRAGMENT_COOKIES
            )
        )
        
        if result:
            now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p (MMT)")
            await processing_msg.edit_text(
                f"===== 🧾 **STAR RECEIPT** =====\n\n"
                f"💳 Recipient ⌨️ @{raw_username}\n"
                f"⭐ Stars ⌨️ {amount}\n"
                f"✅ Status: **Success**\n\n"
                f"🔜 Created At:\n{now}\n\n"
                f"======= **Transaction Complete** =======",
                parse_mode="Markdown"
            )
            # Group ထဲမှာ အောင်မြင်ကြောင်း အသိပေး
            await message.answer(f"✅ **@{raw_username}** ထံသို့ ⭐ **{amount} Stars** ပို့ဆောင်ပြီးပါပြီ။")
        else:
            await processing_msg.edit_text(
                f"❌ **Fragment Error**\n"
                f"@{raw_username} ထံသို့ ⭐ {amount} Stars ပို့ဆောင်မှု မအောင်မြင်ပါ။\n"
                f"Fragment API returned: {result}"
            )
    except Exception as e:
        await processing_msg.edit_text(f"❌ **System Error:** `{str(e)}`")
        logging.error(f"Star command error: {e}")

@dp.message(F.text.startswith(".ton"))
async def admin_ton_command(message: Message):
    """.ton @username amount - Admin အတွက် TON ချက်ချင်းထည့်ပေးမယ့် command"""
    
    # Admin မဟုတ်ရင် ငြင်းပယ်
    if not is_admin(message.from_user.id):
        await message.reply("❌ သင်သည် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။ (Admin only)")
        return
    
    # Command ကို parse လုပ်ခြင်း
    parts = message.text.strip().split()
    if len(parts) < 3:
        await message.reply(
            "⚠️ **အသုံးပြုပုံ:**\n"
            "`.ton @username TONပမာဏ`\n\n"
            "**ဥပမာ:**\n"
            "`.ton @tzk 1`\n"
            "`.ton tzk 0.5`\n\n"
            f"**ရနိုင်သော ပမာဏများ (ဥပမာ):** {', '.join(map(str, VALID_TON_AMOUNTS))}"
        )
        return
    
    # Username နဲ့ amount ကို ထုတ်ယူခြင်း
    raw_username = parts[1].replace("@", "").strip()
    try:
        amount = float(parts[2])
    except ValueError:
        await message.reply("❌ TON ပမာဏသည် နံပါတ်သာဖြစ်ရပါမည်။ ဥပမာ - 0.5, 1, 5")
        return
    
    # Processing message ပို့ခြင်း
    processing_msg = await message.reply(f"⏳ `@{raw_username}` ထံသို့ 💎 {amount} TON ပို့ဆောင်နေပါသည်...", parse_mode="Markdown")
    
    try:
        # Fragment API မှာ send_ton သို့မဟုတ် transfer_ton method ရှိမရှိ စစ်ဆေးပါ
        # အောက်ပါအတိုင်း method name ကို သင့် fragment_api_lib နဲ့ ကိုက်ညီအောင် ပြင်ရန်
        if hasattr(fragment, 'send_ton'):
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: fragment.send_ton(
                    username=raw_username,
                    amount=amount,
                    seed=TON_SEED,
                    fragment_cookies=FRAGMENT_COOKIES
                )
            )
        elif hasattr(fragment, 'transfer_ton'):
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: fragment.transfer_ton(
                    username=raw_username,
                    amount=amount,
                    seed=TON_SEED,
                    fragment_cookies=FRAGMENT_COOKIES
                )
            )
        else:
            # ဒီနေရာမှာ သင့်ရဲ့ fragment_api_lib ထဲက TON transfer method အတိုင်း ပြင်ရန်
            await processing_msg.edit_text(
                f"❌ **API Error:**\n"
                f"fragment_api_lib တွင် TON transfer method မတွေ့ပါ။\n"
                f"သင့်ရဲ့ library ထဲက method name ကို စစ်ဆေးပါ။\n\n"
                f"ဥပမာ - `.send_ton` or `.transfer_ton`"
            )
            return
        
        if result:
            now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p (MMT)")
            await processing_msg.edit_text(
                f"===== 🧾 **TON RECEIPT** =====\n\n"
                f"💳 Recipient ⌨️ @{raw_username}\n"
                f"💎 TON Amount ⌨️ {amount} TON\n"
                f"✅ Status: **Success**\n\n"
                f"🔜 Created At:\n{now}\n\n"
                f"======= **Transaction Complete** =======",
                parse_mode="Markdown"
            )
            await message.answer(f"✅ **@{raw_username}** ထံသို့ 💎 **{amount} TON** ပို့ဆောင်ပြီးပါပြီ။")
        else:
            await processing_msg.edit_text(
                f"❌ **Fragment Error**\n"
                f"@{raw_username} ထံသို့ 💎 {amount} TON ပို့ဆောင်မှု မအောင်မြင်ပါ။"
            )
    except Exception as e:
        await processing_msg.edit_text(f"❌ **System Error:** `{str(e)}`")
        logging.error(f"TON command error: {e}")

@dp.message(F.text.startswith(".help"))
async def admin_help(message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Admin only command.")
        return
    
    await message.reply(
        "🛠 **Admin Commands**\n\n"
        "⭐ `.star @username amount` - Stars ချက်ချင်းထည့်ပေးရန်\n"
        "   ဥပမာ: `.star @tzk 100`\n\n"
        "💎 `.ton @username amount` - TON ချက်ချင်းထည့်ပေးရန်\n"
        "   ဥပမာ: `.ton @tzk 1`\n\n"
        "📊 `.bal` - Wallet Balance ကြည့်ရန် (Fragment)\n"
        "💳 `.topup amount` - Wallet ဖြည့်ရန်\n\n"
        "🟢 **System Status:** Online\n"
        "💳 **Date:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

# ===== MAIN EXECUTION =====
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Manual Payment Verification Bot is running with .star and .ton commands...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
