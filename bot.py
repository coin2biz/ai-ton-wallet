import json,os,time
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes

TOKEN=os.getenv("BOT_TOKEN")
DB_FILE = "users.json" # On Render, add Disk at /data for permanent

def load_db():
 if not os.path.exists(DB_FILE): return {}
 try:
  with open(DB_FILE,"r") as f: return json.load(f)
 except: return {}

def save_db(db):
 with open(DB_FILE,"w") as f: json.dump(db,f)

def get_user(db,uid):
 uid=str(uid)
 if uid not in db:
  db[uid]={"balance":10,"last_mine":0,"referrals":0,"referred_by":None,"name":""}
 return db[uid]

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db()
 user=update.effective_user
 uid=str(user.id)

 # Get referral code from /start 6829410 OR Web App startapp
 ref = None
 if context.args:
  ref = str(context.args[0])
 # For Mini App: check start_param from web app
 if not ref and update.message and update.message.text and "startapp=" in update.message.text:
  try: ref = update.message.text.split("startapp=")[-1].split()[0]
  except: pass

 u = get_user(db, uid)
 u["name"] = user.first_name

 # Only count if new user and not self-referral and never referred before
 if ref and ref!= uid and u["referred_by"] is None:
  # Ensure referrer exists in DB
  ref_user = get_user(db, ref)
  ref_user["referrals"] += 1
  ref_user["balance"] += 10 # Referrer gets 10 PAT
  u["referred_by"] = ref
  u["balance"] += 5 # New user gets 5 PAT bonus
  print(f"REFERRAL: {ref} invited {uid}")

 save_db(db)
 link=f"https://t.me/{context.bot.username}?start={uid}"
 txt=f"🚀 PURE AI TOKEN\nWelcome {user.first_name}!\n\n💰 Balance: {u['balance']} PAT\n👥 Friends: {u['referrals']}\n\n⛏️ /mine - Earn 2 PAT\n👥 /referral - Invite = 10 PAT\n💼 /balance - Check\n🏆 /top - Top 10\n\n🔗 Your Link:\n{link}\n\nInvite 100 = 1000 PAT FREE!"
 await update.message.reply_text(txt)

async def mine(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db();uid=str(update.effective_user.id);u=get_user(db,uid);now=time.time()
 if now-u.get("last_mine",0)<21600:
  left=int((21600-(now-u.get("last_mine",0)))/3600)
  await update.message.reply_text(f"⏳ Wait {left}h left da!");return
 u["last_mine"]=now;u["balance"]+=2;save_db(db)
 await update.message.reply_text(f"⛏️ Mined +2 PAT\n💰 Balance: {u['balance']} PAT")

async def balance(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db();u=get_user(db,str(update.effective_user.id))
 await update.message.reply_text(f"💰 Balance: {u['balance']} PAT\n👥 Referrals: {u['referrals']}\n🔗 Referred by: {u['referred_by'] or 'None'}")

async def referral(update:Update,context:ContextTypes.DEFAULT_TYPE):
 uid=str(update.effective_user.id)
 db=load_db();u=get_user(db,uid)
 link=f"https://t.me/{context.bot.username}?start={uid}"
 await update.message.reply_text(f"👥 INVITE & EARN 10 PAT\n\nFriends: {u['referrals']}\nEarned: {u['referrals']*10} PAT\n\nYour Link:\n{link}\n\n1 Friend = 10 PAT!")

async def top(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db();top=sorted(db.items(),key=lambda x:x[1].get('balance',0),reverse=True)[:10]
 msg="🏆 TOP 10 LEADERBOARD\n\n";c=1
 for k,v in top:msg+=f"{c}. {v.get('name','User')[:8]} - {v.get('balance',0)} PAT\n";c+=1
 await update.message.reply_text(msg)

app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("mine",mine))
app.add_handler(CommandHandler("balance",balance))
app.add_handler(CommandHandler("referral",referral))
app.add_handler(CommandHandler("top",top))
print("Bot Running - Referral Fixed")
app.run_polling()
