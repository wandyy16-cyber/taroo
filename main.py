import asyncio
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# ========== КОНФИГУРАЦИЯ ==========
# Замени на свой токен, который получил от @BotFather
BOT_TOKEN = "7168480194:AAHhyS3nHgQ_9Yq7O4pcd_8X5nS9bwFPh2c"

# ========== ДАННЫЕ АРКАНОВ ==========
ARCANUM_NAMES = {
    1: "Маг", 2: "Верховная Жрица", 3: "Императрица", 4: "Император",
    5: "Иерофант", 6: "Влюбленные", 7: "Колесница", 8: "Сила",
    9: "Отшельник", 10: "Колесо Фортуны", 11: "Справедливость",
    12: "Повешенный", 13: "Смерть", 14: "Умеренность",
    15: "Дьявол", 16: "Башня", 17: "Звезда", 18: "Луна",
    19: "Солнце", 20: "Суд", 21: "Мир", 22: "Шут"
}

ARCANUM_DESCRIPTIONS = {
    1: "🗝 Ты обладаешь талантом убеждения и манифестации. Все инструменты уже у тебя в руках.",
    2: "🌙 Доверяй интуиции. Сейчас важно слушать внутренний голос, а не логику.",
    3: "🌸 Творчество и изобилие. Время созидать, заботиться и принимать новые идеи.",
    4: "🏛 Структура и власть. Строй системы, бери ответственность, будь надёжной опорой.",
    5: "📜 Учитель и традиции. Ищи мудрость в проверенных источниках или делись знанием.",
    6: "💖 Выбор и связь. Твоя задача — сделать выбор сердцем, а не умом.",
    7: "⚡️ Движение и победа. Бери инициативу, действуй быстро, преодолевай препятствия.",
    8: "🦁 Контроль и страсть. Укроти внутреннего зверя, но не теряй силу духа.",
    9: "🏔 Уединение и мудрость. Пауза нужна, чтобы увидеть истинный путь.",
    10: "🎡 Удача и циклы. Судьба ведёт тебя — отпусти контроль и доверься потоку.",
    11: "⚖️ Карма и истина. Поступай честно — и мир ответит тем же.",
    12: "🌀 Жертва ради прозрения. Иногда нужно отпустить, чтобы увидеть новое.",
    13: "💀 Трансформация. Что-то заканчивается, чтобы родилось лучшее. Не бойся.",
    14: "⚖️ Алхимия и баланс. Найди золотую середину, смягчай крайности.",
    15: "⛓ Искушение и тени. Осознай свои слабости — и они перестанут управлять тобой.",
    16: "💥 Крах иллюзий. Разрушение старого ради настоящей свободы.",
    17: "✨ Надежда и вдохновение. Ты под защитой звёзд, верь в чудо.",
    18: "🌊 Тайны и страхи. Доверься подсознанию, но не теряй связь с реальностью.",
    19: "☀️ Успех и радость. Твой час сиять! Делись светом с другими.",
    20: "📯 Возрождение. Проснись для новой главы, прошлое отпущено.",
    21: "🌍 Завершение цикла. Ты достиг целостности, впереди новый уровень.",
    22: "🌀 Бесконечность и свобода. Ты вне правил. Твоя сила — в спонтанности и чистоте."
}

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    """Главная клавиатура бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔮 Мой Аркан")],
            [KeyboardButton(text="💞 Аркан пары")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def validate_date(date_str: str) -> bool:
    """Проверяет корректность даты в формате ДД.ММ.ГГГГ"""
    pattern = r'^(\d{2})\.(\d{2})\.(\d{4})$'
    match = re.match(pattern, date_str)
    if not match:
        return False
    
    day, month, year = map(int, match.groups())
    
    try:
        datetime(year, month, day)
        return 1900 <= year <= datetime.now().year
    except ValueError:
        return False

def calculate_arcanum(date_str: str) -> int:
    """Рассчитывает аркан по дате рождения"""
    # Убираем все не-цифры
    digits = [int(ch) for ch in date_str if ch.isdigit()]
    total = sum(digits)
    
    # Сводим к числу от 1 до 22
    while total > 22:
        total = sum(int(d) for d in str(total))
    
    return total

def calculate_compatibility(arcanum1: int, arcanum2: int) -> int:
    """Рассчитывает аркан совместимости двух людей"""
    total = arcanum1 + arcanum2
    if total > 22:
        total = total - 22
    return total

def get_arcanum_text(arcanum_number: int) -> str:
    """Возвращает красивое сообщение с описанием аркана"""
    name = ARCANUM_NAMES.get(arcanum_number, "Неизвестный аркан")
    description = ARCANUM_DESCRIPTIONS.get(arcanum_number, "Описание отсутствует")
    return f"🎴 *{arcanum_number} — {name}*\n\n{description}"

# ========== СОСТОЯНИЯ БОТА ==========
class TarotStates(StatesGroup):
    waiting_birthdate = State()  # Ждем дату рождения пользователя
    waiting_first_birthdate = State()  # Ждем первую дату для пары
    waiting_second_birthdate = State()  # Ждем вторую дату для пары

# ========== ОБРАБОТЧИКИ КОМАНД ==========
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "🌟 *Добро пожаловать в Таро-бот!* 🌟\n\n"
        "Я помогу тебе узнать твой личный аркан по дате рождения "
        "и рассчитать совместимость с другим человеком.\n\n"
        "🔮 *Мой Аркан* — узнай свой старший аркан Таро\n"
        "💞 *Аркан пары* — рассчитай совместимость\n\n"
        "Просто нажми на нужную кнопку 👇"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message):
    """Обработчик команды /help и кнопки Помощь"""
    help_text = (
        "📖 *Как пользоваться ботом:*\n\n"
        "🔮 *Мой Аркан* — введи свою дату рождения в формате ДД.ММ.ГГГГ\n"
        "   Пример: 18.03.1995\n\n"
        "💞 *Аркан пары* — сначала введи свою дату, затем дату партнёра\n\n"
        "❓ *Помощь* — показать это сообщение\n\n"
        "📌 *Важно:* дата должна быть реальной и в диапазоне 1900-2026 гг."
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())

@router.message(F.text == "🔮 Мой Аркан")
async def my_arcanum_start(message: Message, state: FSMContext):
    """Начинаем процесс получения личного аркана"""
    await message.answer(
        "📅 *Введи свою дату рождения*\n\n"
        "Отправь дату в формате: *ДД.ММ.ГГГГ*\n"
        "Пример: 18.03.1995\n\n"
        "Для отмены отправь /cancel",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(TarotStates.waiting_birthdate)

@router.message(F.text == "💞 Аркан пары")
async def couple_arcanum_start(message: Message, state: FSMContext):
    """Начинаем процесс получения аркана пары"""
    await message.answer(
        "💑 *Рассчитаем совместимость*\n\n"
        "Сначала введи *свою* дату рождения в формате: *ДД.ММ.ГГГГ*\n"
        "Пример: 18.03.1995\n\n"
        "Для отмены отправь /cancel",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(TarotStates.waiting_first_birthdate)

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущей операции"""
    await state.clear()
    await message.answer(
        "✅ Операция отменена",
        reply_markup=get_main_keyboard()
    )

