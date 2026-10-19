require('dotenv').config();
const express = require('express');
const { Telegraf } = require('telegraf');

const app = express();
const PORT = process.env.PORT || 3000;

const WALLET = "UQAEDooFclpORMBH4KHniCJq1O46wEyJ1hGzudZjXpR4P6Bg";
const RATE = 1000;

const bot = new Telegraf(process.env.BOT_TOKEN);

bot.start((ctx) => {
  return ctx.reply(
`🚀 *PURE AI TOKEN - Payment Wallet*

💎 *TON Wallet Address:*
\`${WALLET}\`

💰 *Rate:* 1 TON = ${RATE} PURE AI

📥 Send TON to above address
📤 Then send /check

Commands:
/buy - How to buy
/wallet - Show wallet address
/rate - Current rate`,
    { parse_mode: 'Markdown' }
  );
});

bot.command('wallet', (ctx) => ctx.reply(`Your payment wallet:\n${WALLET}`));
bot.command('rate', (ctx) => ctx.reply(`1 TON = ${RATE} PURE AI TOKENS`));
bot.command('buy', (ctx) => ctx.reply(`Send TON to:\n${WALLET}\n\nMinimum: 0.5 TON`));
bot.command('check', (ctx) => ctx.reply('Send your Transaction Hash to @coin2biz for verification ✅'));

bot.launch().then(()=>console.log('Bot started'));

app.get('/', (req,res)=> res.send(`AI TON WALLET LIVE ✅\nWallet: ${WALLET}\nPURE AI TOKEN Payment Gateway`));
app.get('/health', (req,res)=> res.send('OK'));

app.listen(PORT, ()=> console.log('Running on '+PORT));
