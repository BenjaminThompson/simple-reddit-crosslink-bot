import sqlite3
import reddit
import re
import calendar, time

db = sqlite3.connect("data.db")
c = db.cursor()

comment = """Hi, this post was crosslinked in [{0}]({1})."""

r = reddit.Client("https://ssl.reddit.com", "Example Crosslinker bot by /u/YourNameHere", testmode=False)
r.login("YourNameHere", "PASSWORD_HERE")


for sub in ["ExampleSubreddit1", "ExampleSubreddit2", "ExampleSubreddit3"]: #List here the subreddits you're going to check for crosslinks
    posts = r.fetch_sub_pages(sub, pages=2)

    for post in posts:
        kind = post['kind']
        id = post['data']['id']
        permalink = post['data']['permalink']
        url = post['data']['url']
        links = re.findall(r"http://[\w]+\.reddit\.com/r/MyTargetSubreddit[\w/]+", post['data']['selftext']) #Replace MyTargetSubreddit with the subreddit you want to notice crosslinks to
        links.append(url)

        for link in links:
            if "/r/MyTargetSubreddit" in link: #Replace MyTargetSubreddit with the subreddit you want to notice crosslinks to
                try:
                    targetpost_type, targetpost_id, created_utc = r.id_post_by_url(link+".json")
                    if calendar.timegm(time.localtime()) - created_utc > (60*60*24*7):
                        continue

                    c.execute("SELECT count(*) FROM posts WHERE type = '{0}' AND id = '{1}' AND alerted = 1".format(kind, id))
                    link_row = c.fetchone()
                    c.execute("SELECT count(*) FROM posts WHERE type = '{0}' AND id = '{1}' AND commented = 1".format(targetpost_type,
                                                                                                                      targetpost_id))
                    acpost_row = c.fetchone()

                    if link_row[0] == 0 or acpost_row[0] == 0:
                        c.execute("INSERT INTO posts (type, id, commented, alerted) VALUES ('{0}', '{1}', 0, 0)".format(kind, id))
                        c.execute("INSERT INTO posts (type, id, commented, alerted) VALUES ('{0}', '{1}', 0, 0)".format(targetpost_type,
                                                                                                                        targetpost_id))
                        db.commit()
                        comment_to_post = comment.format(sub, permalink)
                        r.post_comment(parent=targetpost_type+"_"+targetpost_id,
                                       text=comment_to_post)
                    c.execute("UPDATE posts SET alerted = 1 WHERE type = '{0}' AND id = '{1}'".format(kind, id))
                    c.execute("UPDATE posts SET commented = 1 WHERE type = '{0}' AND id = '{1}'".format(targetpost_type,
                                                                                                        targetpost_id))
                    db.commit()
                except Exception as exc:
                    print("Failed to crosslink \t {0} \t from : \t {1}".format(link,permalink))
