import praw, re, random, os, traceback, time

print "Starting"
r = praw.Reddit("A bot to send butt tips to users by /u/Natatos")
r.login(os.environ["USERNAME"], os.environ["PASSWORD"])
if r.is_logged_in():
  print "Logged in", os.environ["USERNAME"]
else:
  print "Problem logging in"
  exit()

def choose_reply():
  with open("replies.txt") as f:
    replies = f.readlines()
  return random.choice(replies)

def build_reply(comment):
  values = {
    "to": comment.body.split()[-1],
    "amount": comment.body.split()[0]
  }
  return "Sending {0} ButtTips to {1}\n\n{2}".format(values["amount"], values["to"], choose_reply())

def have_replied(comment):
  done = False
  # I worry that this method is too resource intensive, and it might be better to use a DB
  # If it is, and by much, someone can tell me and I'll change it
  # However, there's only at most 1000 comments (unless it's multi, then it's 1000*numSubs)
  for reply in comment.replies:
    if reply.author.name == os.environ["USERNAME"]:
      done = True
      break
  return done

while True:
  try:
    for comment in praw.helpers.comment_stream(r, "enoughlibrarianspam", limit=None, verbosity=0):
      if re.search("\+[.0-9]* (ButtTip to [/u])", comment.body, re.IGNORECASE):
        if not have_replied(comment):
          print "Trying", comment.permalink
          comment.reply(build_reply(comment))
  except Exception as e:
    traceback.print_exc()
    time.sleep(60)
    continue
  except KeyboardInterrupt:
    r.clear_authentication()
    print "Logged Out & Ending"
    break
