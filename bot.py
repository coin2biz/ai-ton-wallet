import os, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["ai_ton_wallet"]
users_collection = db["users"]

print("✅ MongoDB Connected")

def get_user(uid):
    uid = str(uid)
    user = users_collection.find_one({"user_id": uid})
    if not user:
        user = {"user_id": uid, "balance": 10, "last_mine": 0, "referrals": 0, "referred_by": None, "name": ""}
        users_collection.insert_one(user)
    return user

def update_user(uid, data):
    users_collection.update_one({"user_id": str(uid)}, {"$set": data})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    ref = None
    if context.args:
        ref = str(context.args[0])
    if not ref and update.message and "startapp=" in update.message.text:
        try: ref = update.message.text.split("startapp=")[-1].split()[0]
        except: pass
    u = get_user(uid)
    update_user(uid, {"name": user.first_name})
    if ref and ref != uid and u.get("referred_by") is None:
        ref_user = get_user(ref)
        users_collection.update_one({"user_id": ref}, {"$inc": {"referrals": 1, "balance": 10}})
        update_user(uid, {"referred_by": ref, "balance": u["balance"] + 5})
    u = get_user(uid)
    link = f"https://t.me/{context.bot.username}?start={uid}"
    txt = f"🚀 PURE AI TOKEN\nWelcome {user.first_name}!\n\n💰 Balance: {u['balance']} PAT\n👥 Friends: {u['referrals']}\n\nYour Link:\n{link}"
    await update.message.reply_text(txt)

async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    u = get_user(uid)
    now = time.time()
    if now - u.get("last_mine", 0) < 21600:
        left = int((21600 - (now - u.get("last_mine", 0))) / 3600)
        await update.message.reply_text(f"⏳ Wait {left}h left!"); return
    update_user(uid, {"last_mine": now, "balance": u["balance"] + 2})
    u = get_user(uid)
    await update.message.reply_text(f"⛏️ Mined +2 PAT\n💰 Balance: {u['balance']} PAT")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(str(update.effective_user.id))
    await update.message.reply_text(f"💰 Balance: {u['balance']} PAT\n👥 Referrals: {u['referrals']}")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    u = get_user(uid)
    link = f"https://t.me/{context.bot.username}?start={uid}"
    await update.message.reply_text(f"👥 Friends: {u['referrals']}\nYour Link:\n{link}")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = users_collection.find().sort("balance", -1).limit(10)
    msg = "🏆 TOP 10\n\n"; c = 1
    for v in top_users:
        msg += f"{c}. {v.get('name','User')[:8]} - {v.get('balance',0)} PAT\n"; c+=1
    await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mine", mine))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("referral", referral))
app.add_handler(CommandHandler("top", top))
app.run_polling()