@router.message(TarotStates.waiting_birthdate)
async def process_birthdate(message: Message, state: FSMContext):
    """Обрабатываем дату рождения для личного аркана"""
    date_str = message.text.strip()
    
    if not validate_date(date_str):
        await message.answer(
            "❌ *Неверный формат или дата*\n\n"
            "Пожалуйста, введи дату в формате: *ДД.ММ.ГГГГ*\n"
            "Пример: 18.03.1995\n\n"
            "Убедись, что дата существует (например, 31.02.2023 — неверно)"
        )
        return
    
    # Рассчитываем аркан
    arcanum = calculate_arcanum(date_str)
    arcanum_text = get_arcanum_text(arcanum)
    
    # Отправляем результат
    result_text = (
        f"📅 *Твоя дата рождения:* {date_str}\n\n"
        f"{arcanum_text}\n\n"
        "✨ Этот аркан показывает твои врожденные таланты и жизненный путь."
    )
    
    await message.answer(result_text, reply_markup=get_main_keyboard())
    await state.clear()

@router.message(TarotStates.waiting_first_birthdate)
async def process_first_birthdate(message: Message, state: FSMContext):
    """Обрабатываем первую дату для пары"""
    date_str = message.text.strip()
    
    if not validate_date(date_str):
        await message.answer(
            "❌ *Неверный формат или дата*\n\n"
            "Введи дату в формате: *ДД.ММ.ГГГГ*\n"
            "Пример: 18.03.1995"
        )
        return
    
    # Сохраняем первую дату
    await state.update_data(first_date=date_str)
    
    await message.answer(
        "✅ Первая дата принята!\n\n"
        "Теперь введи *дату рождения партнёра* в формате: *ДД.ММ.ГГГГ*\n"
        "Пример: 20.07.1993"
    )
    await state.set_state(TarotStates.waiting_second_birthdate)

@router.message(TarotStates.waiting_second_birthdate)
async def process_second_birthdate(message: Message, state: FSMContext):
    """Обрабатываем вторую дату и выводим результат совместимости"""
    date_str = message.text.strip()
    
    if not validate_date(date_str):
        await message.answer(
            "❌ *Неверный формат или дата*\n\n"
            "Введи дату в формате: *ДД.ММ.ГГГГ*\n"
            "Пример: 20.07.1993"
        )
        return
    
    # Получаем первую дату
    data = await state.get_data()
    first_date = data.get('first_date')
    
    # Рассчитываем арканы
    arcanum1 = calculate_arcanum(first_date)
    arcanum2 = calculate_arcanum(date_str)
    compatibility = calculate_compatibility(arcanum1, arcanum2)
    
    # Формируем результат
    result_text = (
        f"💑 *Результат совместимости*\n\n"
        f"🔮 *Первый человек:* {first_date}\n"
        f"{get_arcanum_text(arcanum1)}\n\n"
        f"🔮 *Второй человек:* {date_str}\n"
        f"{get_arcanum_text(arcanum2)}\n\n"
        f"💞 *Аркан совместимости:*\n"
        f"{get_arcanum_text(compatibility)}\n\n"
        "✨ Этот аркан показывает, какая энергия возникает между вами."
    )
    
    await message.answer(result_text, reply_markup=get_main_keyboard())
    await state.clear()

@router.message()
async def handle_unknown(message: Message):
    """Обработка неизвестных сообщений"""
    await message.answer(
        "❓ Я не понимаю эту команду\n\n"
        "Пожалуйста, используй кнопки меню или команды:\n"
        "/start — начать работу\n"
        "/help — помощь\n"
        "/cancel — отменить текущую операцию",
        reply_markup=get_main_keyboard()
    )

# ========== ЗАПУСК БОТА ==========
async def main():
    """Главная функция запуска бота"""
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    # Запускаем бота
    print("🤖 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
