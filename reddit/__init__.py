import requests
import json
import time
import logging


class Client:
    def __init__(self, baseurl = "", user_agent = "", modhash = "", testmode=False):
        """



        """
        self.testmode = testmode
        self.baseurl = baseurl
        self.user_agent = user_agent
        self.modhash = modhash
        self.headers = {'user-agent': user_agent}
        self.session = ""
        if len(modhash) > 0:
            self.headers['X-Modhash'] = modhash

        if len(baseurl) == 0 or len(user_agent) == 0:
            raise Exception("Insufficient Parameters. Specify both baseurl and user_agent.")

    def login(self, username, password):
        if len(self.modhash) == 0:
            self.session = requests.session()
            self.session.headers = self.headers
            try:
                self.session.headers = self.headers
                data = self.session.post("{0}/api/login".format(self.baseurl), data={'user': username,
                                                                             'passwd': password,
                                                                             'api_type': 'json',
                                                                             'rem': True})
                j = json.loads(data.content.decode())
                self.headers['X-Modhash'] = j['json']['data']['modhash']

            except Exception as exc:
                raise Exception("Login Failed.\n" + str(exc))
        else:
            return

    def fetch_sub_pages(self, sub="", after="", pages=1):
        if len(sub) == 0:
            raise Exception("No Subreddit specified.")
        posts = []
        for x in range(pages):
            with self.session as client:
                client.headers = self.headers
                data = client.get("{0}/r/{1}/.json?after={2}".format(self.baseurl, sub, after))
                doc = json.loads(data.content.decode())
                after = doc['data']['after']
                for post in doc['data']['children']:
                    try:
                        if post not in posts:
                            posts.append(post)
                    except:
                        pass
                time.sleep(2)
        return posts

    def post_comment(self, parent, text):
        if self.testmode == True:
            print(parent + "\t" + text)
        else:
            with self.session as client:
                client.headers = self.headers
                data = client.post("{0}/api/comment".format(self.baseurl), data = {'user': 'MyUserName', #Oops, hard coded username here. Should fix
                                                                                   'api_type': 'json',
                                                                                   'text': text,
                                                                                   'thing_id': parent})
                print(data.content.decode())
            time.sleep(10)

    def id_post_by_url(self, url):
        with self.session as client:
            client.headers = self.headers
            data = client.get(url)
            doc = json.loads(data.content.decode())
            return (doc[0]['data']['children'][0]['kind'],
                    doc[0]['data']['children'][0]['data']['id'],
                    doc[0]['data']['children'][0]['data']['created_utc'])