import os
import shelve
import pickle
import re

import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload


# probably a safer way to do this
def ascii_sanitize(string):
    all_printable_characters = r"""!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{}~ """
    re_filter = "[^{}]".format(all_printable_characters)
    new_str = re.sub(re_filter, "", string)
    return new_str


def authenticate(secret_file):
    scopes = ["https://www.googleapis.com/auth/youtube",
              "https://www.googleapis.com/auth/youtube.force-ssl",
              ]
    credentials = None

    if os.path.exists("creds/token.pickle"):
        # load saved creds from file
        with open("creds/token.pickle", 'rb') as token:
            credentials = pickle.load(token)
    # if the credentials aren't valid or don't exist, use the refresh token or oauth to log in
    if not credentials or not credentials.valid:
        # if they're expired, use the refresh token
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # connects to secrets file for oauth authentication
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(secret_file,
                                                                                       scopes=scopes)
            flow.run_local_server(authorization_prompt_message="")  # port 8080 localhost
            credentials = flow.credentials
            with open("creds/token.pickle", 'wb') as token_file:
                pickle.dump(credentials, token_file)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube


def top_level_comment(video_id, comment_text, secret_file="creds/client_secret.json"):
    youtube = authenticate(secret_file)

    request_body = {
        'snippet': {
            'videoId': video_id,
            'topLevelComment': {
                'snippet': {
                    'textOriginal': comment_text,
                },
            },
        },
    }
    request = youtube.commentThreads().insert(
        # part=','.join(request_body.keys()),
        part='snippet',
        body=request_body,
    )
    response = request.execute()
    return response


def upload_video(video_file, title, description="", secret_file="creds/client_secret.json"):
    youtube = authenticate(secret_file)

    body = {
        "snippet": {
            "title": title,
            "description": description,

        },
        "status": {"privacyStatus": "public"},
    }

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
    )
    response = request.execute()
    return response


if __name__ == '__main__':
    # upload_video("media/createdVideos/You are given 1.mp4", "You are given 1 milion dollars but to accept it you must enter the last video game you played and stay for a year.If you accept it ,how's life there?")
    print(top_level_comment('GkZvwKB6B0E', "test comment 123 hello people"))
