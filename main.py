import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import config

logging.basicConfig(level=logging.INFO)
bot = Bot(config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())


class Game(StatesGroup):
    guessing_number = State()


@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.update_data(rint=random.randint(1, 100), tries=10)
    await message.answer('Я загадал число от 1 до 100\n'
                         'У вас есть 10 попыток')
    await state.set_state(Game.guessing_number)


@dp.message(Command("stop"))
@dp.message(Text(text="отмена", ignore_case=True))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Игра прервана")


@dp.message(Game.guessing_number)
async def answer(message: types.Message, state: FSMContext):
    tries = (await state.get_data())['tries']
    if tries > 1:
        try:
            number = int(message.text)
        except ValueError:
            await message.reply('Введите число')
            return None
        rint = (await state.get_data())['rint']
        if rint > number:
            await state.update_data(tries=tries - 1)
            await message.reply("Загаданное число больше\n"
                                f"У вас осталось {tries-1} попыток")
        elif rint < number:
            await state.update_data(tries=tries - 1)
            await message.reply('Загаданное число меньше\n'
                                f"У вас осталось {tries-1} попыток")
        else:
            await message.reply('Вы отгадали число!')
            await state.clear()
    else:
        await message.reply('У вас закончились попытки. Вы проиграли')
        await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
