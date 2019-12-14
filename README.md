# Export Pinboard Pins for The Briefly
Creates a text file with links from Pinboard for use on thebriefly.com

I was previously using IFTTT for some of this functionality. I save links to Pinboard.in, tagged with 'nyc' throughout the day. IFTTT would take those pins and put the text and URL that was saved into a spreadsheet in Google Sheets. Then I would format the text, do some quick transformations in a text editor and put that into a WordPress post. This saves a few of those steps.

This skips a step and formats the text and outputs a txt file for me to copy and paste from.

```import pinboard
import datetime
import feedparser
import requests
from datetime import datetime
import re
```

First we grab the WordPress tags. This isn't a perfect method, but there are under 2,000 tags so this loop will work for now. The tags are poorly formatted (that's my fault), so it's formatted a little.

```
tags = []

for i in range(20):
    resp = requests.get('https://thebriefly.com/wp-json/wp/v2/tags?page=' + str(i + 1) + '&per_page=100')
    for k in range(len(resp.json())):
        tags.append(resp.json()[k]['name'].lower())
```

Grab the weather. Using the Dark Sky API to grab the day's high and low temperatures and the summary of the day's weather. There's a little bit of work if the day the script is run is a Friday so we can grab the weekend's high and low temperatures.
        
```        
API_KEY = 'API_KEY'

lat, long = '40.683', '-73.9708'

resp = requests.get('https://api.darksky.net/forecast/' + API_KEY + '/' + lat + ',' + long)

low = str(round(resp.json()['daily']['data'][0]['temperatureLow']))
high = str(round(resp.json()['daily']['data'][0]['temperatureHigh']))

if datetime.fromtimestamp(resp.json()['daily']['data'][0]['time']).strftime("%A") == 'Friday':
    w_low = str(round(min(resp.json()['daily']['data'][1]['temperatureLow'], resp.json()['daily']['data'][2]['temperatureLow'])))
    w_high = str(round(max(resp.json()['daily']['data'][1]['temperatureHigh'], resp.json()['daily']['data'][2]['temperatureHigh'])))
    condition = str(resp.json()['daily']['data'][0]['summary'])
        
    weather = '<p style="text-align: center;">Today -&nbsp;Low: ' + low +  '˚ High: ' + high + '˚<br />' + condition + '<br/>This weekend -&nbsp;Low: ' + w_low +  '˚ High: ' + w_high + '˚</p>'
    
else:
    weather = '<p style="text-align: center;">Today -&nbsp;Low: ' + low +  '˚ High: ' + high + '˚<br />' + condition + '</p>'
```

I publish The Briefly every morning at different times. This looks at the RSS feed and grabs the time of the most recently published article on thebriefly.com and stores the time as pubb.

```
pb = pinboard.Pinboard('LOGIN:API_KEY')

rss = feedparser.parse('http://thebriefly.com/feed/')
date_time_str = rss['entries'][1]['published'][:-6]
pubb = datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S')
```
Retrieves the 50 most recent pins from my Pinboard account with the tag 'nyc' applied and reverses them to reverse chronological order.
```
listy = pb.posts.recent(count=50, tag='nyc')['posts']
listy.reverse()
```
 Adds the note from the pins (that's what .extend is) and the url to a list 
```
briefly = []
for i in range(len(listy)):
    if '?emc=rss&partner=rss' in listy[i].url:
        listy[i].url = listy[i].url.replace('?emc=rss&partner=rss', '')
    if listy[i].time > pubb:
        briefly.append(listy[i].extended + '\n' + listy[i].url)
```        
Looks for any tag in each pin and creates a list of the used tags. Before the comparison happens, punctuation is stripped and the pin is formatted for an easy comparison. I'm not totally thrilled with the way the comparison is done, but it's working in a basic form.
```
punctuations = '''•!()-[]{};:'"\,<>./?@#$%^&*_~'''
tag_list = []
no_tags = []
words_re = re.compile(" | ".join(tags))
for item in briefly:
    for x in item.lower(): 
        if x in punctuations: 
            item = item.replace(x.lower(), " ") 
    try:
        tag_list.append(words_re.search(item)[0])
    except:
        no_tags.append(item)
```        
Creates and writes file
```
open('the briefly.txt', 'w').close()

# writes to the text file and replaces the two usages of '•'
# to open and close a link.

with open('the briefly.txt', 'w') as f:
    f.write('Pins Saved: ' + str(len(briefly)) + '\n\n')
    f.write(weather)
    for item in briefly:
        if '•' in item:
            f.write(item.split('\n')[0].replace('•', '<a href="' + item.split('\n')[1] + '">', 1).replace('•', '</a>', 1) + '\n\n')
        else:
            f.write('<a href="' + item.split('\n')[1] + '">' + ' '.join(item.split('\n')[0].split('(')[:1]).strip() + '</a>' + ' ' + item.split('\n')[0][len(' '.join(item.split('\n')[0].split('(')[:1])):] + '\n\n')
    f.write('\n\n tags: ' + ','.join(tag_list))
    f.write('\n\n no tags: ' + str(no_tags))
```

## Where To Go From Here
The next step would be to use the WordPress API to save the text right to a WordPress draft post directly instead of a text file.
