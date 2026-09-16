from aiogram.methods import SetMyCommands
from aiogram.types import BotCommandScopeChat, BotCommandScopeDefault

from bot.commands import setup_commands


def _names(call: SetMyCommands) -> list[str]:
    return [c.command for c in call.commands]


async def test_everyone_sees_public_commands_without_summary(bot, session):
    await setup_commands(bot, author_id=None)
    [call] = session.calls(SetMyCommands)
    assert isinstance(call.scope, BotCommandScopeDefault)
    assert _names(call) == ["start", "version", "whoami"]
    assert all(c.description for c in call.commands)


async def test_author_chat_also_sees_summary(bot, session):
    await setup_commands(bot, author_id=777)
    calls = session.calls(SetMyCommands)
    assert len(calls) == 2
    [author_call] = [c for c in calls if isinstance(c.scope, BotCommandScopeChat)]
    assert author_call.scope.chat_id == 777
    assert _names(author_call) == ["start", "summary", "version", "whoami"]
