
import json
import os
import re
from typing import Optional

import httpx
from constants import MEDIA_SAVE_PATH, TWEETS_SAVE_PATH
from objects.person import Person
from utilities.logger import LOGGER
from utils import Err, format_url_universal_binbows


class Tweet:
    TWEET_CACHE = []

    tweet_dict: dict
    sort_index: Optional[str]
    tweet_poster: Person
    all_images: list[str]
    all_gifs: list[str]
    all_videos: list[str]
    def __init__(self, tweet_dict: dict, sort_index: Optional[str]):
        self.sort_index = sort_index
        typename = tweet_dict["__typename"]
        if typename == "Tweet":
            self.tweet_poster = Person(tweet_dict['core']['user_results']['result'])
        # Example of visibility esults: https://x.com/Cr7Fran4ever/status/1910724957031575897
        elif typename == "TweetWithVisibilityResults":
            self.tweet_poster = Person(tweet_dict["tweet"]['core']['user_results']['result'])
            tweet_dict = tweet_dict["tweet"]
        

        self.all_images = []
        self.all_gifs = []
        self.all_videos = []

        # IMAGES
        media = tweet_dict["legacy"].get("entities")
        if media is not None:
            media = media.get("media", [])
        else:
            media = []
        
        extended_media = tweet_dict["legacy"].get("extended_entities")
        if extended_media is not None:
            extended_media = extended_media.get("media", [])
        else:
            extended_media = []
        
        for file in media + extended_media:
            filetype = file["type"]
            if filetype == 'photo':
                thumb = file['media_url_https']
                if thumb not in self.all_images:
                    self.all_images.append(thumb) 
              
            elif filetype == 'animated_gif':
                thumb = file['media_url_https']
                if thumb not in self.all_images:
                    self.all_images.append(thumb)
                variants = file['video_info']['variants']
                if len(variants) != 1:
                    LOGGER.warn(f"Weird variant count for gif ({len(variants)} instead of 1: {variants}) {file}", additional=[Err("Variants", variants), Err("All content", tweet_dict)])
                if len(variants) == 0:
                    continue
                gif_url = variants[0]['url']
                self.all_gifs.append(gif_url)

            elif filetype == 'video':
                thumb = file['media_url_https']
                if thumb not in self.all_images:
                    self.all_images.append(thumb)
                variants = file['video_info']['variants']
                mpeg_variants = 0
                qualities: list[tuple[int, int, str]] = []
                for variant in variants:
                    content_type = variant['content_type']
                    url = variant['url']
                    bitrate = variant.get('bitrate')
                    if content_type == "application/x-mpegURL":
                        mpeg_variants += 1
                        # self.all_videos.append(url)
                    elif content_type == "video/mp4":
                        pixel_count = 0
                        try:
                            match = re.search(r"\/(\d*)x(\d*)\/", url)
                            if match is None:
                                raise Exception("Couldn't find match.")
                            pixel_count = int(match.group(1)) * int(match.group(2))
                        except:
                            LOGGER.error(f"Couldn't get pixel count from url: {url}", additional=[Err("Variant", variant), Err("File", file), Err("Tweet dict", self.tweet_dict)])
                        
                        qualities.append((pixel_count, bitrate, url))
                    else:
                        LOGGER.warn(f"Unknown content type for media: {content_type}", additional=[Err("Variant", variant), Err("File", file), Err("Tweet dict", self.tweet_dict)])

                if len(qualities) == 0:
                    if mpeg_variants > 0:
                        LOGGER.error("Only (ungrabbed) MPEG variants founds on video.", additional=[Err("File", file), Err("Tweet dict", self.tweet_dict)])
                    else:
                        LOGGER.error("No quality found on video.", additional=[Err("File", file), Err("Tweet dict", self.tweet_dict)])
                    continue                    

                qualities.sort(key=lambda x: (x[0], x[1]), reverse=True)
                best_video = qualities[0]
                best_bitrate = best_video[1]
                for quality in qualities:
                    if quality[1] > best_bitrate:
                        best_bitrate = quality[1]
                
                if best_bitrate != best_video[1]:
                    LOGGER.warn(f"Best video resolution doesn't have the best bitrate ? Best {best_bitrate} vs choosen {best_video[1]}", additional=[Err("File", file), Err("Tweet dict", self.tweet_dict)])
                
                self.all_videos.append(best_video[2])

            else:
                LOGGER.error(f"Unknown filetype: {filetype}", additional=[Err("File", file), Err("Tweet dict", self.tweet_dict)])



        # Replace the user dict with just the id to save on space & keep users cached somewhere else.
        tweet_dict['core']['user_results']['result'] = tweet_dict['core']['user_results']['result']['rest_id']
        self.tweet_dict = tweet_dict

    def get_tweet_user(self):
        return self.tweet_poster
        
    def save_tweet_only_to_file(self):
        tweet_uid = self.tweet_dict["rest_id"]
        person_uid = self.tweet_poster.user_dict['rest_id']

        if tweet_uid in Tweet.TWEET_CACHE:
            # print("Already saved id: " + tweet_uid)
            return

        save_folder = f"{TWEETS_SAVE_PATH}{os.sep}"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        if not os.path.exists(f"{save_folder}.git"):
            # TODO: Handle when not found (also handle windows)
            os.system(f"cd {save_folder} && git init")

        
        with open(f"{save_folder}{person_uid}-{tweet_uid}.json", 'w') as f: #unique id
            json.dump({
                "sort_index": self.sort_index,
                "tweet_dict": self.tweet_dict
            }, f, indent=4)
        
        Tweet.TWEET_CACHE.append(tweet_uid)
    
    def save_all_media(self):
        for url in self.all_images + self.all_gifs + self.all_videos:
            cleaned = url.replace("https://", "").replace("http://", "")
            filename = format_url_universal_binbows(MEDIA_SAVE_PATH + os.sep + os.sep.join(cleaned.split("/")))
            foldername = format_url_universal_binbows(MEDIA_SAVE_PATH + os.sep + os.sep.join(cleaned.split("/")[:-1]))
            
            if (os.path.exists(filename)):
                # print("File exists: " + filename)
                continue

            print(f"Saving media: {filename}...", end="")

            if not os.path.exists(foldername):
                os.makedirs(foldername)
            
            image_content = httpx.get(url).content
            with open(filename, "wb") as f:
                f.write(image_content)
            
            print("Done !")