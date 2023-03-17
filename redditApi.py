import requests
import json
import shelve
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Post:
    post_id: str
    post_title: str
    post_url: str
    img_url: str
    nsfw_img: bool = False
    nsfw_tag: bool = False


def oauth():
    with open("creds/reddit_creds.json", 'r') as creds_file:
        json_loaded = json.load(creds_file)
        username = json_loaded['username']
        password = json_loaded['password']
        app_client_id = json_loaded['app_client_id']
        app_secret_token = json_loaded['app_secret_token']

    # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
    auth = requests.auth.HTTPBasicAuth(app_client_id, app_secret_token)

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': username,
            'password': password}

    # set up our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'GavinsBot/0.0.1'}

    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    if res == 503:
        print("Reddit says their down right now, try again later, exiting...")
        exit(0)

    # convert response to JSON and pull access_token value
    token = res.json()['access_token']

    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {token}"}}
    return headers
    # while the token is valid (~2 hours) we just add headers=headers to our requests


# --- sending requests ---
def request(subreddit: str = "AskReddit", limit: str = "10", time: str = "week") -> list:
    headers_ = oauth()
    after = None
    posts = []
    while len(posts) < int(limit):
        params = {'limit': limit,  # number of posts
                  't': time,  # hour, day, week, month, year, all
                  'after': after}  # post to continue after
        response = requests.get('https://oauth.reddit.com/r/{}/top'.format(subreddit), headers=headers_, params=params)
        res = response.json()  # convert json to python

        for i in range(len(res['data']['children'])):
            data = res['data']['children'][i]['data']
            post_id = data['id']
            post_title = data['title']
            img_url = data['url']
            post_url = "https://reddit.com" + data['permalink']
            after = res['data']['after']

            # test for nsfw image or tag, tag is on stuff like AskReddit posts, while image is just actually nsfw
            # Won't work on nsfw subs because they don't have it marked in the response at all for some reason
            if data.get('preview'):
                if data['preview']['images']['variants'].get('nsfw'):
                    nsfw_img = True
                else:
                    nsfw_img = False
            else:
                nsfw_img = False
            if data['whitelist_status'] == "promo_adult_nsfw":
                nsfw_tag = True
            else:
                nsfw_tag = False

            current_post = Post(post_id, post_title, post_url, img_url, nsfw_img, nsfw_tag)
            # test if the post has been made into a video before
            with shelve.open("shelve/usedPosts.db") as db:
                if post_id in db.keys():
                    # print(f"skipped post: {post_title}")
                    continue  # don't add to list
                else:
                    db[post_id] = False  # true or false whether a video has been made with the post yet
            posts.append(current_post)
    return posts


if __name__ == '__main__':
    posts = request()
    for post in posts:
        print(f"url: {post.post_url}")
