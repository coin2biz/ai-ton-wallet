import json,os,time
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes

TOKEN=os.getenv("BOT_TOKEN")

def load_db():
 if not os.path.exists("users.json"):return {}
 try:
  with open("users.json","r") as f:return json.load(f)
 except:return {}

def save_db(db):
 with open("users.json","w") as f:json.dump(db,f)

def get_user(db,uid):
 uid=str(uid)
 if uid not in db:db[uid]={"balance":10,"last_mine":0,"referrals":0,"referred_by":None}
 return db[uid]

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db();user=update.effective_user;uid=str(user.id)
 ref=None
 if context.args:ref=context.args[0]
 if ref and ref!=uid and ref in db and db.get(uid,{}).get("referred_by") is None:
  db[ref]["balance"]+=10;db[ref]["referrals"]+=1
 u=get_user(db,uid)
 if ref and ref!=uid and u["referred_by"] is None:
  u["referred_by"]=ref;u["balance"]+=5
 save_db(db)
 link=f"https://t.me/{context.bot.username}?start={uid}"
 txt=f"🚀 PURE AI TOKEN\nWelcome {user.first_name}!\n\n💰 Balance: {u['balance']} PAT\n\n⛏️ /mine - Earn 2 PAT\n👥 /referral - Invite = 10 PAT\n💼 /balance - Check\n🏆 /top - Top 10\n\n🔗 Your Link:\n{link}\n\nInvite 100 = 1000 PAT FREE!"
 await update.message.reply_text(txt)

async def mine(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db();uid=str(update.effective_user.id);u=get_user(db,uid);now=time.time()
 if now-u.get("last_mine",0)<21600:
  await update.message.reply_text("⏳ Wait 6h da!");return
 u["last_mine"]=now;u["balance"]+=2;save_db(db)
 await update.message.reply_text(f"⛏️ Mined +2 PAT\n💰 Balance: {u['balance']} PAT")

async def balance(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db();u=get_user(db,str(update.effective_user.id))
 await update.message.reply_text(f"💰 Balance: {u['balance']} PAT\n👥 Referrals: {u['referrals']}")

async def referral(update:Update,context:ContextTypes.DEFAULT_TYPE):
 uid=str(update.effective_user.id);link=f"https://t.me/{context.bot.username}?start={uid}"
 await update.message.reply_text(f"👥 INVITE & EARN 10 PAT\n\nYour Link:\n{link}\n\n1 Friend = 10 PAT!")

async def top(update:Update,context:ContextTypes.DEFAULT_TYPE):
 db=load_db();top=sorted(db.items(),key=lambda x:x[1].get('balance',0),reverse=True)[:10]
 msg="🏆 TOP 10 LEADERBOARD\n\n"
 c=1
 for k,v in top:msg+=f"{c}. {k[:4]}*** - {v.get('balance',0)} PAT\n";c+=1
 await update.message.reply_text(msg)

app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("mine",mine))
app.add_handler(CommandHandler("balance",balance))
app.add_handler(CommandHandler("referral",referral))
app.add_handler(CommandHandler("top",top))
print("Bot Running")
app.run_polling()
