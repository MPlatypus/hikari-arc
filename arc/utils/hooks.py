import typing as t

import hikari

from arc.abc.hookable import HookResult
from arc.context import Context
from arc.errors import (
    BotMissingPermissionsError,
    DMOnlyError,
    GuildOnlyError,
    InvokerMissingPermissionsError,
    NotOwnerError,
)


def guild_only(ctx: Context[t.Any]) -> HookResult:
    """A pre-execution hook that aborts the execution of a command if it is invoked outside of a guild."""
    if ctx.guild_id is None:
        raise GuildOnlyError("This command can only be used in a guild.")
    return HookResult()


def dm_only(ctx: Context[t.Any]) -> HookResult:
    """A pre-execution hook that aborts the execution of a command if it is invoked outside of a DM."""
    if ctx.guild_id is not None:
        raise DMOnlyError("This command can only be used in a DM.")
    return HookResult()


def owner_only(ctx: Context[t.Any]) -> HookResult:
    """A pre-execution hook that aborts the execution of a command if it is invoked by a non-owner."""
    if ctx.author.id not in ctx.client.owner_ids:
        raise NotOwnerError("This command can only be used by the application owners.")
    return HookResult()


def _has_permissions(ctx: Context[t.Any], perms: hikari.Permissions) -> HookResult:
    """Check if the invoker has the specified permissions."""
    if ctx.member is None:
        raise GuildOnlyError("This command can only be used in a guild.")

    missing_perms = ~ctx.member.permissions & perms

    if missing_perms is not hikari.Permissions.NONE:
        raise InvokerMissingPermissionsError(
            missing_perms, f"Invoker is missing '{missing_perms}' permissions to run this command."
        )

    return HookResult()


def has_permissions(perms: hikari.Permissions) -> t.Callable[[Context[t.Any]], HookResult]:
    """A pre-execution hook that aborts the execution of a command if the invoker is missing the specified permissions."""
    return lambda ctx: _has_permissions(ctx, perms)


def _bot_has_permissions(ctx: Context[t.Any], perms: hikari.Permissions) -> HookResult:
    """Check if the bot has the specified permissions."""
    if ctx.app_permissions is None:
        raise GuildOnlyError("This command can only be used in a guild.")

    missing_perms = ~ctx.app_permissions & perms

    if missing_perms is not hikari.Permissions.NONE:
        raise BotMissingPermissionsError(
            missing_perms, f"Bot is missing '{missing_perms}' permissions to run this command."
        )

    return HookResult()


def bot_has_permissions(perms: hikari.Permissions) -> t.Callable[[Context[t.Any]], HookResult]:
    """A pre-execution hook that aborts the execution of a command if the bot is missing the specified permissions."""
    return lambda ctx: _bot_has_permissions(ctx, perms)
