import hashlib
import json
import logging
import threading
import time
from typing import Optional
from discord_webhook import DiscordEmbed, DiscordWebhook
import httpx

from constants import BAD_REPORT_URL, GOOD_REPORT_URL, WARN_REPORT_URL, WASTEBIN_LOG_URL
from utilities.logger import LOGGER
from utils import Err

# WEBHOOK_TASKS: dict[str, list[DiscordWebhook]] = {}

# https://birdie0.github.io/discord-webhooks-guide/other/field_limits.html
# Assuming the title + footer are less than 1904 chars in size


class WebhookManager:
    webhook_queue: list[DiscordWebhook]
    should_stop: bool
    polling_rate: float

    def __init__(self, polling_rate: float = 0.5):
        self.webhook_queue = []
        self.should_stop = False
        self.polling_rate = polling_rate
        LOGGER.webhook_queue_func = self.queue_webhook

    def start(self):
        self.thread = threading.Thread(target=self.process_webhooks)
        self.thread.start()

    def queue_webhook(self, log_level: int, title: str, message: str, additional: Optional[list[Err]]= None, footer: Optional[str] = None):
        if log_level == logging.DEBUG:
            url = GOOD_REPORT_URL
            color = "3fbf00"
        if log_level == logging.INFO:
            url = GOOD_REPORT_URL
            color = "3fbf00"
        elif log_level == logging.WARN or log_level == logging.WARNING:
            url = WARN_REPORT_URL
            color = "ffd919"
        elif log_level == logging.ERROR:
            url = BAD_REPORT_URL
            color = "fc0303"
        else:
            url = BAD_REPORT_URL
            color = "fc0303"
            
        if not url:
            return
        
        if len(message) > 4096:
            LOGGER.error("TOO FUCKING BIG WEBHOOK MESSAGE!", send_webhook=False)
        
        hook = DiscordWebhook(url=url, rate_limit_retry=True)
        embed = DiscordEmbed(title=title, description=message, color=color)
        if footer:
            embed.set_footer(footer)
            embed.set_timestamp()
        
        hook.add_embed(embed)

        if additional and len(additional) > 0:
            LOGGER.info(f"Uploading {len(additional)} pastes for webhook.")
            for entry in additional:
                try:
                    upload = httpx.post(
                        url = WASTEBIN_LOG_URL, 
                        json={
                            "text": json.dumps(entry.content, indent=4),
                            "extension": entry.extension,
                            "title": title,
                            "expires": 4294967295 # Can't be 0 in the api so max u32
                        }
                    )
                    path = json.loads(upload.content.decode())["path"]
                except Exception as e:
                    LOGGER.error(f"Failed to upload text to wastebin: {e}", send_webhook=False)
                    path = f"COULD NOT UPLOAD: {e}"
                
                embed.add_embed_field(name=entry.name, value=f"[{path[1:]}]({WASTEBIN_LOG_URL + path})")

            LOGGER.info(f"Done uploading pastes for webhook.")


        self.webhook_queue.append(hook)

        return

        
    def process_webhooks(self):
        # Note: ONLY sleep if havent done anything this time.
        while True:
            if len(self.webhook_queue) > 0:
                LOGGER.info(f"Processing webhook (remaining: {len(self.webhook_queue)})")
                hook = self.webhook_queue.pop(0) 
                hook.execute()
            else:
                if self.should_stop:
                    LOGGER.info("Stopping webhook manager thread.")
                    return
                time.sleep(self.polling_rate)

            

    def terminate_gracefully(self):
        self.should_stop = True

WEBHOOK_MANAGER = WebhookManager(polling_rate=0.5)
