import praw, re, random, os, traceback, time

# Log that the programme is starting, then initialize praw and login to Reddit
# After trying logging in, the programme logs if it was successful or not
print "Starting"
r = praw.Reddit("A bot to send butt tips to users by /u/Natatos")
r.login(os.environ["USERNAME"], os.environ["PASSWORD"])
if r.is_logged_in():
  print "Logged in", os.environ["USERNAME"]
else:
  print "Problem logging in"
  exit()


# Loads each line from the replies file into a list
# Then randomly chooses one and returns it as a string
def choose_reply():
  with open("replies.txt") as f:
    replies = f.readlines()
  return random.choice(replies)


# Inputs a comment object
# A dictionary of values is created with to being the last word of the comment,
# which should be /u/User or u/User, but no checks/preventions force that.
# Amount is the first word of the comment and will be the +X value.
# The comment string is then constructed and returned
# TODO: Need better input handling for getting values
def build_reply(comment):
  values = {
    "to": comment.body.split()[-1],
    "amount": comment.body.split()[0]
  }
  return "Sending {0} ButtTips to {1}\n\n{2}".format(values["amount"], values["to"], choose_reply())


# Inputs a comment object
# done is set to false, then a loop goes over the replies to the comment
# If the the reply author name is the same as the bot username,
# then done is set to true and the loop ends. The true/false value of done is returned
#
# I worry that this method is too resource intensive, and it might be better to use a DB
# If it is, and by much, someone can tell me and I'll change it
# However, there's only at most 1000 comments (unless it's multi, then it's 1000*numSubs)
def have_replied(comment):
  done = False
  for reply in comment.replies:
    if reply.author.name == os.environ["USERNAME"]:
      done = True
      break
  return done


# In an infinite loop is created so that errors don't stop the program,
# and so keyboard interruption ends the infinite for loop better.
# The for loop goes over each comment as they come
# An if statement does a regex check between the comment body and tip cue
# If a tip is made then an if statement checks it's been replied to or not
# This is needed because if an error happens (i.e. commenting too much), then
# it starts the whole loop over, and will fixate on one comment if they're not coming
# in fast enough. Also it's nice to not reply to the same comment accidentally.
# Then the comment is built the reply is made.
#
# In the first exception, traceback is printed to show the error (commented out in prod,
# because it's going to pretty much always be saying it's posting too much)
# Then the program sleeps for a minute, again because it'll just be posting too much
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
