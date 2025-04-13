import json
from constants import ALREADY_KNOWN_BOOKMARK_SORT_INDEXES, ALREADY_KNOWN_BOOKMARKS, TWEETS_SAVE_PATH, USER_ID
from objects.tweet import Tweet
from request.bookmarks_request import BookmarkRequest

# Flaw: Doesn't save deletions.
# Fix: since we already stop when we hit a known id, just 
# remove tweets in the oringial json if they aren't here anymore
# Except i like backing up shit :D

class BookmarkSaver:
    user_id: str

    action_id = "ztCdjqsvvdL0dE8R5ME0hQ"
    action_name = "Bookmarks"

    # action_title: str

    previous_tweets: list[str]

    grabbed_tweets: list[Tweet]

    def __init__(self, user_id: str):
        self.user_id = user_id
        # self.action_title = action_name.lower()

        self.grabbed_tweets = []
    
    def _perform_iteration(self, cursor: str | None = None):
        print("Performing iteration.")
        req = BookmarkRequest(
            user_id=USER_ID,
            cursor=cursor
        )

        req.do_all()

        self.grabbed_tweets += req.tweets
        # print(json.dumps(req.tweets[0].tweet_dict))
        # print(f"Found {len(req.tweets)} tweets (next: {req.next_cursor}, @{req.tweets[0].tweet_poster.user_dict["rest_id"]}, {req.tweets[0].tweet_dict["legacy"]["full_text"]})")
        return req.found_known_tweet, req.next_cursor

    def grab_all_for_action(self):
        # Stop when the next request is empty.
        # TODO: Handle fails.
        grabbed_user_count = 0 
        found_known_tweet, next_cursor = self._perform_iteration()
        while len(self.grabbed_tweets) != grabbed_user_count and not found_known_tweet:
            grabbed_user_count = len(self.grabbed_tweets)
            found_known_tweet, next_cursor = self._perform_iteration(next_cursor)

        if found_known_tweet:
            print("Stopped prematurely.")

        print(f"Found {len(self.grabbed_tweets)} bookmarks")



    def just_save_grabbed_and_prev_no_git(self):
        for tweet in self.grabbed_tweets:
            tweet.save_tweet_only_to_file()
            tweet.tweet_poster.save_to_file()
            tweet.save_all_media()
        
        new_bookmarks = [{
            "author_id": x.tweet_poster.user_dict['rest_id'],
            "author_screen_name": x.tweet_poster.user_dict['legacy']['screen_name'],
            "tweet_id": x.tweet_dict['rest_id'],
            "sort_index": x.sort_index
        } for x in self.grabbed_tweets if x.sort_index not in ALREADY_KNOWN_BOOKMARK_SORT_INDEXES]
        
        print(f"New bookmark count: {len(new_bookmarks)}")

        bookmarks = new_bookmarks + ALREADY_KNOWN_BOOKMARKS
        print(f"Total bookmark count: {len(bookmarks)}")

        with open(f"{TWEETS_SAVE_PATH}/bookmarks.json", 'w') as f:
            json.dump(bookmarks, f, indent=4)