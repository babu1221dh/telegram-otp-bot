import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Token এবং অন্যান্য কনফিগারেশন
TOKEN = "8600262077:AAE41N9dOTgiY2Q_r_ZdsIQrwjJdvQN7gOk"
OTP_PRICE = 0.5
CHANNEL_USERNAME = "@YourChannelUsername"  # আপনার চ্যানেলের ইউজারনেম এখানে দিন (যেমন: @TrendBurst)

# ইউজার ব্যালেন্স ট্র্যাক করার ডিকশনারি (টেম্পোরারি)
user_balances = {}

async def check_subscription(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # চ্যানেল সাবস্ক্রাইব করা আছে কিনা চেক করা
    is_subscribed = await check_subscription(context.bot, user_id)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔄 Joined / Check", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ বটটি ব্যবহার করতে হলে অবশ্যই আমাদের চ্যানেলে জয়েন করতে হবে!\n\nদয়া করে চ্যানেল জয়েন করে নিচের বাটনে ক্লিক করুন:",
            reply_markup=reply_markup
        )
        return

    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = user_balances.get(user_id, 0.0)
    
    keyboard = [
        [InlineKeyboardButton("📱 Instagram OTP", callback_data="get_instagram")],
        [InlineKeyboardButton("📘 Facebook OTP", callback_data="get_facebook")],
        [InlineKeyboardButton("💬 Discord OTP", callback_data="get_discord")],
        [InlineKeyboardButton("🚗 Uber OTP", callback_data="get_uber")],
        [InlineKeyboardButton("⚽ 1xBet OTP", callback_data="get_1xbet")],
        [InlineKeyboardButton("💰 My Balance", callback_data="balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"🤖 **OTP Bot Menu**\n\n"
        f"👤 আপনার আইডি: `{user_id}`\n"
        f"💵 বর্তমান ব্যালেন্স: `${balance}`\n"
        f"🏷️ প্রতি OTP এর মূল্য: `${OTP_PRICE}`\n\n"
        f"নিচের সার্ভিসগুলো থেকে আপনার প্রয়োজনীয় সার্ভিসটি সিলেক্ট করুন:"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "check_sub":
        is_subscribed = await check_subscription(context.bot, user_id)
        if is_subscribed:
            await query.message.delete()
            await show_main_menu(update, context)
        else:
            await query.answer("❌ আপনি এখনো চ্যানেলে জয়েন করেননি!", show_alert=True)
        return

    if query.data == "balance":
        balance = user_balances.get(user_id, 0.0)
        await query.answer(f"আপনার বর্তমান ব্যালেন্স: ${balance}", show_alert=True)
        return

    # সার্ভিস অনুযায়ী ফাইল ম্যাপ করা
    service_files = {
        "get_instagram": "instagram.txt",
        "get_facebook": "facebook.txt",
        "get_discord": "discord.txt",
        "get_uber": "uber.txt",
        "get_1xbet": "1xbet.txt"
    }

    if query.data in service_files:
        filename = service_files[query.data]
        
        # ফাইল থেকে নম্বর রিড করা এবং একটি রেন্ডম নম্বর নেওয়া
        if not os.path.exists(filename):
            await query.answer("❌ এই সার্ভিসের কোনো নম্বর ফাইল পাওয়া যায়নি!", show_alert=True)
            return

        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # খালি লাইন বা ফাঁকা স্পেস ফিল্টার করা
        numbers = [line.strip() for line in lines if line.strip()]

        if not numbers:
            await query.answer("⚠️ দুঃখিত, এই মুহূর্তে এই সার্ভিসে কোনো নম্বর স্টক নেই!", show_alert=True)
            return

        # প্রথম নম্বরটি নেওয়া এবং বাকিগুলো আবার ফাইলে সেভ করা (নম্বরটি রিমুভ করে দেওয়া)
        selected_number = numbers[0]
        remaining_numbers = numbers[1:]

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_numbers) + ("\n" if remaining_numbers else ""))

        # ব্যালেন্স আপডেট করা
        current_balance = user_balances.get(user_id, 0.0)
        user_balances[user_id] = round(current_balance + OTP_PRICE, 2)

        # ইউজারকে নম্বরটি পাঠানো
        await query.message.reply_text(
            f"✅ সফলভাবে নম্বর নেওয়া হয়েছে!\n\n"
            f"📞 নম্বর: `{selected_number}`\n"
            f"💵 আপনার অ্যাকাউন্ট থেকে কাটা হয়েছে: `${OTP_PRICE}`\n"
            f"💰 নতুন ব্যালেন্স: `${user_balances[user_id]}`",
            parse_mode="Markdown"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
