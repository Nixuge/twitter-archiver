
import asyncio
from types import CoroutineType
from typing import Any, Optional
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from httpx import Response

from constants import BAD_REPORT_URL, GOOD_REPORT_URL

WEBHOOK_TASKS: list[CoroutineType[Any, Any, Response]] = []


def queue_webhook(good: bool, title: str, message: str, additional: Optional[str] = None, footer: Optional[str] = None):
    if good: url = GOOD_REPORT_URL
    else: url = BAD_REPORT_URL
    
    if not url:
        return

    hook = AsyncDiscordWebhook(url=url, rate_limit_retry=True)

    if good: color = "3fbf00"
    else: color = "fc0303"

    embed = DiscordEmbed(title=title, description=message, color=color)
    if additional:
        embed.add_embed_field(name="Data", value=additional)
    if footer:
        embed.set_footer(footer)
        embed.set_timestamp()
    
    hook.add_embed(embed)

    WEBHOOK_TASKS.append(hook.execute())

async def cleanup():
    for task in WEBHOOK_TASKS:
        await task
