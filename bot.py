"""Telegram-бот группы 26-03 БД."""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

SITE_URL = "https://26-03-bd.vercel.app"

# Токен бота. Переменная окружения BOT_TOKEN (Railway → Variables) имеет приоритет.
BOT_TOKEN = "8053408935:AAG1xTQ4GbOwzYk6PzvgX3rSos76EFJjS4E"

WELCOME_TEXT = (
    "Привет! Это, ⁿØ ᶜᵃᵖ 👋\n\n"
    "В этом боте находится инструкция по использованию приложения группы 26-03 БД. "
    "Также отсюда можно быстро открыть само приложение"
)

# Инструкция разбита на части, чтобы каждое сообщение помещалось в лимит Telegram (4096 символов).
INSTRUCTION_PARTS = [
    (
        "Здравствуйте!\n\n"
        "Это мини-приложение группы <b>26-03 БД</b> — все дела группы теперь в одном месте, "
        "прямо в Telegram.\n\n"
        "Пользоваться приложением полностью <b>добровольно</b>. Это не обязательное требование "
        "и не обязанность — просто так удобнее: не нужно ничего искать в чатах и пересылать "
        "старосте в личку. Если вам это не нужно, вы ничего не теряете: все важные объявления "
        "по-прежнему будут дублироваться в чате группы.\n\n"
        "<b>Что здесь есть:</b>\n\n"
        "📄 <b>СПРАВКИ</b>\n"
        "Если вы болели или не пришли на занятия по уважительной причине и у вас есть справка — "
        "отправьте её сюда, а не в личку. Староста сразу увидит её в админке и получит уведомление, "
        "что пришла новая справка. Отправить можно прямо с телефона: сначала указываете период "
        "отсутствия, потом прикрепляете фото справки и при желании пишете комментарий. "
        "Удалить отправленную справку можно, пока староста её не прочитал. После прочтения "
        "справка остаётся в приложении — так она не потеряется."
    ),
    (
        "📊 <b>ПОСЕЩАЕМОСТЬ</b>\n"
        "Здесь видны ваши пропуски: общее количество, разбивка по предметам и за текущую неделю. "
        "Ничего указывать вручную не нужно — данные загружает староста, а вы просто открываете "
        "и смотрите. Если цифр ещё нет, будет написано «Данные о посещаемости пока не загружены».\n\n"
        "📓 <b>ЭЛЕКТРОННЫЙ ДНЕВНИК</b>\n"
        "Домашние задания по дням недели: что задали на каждый день и по каким предметам. "
        "Это не оценки — только ДЗ, чтобы ничего не потерялось. Опубликованные задания могут "
        "отредактировать только назначенные ответственные по предмету, а староста может убрать "
        "задание, если оно ошибочное.\n\n"
        "<b>КАК ВОЙТИ</b>\n"
        "При первом запуске приложение попросит код. Код вам выдаёт староста — у каждого свой. "
        "Вводите его в разделе <b>Профиль</b> (шестерёнка в правом верхнем углу) → "
        "«Войти по коду». Всё, вводите один раз — дальше приложение запомнит это устройство "
        "и будет открываться сразу. Если сменили телефон, попросите старосту отвязать аккаунт, "
        "и код снова заработает.\n\n"
        "Свой код храните при себе: это ваш вход, никому его не передавайте."
    ),
    (
        "\nИ ещё: приложение будет развиваться — со временем здесь появятся новые функции. "
        "Обо всех обновлениях и нововведениях я буду сообщать прямо в этом чате с ботом. "
        "Вся важная информация будет дублироваться и в чате группы, и здесь, в сообщениях "
        "бота — чтобы точно ничего не пропустить. А ещё я буду предлагать вам самим "
        "поучаствовать: буду присылать опросы о том, какие новые функции вам нужны и что стоит "
        "добавить в первую очередь. Так что заглядывайте в бота иногда — там будут новости.\n\n"
        "Со всеми вопросами по приложению — к старосте."
    ),
]


def site_button(chat_type: str | None) -> InlineKeyboardButton:
    """Кнопка приложения: в личке открывает Mini App, в группе — обычную ссылку.

    Mini App (web_app) в обычных группах Telegram не поддерживает — там кнопка
    с url, иначе мини-приложение просто не откроется.
    """
    # Sentinel из Telegram, когда chat.type недоступен.
    if chat_type is None or chat_type in (ChatType.PRIVATE, "sender"):
        return InlineKeyboardButton(text="🌐 Открыть сайт", web_app=WebAppInfo(url=SITE_URL))
    return InlineKeyboardButton(text="🌐 Открыть сайт", url=SITE_URL)


def menu_keyboard(chat_type: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction")],
            [site_button(chat_type)],
        ]
    )


def instruction_keyboard(chat_type: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [site_button(chat_type)],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="menu")],
        ]
    )


dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=menu_keyboard(message.chat.type))


@dp.callback_query(F.data == "instruction")
async def show_instruction(callback: CallbackQuery) -> None:
    await callback.answer()

    if callback.message is None:
        return

    # Инструкция отправляется новыми сообщениями, чтобы текст не терялся при нажатии «Назад».
    for part in INSTRUCTION_PARTS:
        await callback.message.answer(part)

    await callback.message.answer(
        "Готово — это вся инструкция. Если что-то останется непонятным, обращайтесь к старосте.",
        reply_markup=instruction_keyboard(callback.message.chat.type),
    )


@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery) -> None:
    await callback.answer()

    if callback.message is None:
        return

    # Меню приходит новым сообщением, чтобы у него была активная кнопка «Открыть сайт»
    # и чтобы не менять уже прочитанные части инструкции.
    await callback.message.answer(
        WELCOME_TEXT, reply_markup=menu_keyboard(callback.message.chat.type)
    )


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    token = (
        os.getenv("BOT_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
        or os.getenv("TELEGRAM_TOKEN")
        or BOT_TOKEN
    )
    if not token:
        raise SystemExit(
            "Не задан токен бота. Добавьте переменную окружения BOT_TOKEN "
            "(Railway: Variables → BOT_TOKEN)."
        )

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Бот запущен в режиме Long Polling")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit) as exc:
        if isinstance(exc, SystemExit) and exc.code not in (None, 0):
            raise
        logging.info("Бот остановлен")
