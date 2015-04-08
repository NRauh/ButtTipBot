import logging
import praw
import re
import random
import os
import traceback
import time

# HTTP errors (when reddit inevitably fails) and connection errors
from requests.exceptions import ConnectionError, HTTPError
# PRAW exceptions
from praw.errors import APIException, ClientException, RateLimitExceeded


SUBREDDIT = "buttcoin+enoughlibertarianspam"
REPLIES = []
VIDEOS = []
COMMENT = "Sending {0} Butts to /u/{1}\n\n{2}[What is Buttcoin?]({3}) | /r/Buttcoin"
DEBUG = os.environ.get("DEBUG", "false") == "true"

USER_AGENT = "ButtTipBot v0.3 by /u/Natatos"

loglvl = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(level=loglvl,
                    format='[%(asctime)s] [%(levelname)s] %(message)s')

log = logging.getLogger("butttipper")
logging.getLogger("requests").setLevel(loglvl)

# Create reddit object. Wait until initalization of ButtTipper to login
r = praw.Reddit(USER_AGENT)

# Change the amount randomly by a few orders of magnitude
def get_amount(original):
    oamt = float(original)
    i = 0
    magnitude = random.randint(0, 3)
    multiply = bool(random.getrandbits(1))
    while i < magnitude:
        if multiply:
            oamt *= 10.0
        else:
            oamt /= 10.0
        i += 1
    return oamt

# Load up a list of possible replies, and video links
def load_reply_data():
    global REPLIES
    global VIDEOS
    f = open("replies.txt", "r")
    REPLIES = f.readlines()
    f.close()
    f = open("videos.txt", "r")
    VIDEOS = f.readlines()
    f.close()

RECOVERABLE = (ConnectionError, HTTPError, APIException, ClientException, RateLimitExceeded)


class ButtTipper:
    def __init__(self, username, password, limit=2000):
        self.username = username
        self.password = password
        self.limit = limit
        self._setup = False
        self.already_done = []

    def run(self):
        if not self._setup:
            raise Exception("ButtTipper Bot has not been setup yet")

        log.info("Checking comments...")
        comments = praw.helpers.comment_stream(r, SUBREDDIT, limit=self.limit)
        for c in comments:
            cue = re.search(
                "(\+[.0-9]*) (ButtTip|butt|buttcoin)s? ?(to|for)? [/u]+[u/]([A-Z0-9_\-]*)",
                c.body, re.IGNORECASE)
            if cue and self.will_reply(c):
                c.reply(COMMENT.format(get_amount(cue.group(1)), cue.group(4),
                        random.choice(REPLIES), random.choice(VIDEOS)))

    def will_reply(self, comment):
        if comment.id in self.already_done:
            return False
        if comment.author and comment.author.name == self.username:
            self.already_done.append(comment.id)
        elif comment.replies:
            for reply in comment.replies:
                if reply.author and reply.author.name == self.username:
                    self.already_done.append(comment.id)
                else:
                    return True
        return False


    def setup(self):
        self._login()
        self._setup = True

    def quit(self):
        r.clear_authentication()
        self._setup = False
        log.info("Forever hold your butts; shutting down.")

    def _login(self):
        r.login(self.username, self.password)
        if not r.is_logged_in():
            raise Exception("Not logged in; authentication error?")
        log.info("Logged in to reddit")


if __name__ == "__main__":
    load_reply_data()

    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")
    wait = int(os.environ.get("WAIT", 20))
    limit = int(os.environ.get("LIMIT", 2000))

    bot = ButtTipper(username, password, limit)
    bot.setup()

    try:
        while True:
            try:
                bot.run()
            except RECOVERABLE as e:
                log.error(traceback.format_exc())
            time.sleep(wait)
    except KeyboardInterrupt:
        bot.quit()
