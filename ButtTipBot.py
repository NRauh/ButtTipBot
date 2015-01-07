import praw, re, random, os, traceback, time

# Log that the programme is starting, then initialize praw and login to Reddit
# After trying logging in, the programme logs if it was successful or not
print("Starting")
r = praw.Reddit("A bot to send butt tips to users by /u/Natatos")
r.login(os.environ["USERNAME"], os.environ["PASSWORD"])
if r.is_logged_in():
  print("Logged in", os.environ["USERNAME"])
else:
  print("Problem logging in")
  exit()


# Loads each line from the replies file into a list
# Then randomly chooses one and returns it as a string
def choose_reply():
  with open("replies.txt") as f:
    replies = f.readlines()
  return random.choice(replies)


# Inputs a comment object
# If the comment author name is the same as the username, it returns false (will not reply)
# If there are replies, a loop goes over them all, and if there is an author,
# and the author is the username, it returns false
# If there are no replies, or the replies weren't the username it returns true (will reply)
#
# I worry that this method is too resource intensive, and it might be better to use a DB
# If it is, and by much, someone can tell me and I'll change it
# However, there's only at most 1000 comments (unless it's multi, then it's 1000*numSubs)
def will_reply(comment):
  if comment.author.name == os.environ["USERNAME"]:
    return False
  if comment.replies:
    for reply in comment.replies:
      if reply.author and reply.author.name == os.environ["USERNAME"]:
        return False
  return True


# In an infinite loop is created so that errors don't stop the program,
# and so keyboard interruption ends the infinite for loop better.
# The for loop goes over each comment as they come
# The cue variable which does a regex check between the comment body and tip phrase
# If a tip is made then an if statement checks it's should be replied to
# Then the comment is built the reply is made from cue regex groups and choose_reply().
#
# In the first exception, traceback is printed to show the error (commented out in prod,
# because it's going to pretty much always be saying it's posting too much)
# Then the program sleeps for a minute, again because it'll just be posting too much
while True:
  try:
    for comment in praw.helpers.comment_stream(r, "enoughlibrarianspam", limit=None, verbosity=0):
      cue = re.search("(\+[.0-9]*) (ButtTip|butt|buttcoin)s? ?(to|for)? [/u]+[u/]([A-Z0-9_\-]*)", comment.body, re.IGNORECASE)
      if cue:
        if will_reply(comment):
          reply = "Sending {0} Butts to /u/{1}\n\n{2}\n\n[[What is Buttcoin?](https://www.youtube.com/watch?v=So50EUl8wbc)][/r/Buttcoin]".format(cue.group(1), cue.group(4), choose_reply())
          comment.reply(reply)
  except Exception as e:
    #traceback.print_exc()
    time.sleep(60)
    continue
  except KeyboardInterrupt:
    r.clear_authentication()
    print("Logged Out & Ending")
    break
