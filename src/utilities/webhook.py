import hashlib
import logging
import threading
import time
from typing import Optional
from discord_webhook import DiscordEmbed, DiscordWebhook

from constants import BAD_REPORT_URL, GOOD_REPORT_URL, WARN_REPORT_URL
from utilities.logger import LOGGER

# WEBHOOK_TASKS: dict[str, list[DiscordWebhook]] = {}

def split_string(input_string, chunk_size=4000):
    return [input_string[i:i + chunk_size] for i in range(0, len(input_string), chunk_size)]

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
        self.thread = threading.Thread(target=self.process_webhooks)
        self.thread.start()
        LOGGER.webhook_queue_func = self.queue_webhook


    def queue_webhook(self, log_level: int, title: str, message: str, additional: Optional[str] = None, footer: Optional[str] = None):
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
        
        queue = []

        if len(message + f"\n\nAdditional content:\n```\n{additional}\n```") <= 4096:
            queue.append(message + f"\n\nAdditional content:\n```\n{additional}\n```")
        else:
            w_id = hashlib.md5(message.encode('utf-8')).hexdigest()[:10]

            # Message part.
            message_splitted = split_string(message)
            for part in message_splitted:
                queue.append(part)

            # Additional part.
            # Note: Here we always put the rest on another message. Here we could use tha latest message's length, but meh.
            additional_splitted = split_string(f"\n\nAdditional content:\n```\n{additional}")
            for i, part in enumerate(additional_splitted):
                if i == 0:
                    part += "\n```"
                else:
                    part = f"```\n{part}\n```"
                queue.append(part)


            # Final.
            partc = len(queue)
            for i, part in enumerate(queue):
                hook = DiscordWebhook(url=url, rate_limit_retry=True)

                if partc == 1:
                    ctitle = title
                else:
                    ctitle = f"{title} ({w_id}, {i+1}/{partc})"
                embed = DiscordEmbed(title=ctitle, description=part, color=color)
                if footer and not "```" in part: #don't add header to additional content.
                    embed.set_footer(footer)
                    embed.set_timestamp()
                
                hook.add_embed(embed)
                # print("added hook")
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
