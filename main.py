import pickle
from datetime import datetime

from aiogram.utils import exceptions, executor
from aiogram import Bot, Dispatcher, types

from config import Config

with open('content.pkl', 'rb') as f:
    loaded_str = pickle.load(f)


bot = Bot(token=Config.TOKEN)
dp = Dispatcher(bot)


def get_start_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    schedule_button = types.KeyboardButton('Расписание')
    markup.add(schedule_button)
    return markup


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.reply(
        'Привет, Ксюшик❤️! Любое твое сообщение или кнопка - расписание',
        reply_markup=get_start_markup())


@dp.message_handler(content_types='text')
async def callback_handler(callback: types.CallbackQuery):
    if callback:
        tech_time = loaded_str.split('TECHNICAL INFO \n')[1]
        if tech_time < datetime.today().strftime("%d-%b-%Y (%H:%M:%S.%f)"):
            await bot.send_message(chat_id=callback.from_user.id, text="YES ITS TRUE")
        data = loaded_str.split('='*55)
        for message in data:
            if message:
                await bot.send_message(chat_id=callback.from_user.id, text=message)
