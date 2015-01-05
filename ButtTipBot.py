import praw, re, random, os

r = praw.Reddit("A bot to send butt tips to users by /u/Natatos")
r.login(os.environ["USERNAME"], os.environ["PASSWORD"])
if not r.is_logged_in():
  print "Problem logging in"
  exit()

def choose_reply():
  with open("replies.txt") as f:
    replies = f.readlines()
  return random.choice(replies)

def send_reply(values):
  comment = "Sending {0} ButtTips to {1}\n{2}".format(values["amount"], values["to"], choose_reply())

def parse_comment(comment):
  values = {
    "amount": comment.split()[0],
    "to": comment.split()[-1]
  }
  send_reply(values)

for comment in praw.helpers.comment_stream(r, "buttcoin"):
  if re.search("\+[.0-9]* (buttip to [/u])", comment.body, re.IGNORECASE):
    parse_comment(comment.body)
