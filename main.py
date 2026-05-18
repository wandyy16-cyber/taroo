import asyncio
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ===== ТВОЙ ТОКЕН =====
BOT_TOKEN = "8610098605:AAFqqSGdzFvvfzY_NaOFBP024MKCa3fANd4"

# ===== ДАННЫЕ АРКАНОВ =====
names = {
    1: "Маг", 2: "Жрица", 3: "Императрица", 4: "Император",
    5: "Иерофант", 6: "Влюбленные", 7: "Колесница", 8: "Сила",
    9: "Отшельник", 10: "Фортуна", 11: "Справедливость",
    12: "Повешенный", 13: "Смерть", 14: "Умеренность",
    15: "Дьявол", 16: "Башня", 17: "Звезда", 18: "Луна",
    19: "Солнце", 20: "Суд", 21: "Мир", 22: "Шут"
}

# ===== КНОПКИ =====
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔮 Мой аркан")],
        [KeyboardButton(text="💑 Совместимость")]
    ],
    resize_keyboard=True
)

# ===== ФУНКЦИЯ РАСЧЕТА АРКАНА =====
def get_arcanum(date):
    digits = [int(d) for d in date if d.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(int(x) for x in str(total))
    return total

# ===== ЗАПУСК БОТА =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(msg):
    await msg.answer("Привет! Я Таро-бот 👋\nВыбери действие:", reply_markup=kb)

@dp.message(lambda msg: msg.text == "🔮 Мой аркан")
async def my_arcanum(msg):
    await msg.answer("Введи дату рождения в формате: ДД.ММ.ГГГГ\nНапример: 18.03.1995")

    @dp.message()
    async def get_date(m):
        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', m.text):
            num = get_arcanum(m.text)
            await m.answer(f"✨ Твой аркан: {num} — {names[num]}", reply_markup=kb)
        else:
            await m.answer("❌ Неправильно! Пиши как: 18.03.1995")

@dp.message(lambda msg: msg.text == "💑 Совместимость")
async def compatibility(msg):
    await msg.answer("Введи ДАТУ ПЕРВОГО человека: ДД.ММ.ГГГГ")
    
    @dp.message()
    async def get_first(m):
        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', m.text):
            first = get_arcanum(m.text)
            await m.answer("Теперь ДАТУ ВТОРОГО человека:")
            
            @dp.message()
            async def get_second(m2):
                if re.match(r'^\d{2}\.\d{2}\.\d{4}$', m2.text):
                    second = get_arcanum(m2.text)
                    total = first + second
                    if total > 22:
                        total = total - 22
                    await m2.answer(
                        f"💑 Результат:\n\n"
                        f"Первый: {first} — {names[first]}\n"
                        f"Второй: {second} — {names[second]}\n\n"
                        f"💞 Совместимость: {total} — {names[total]}",
                        reply_markup=kb
                    )
                else:
                    await m2.answer("❌ Ошибка! Формат: ДД.ММ.ГГГГ")

async def main():
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
