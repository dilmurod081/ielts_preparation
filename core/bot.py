import asyncio
import logging
import django
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from asgiref.sync import sync_to_async

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myielts_site.settings')  # ← Replace with your project name
django.setup()

from core.models import Profile

# --- Config ---
BOT_TOKEN = '7068733907:AAGb5ri9rn_w7coRlPLnUfoFIfap1w8L4vg'
ADMIN_ID = 6667155546  # Must be an integer

# --- Init ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Django ORM access helpers ---
@sync_to_async
def get_profile_by_user_id(user_id):
    return Profile.objects.select_related('user').get(user__id=user_id)

@sync_to_async
def unblock_user(profile):
    profile.is_blocked = False
    profile.save()

# --- Aiogram handler ---
@dp.message()
async def handle_admin_reply(message: Message):
    if message.chat.id != ADMIN_ID:
        await message.answer("❌ You are not authorized to perform this action.")
        return

    parts = message.text.lower().strip().split()
    if len(parts) != 2:
        await message.answer("⚠️ Invalid format. Use: yes [user_id] or no [user_id]")
        return

    command, user_id_str = parts
    try:
        user_id = int(user_id_str)
        profile = await get_profile_by_user_id(user_id)
        username = profile.user.username

        if command == "yes":
            await unblock_user(profile)
            await message.answer(f"✅ User '{username}' (ID: {user_id}) has been unblocked.")
        elif command == "no":
            await message.answer(f"❌ User '{username}' (ID: {user_id}) will remain blocked.")
        else:
            await message.answer("⚠️ Unknown command. Use 'yes [user_id]' or 'no [user_id]'")

    except Profile.DoesNotExist:
        await message.answer(f"🚫 No profile found for User ID {user_id_str}.")
    except ValueError:
        await message.answer("⚠️ Invalid user ID. It must be a number.")
    except Exception as e:
        await message.answer(f"🚨 An unexpected error occurred:\n{e}")

# --- Entry point ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
