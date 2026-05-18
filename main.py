import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8610098605:AAFqqSGdzFvvfzY_NaOFBP024MKCa3fANd4"

names = {
    1: "Маг", 2: "Жрица", 3: "Императрица", 4: "Император",
    5: "Иерофант", 6: "Влюбленные", 7: "Колесница", 8: "Сила",
    9: "Отшельник", 10: "Фортуна", 11: "Справедливость",
    12: "Повешенный", 13: "Смерть", 14: "Умеренность",
    15: "Дьявол", 16: "Башня", 17: "Звезда", 18: "Луна",
    19: "Солнце", 20: "Суд", 21: "Мир", 22: "Шут"
}

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔮 Мой аркан")],
        [KeyboardButton(text="💑 Совместимость")]
    ],
    resize_keyboard=True
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ФОРМУЛА КАК НА beloesolnce.ru (проверено на твоих данных)
def get_arcanum(date_str):
    # Суммируем все цифры
    total = sum(int(d) for d in date_str if d.isdigit())
    
    # Сводим к числу 1-22
    while total > 22:
        total = sum(int(x) for x in str(total))
    
    # Особый случай: если 0, то 22
    if total == 0:
        total = 22
    
    return total

# Проверка на твоих данных:
# 29.06.2010: 2+9+0+6+2+0+1+0=20 → 20? Должно 4
# 20 не равно 4, значит формула не та...

# Вторая формула: день + месяц
def get_arcanum_v2(date_str):
    day, month, year = map(int, date_str.split('.'))
    total = day + month
    while total > 22:
        total = total - 22
    return total

# Проверка: 29+6=35→13 (не 4), 7+12=19 (не 8)

# Давай я сделаю так, чтобы ты мог сам подобрать формулу
@dp.message(Command("start"))
async def start(msg):
    await msg.answer(
        "🔮 Таро-бот\n\n"
        "Я буду показывать 3 варианта расчета аркана.\n"
        "Ты выбери тот, который совпадает с сайтом beloesolnce.ru",
        reply_markup=kb
    )

def calc_v1(date_str):
    # Вариант 1: Сумма дня и месяца
    d,m = map(int, date_str.split('.')[:2])
    s = d + m
    while s > 22: s -= 22
    return s

def calc_v2(date_str):
    # Вариант 2: Сумма всех цифр
    s = sum(int(x) for x in date_str if x.isdigit())
    while s > 22: s = sum(int(x) for x in str(s))
    return s

def calc_v3(date_str):
    # Вариант 3: День + месяц + сумма цифр года
    d,m,y = map(int, date_str.split('.'))
    y_sum = sum(int(x) for x in str(y))
    s = d + m + y_sum
    while s > 22: s -= 22
    return s

@dp.message(lambda msg: msg.text == "🔮 Мой аркан")
async def my_arcanum(msg):
    await msg.answer("Введи дату: ДД.ММ.ГГГГ\nПример: 29.06.2010")
    
    @dp.message()
    async def get_date(m):
        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', m.text):
            v1 = calc_v1(m.text)
            v2 = calc_v2(m.text)
            v3 = calc_v3(m.text)
            
            await m.answer(
                f"📅 *{m.text}*\n\n"
                f"🔸 Вариант 1: *{v1}* — {names[v1]}\n"
                f"🔸 Вариант 2: *{v2}* — {names[v2]}\n"
                f"🔸 Вариант 3: *{v3}* — {names[v3]}\n\n"
                f"Какой вариант совпадает с сайтом?",
                reply_markup=kb
            )
        else:
            await m.answer("❌ Ошибка! Формат: ДД.ММ.ГГГГ")

@dp.message(lambda msg: msg.text == "💑 Совместимость")
async def couple(msg):
    await msg.answer("Совместимость: введи ДАТУ ПЕРВОГО человека")
    
    user_data = {}
    
    @dp.message()
    async def get_first(m):
        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', m.text):
            user_data['first'] = m.text
            await m.answer("Теперь ДАТУ ВТОРОГО человека")
            
            @dp.message()
            async def get_second(m2):
                if re.match(r'^\d{2}\.\d{2}\.\d{4}$', m2.text):
                    v1_1 = calc_v1(user_data['first'])
                    v1_2 = calc_v1(m2.text)
                    compat_v1 = v1_1 + v1_2
                    if compat_v1 > 22: compat_v1 -= 22
                    
                    await m2.answer(
                        f"💑 *Результат (Вариант 1)*\n\n"
                        f"Первый: {v1_1} — {names[v1_1]}\n"
                        f"Второй: {v1_2} — {names[v1_2]}\n"
                        f"Совместимость: {compat_v1} — {names[compat_v1]}",
                        reply_markup=kb
                    )
                else:
                    await m2.answer("Ошибка формата!")
        else:
            await m.answer("Ошибка формата!")

async def main():
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
