import pinboard
import datetime
import feedparser

pb = pinboard.Pinboard('robblatt:69D400CDEC221845114F')

# I publish The Briefly every morning at different times.
# This looks at the RSS feed and grabs the time of the
# most recently published article on thebriefly.com and
# stores the time as pubb.

rss = feedparser.parse('http://thebriefly.com/feed/')
date_time_str = rss['entries'][0]['published'][:-6]
pubb = datetime.datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S')

# Retrieves the 50 most recent pins from my Pinboard account with the
# tag 'nyc' applied and reverses them to reverse chronological order.

listy = pb.posts.recent(count=50, tag='nyc')['posts']
listy.reverse()

# Adds the note from the pins (that's what .extend is) and the url to a list 

briefly = []
for i in range(len(listy)):
    if listy[i].time > pubb:
        briefly.append(listy[i].extended + '\n' + listy[i].url)
        
# creates a file

open('the briefly.txt', 'w').close()

# writes to the text file and replaces the two usages of '•'
# to open and close a link.

with open('the briefly.txt', 'w') as f:
    f.write('Pins Saved: ' + str(len(briefly)) + '\n\n')
    for item in briefly:
        f.write(item.split('\n')[0].replace('•', '<a href="' + item.split('\n')[1] + '">', 1).replace('•', '</a>', 1) + '\n\n')