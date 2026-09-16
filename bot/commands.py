from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

PUBLIC_COMMANDS = [
    BotCommand(command="start", description="Как предложить тему"),
    BotCommand(command="version", description="Версия бота"),
    BotCommand(command="whoami", description="Мой Telegram ID"),
]
SUMMARY_COMMAND = BotCommand(command="summary", description="Сводка всех предложений (автор)")


async def setup_commands(bot: Bot, author_id: int | None) -> None:
    """Register the "/" menu: public commands for everyone, plus /summary in the author's private chat."""
    await bot.set_my_commands(PUBLIC_COMMANDS, scope=BotCommandScopeDefault())
    if author_id is not None:
        author_commands = sorted([*PUBLIC_COMMANDS, SUMMARY_COMMAND], key=lambda c: c.command)
        await bot.set_my_commands(author_commands, scope=BotCommandScopeChat(chat_id=author_id))
