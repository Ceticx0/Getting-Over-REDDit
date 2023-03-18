# Reddit Moment
## A completely automatic reddit video creator and uploader.
[Example output](https://www.youtube.com/@gettingoverREDDit)

This project uses the reddit api to get the top posts of x time frame on any subreddit and screenshot the comments on those posts using playwright. It then takes the text and generates a narration using google cloud tts.  The video will then be rendered with moviepy on top of background footage using screenshots of comments on the posts and their text read aloud. the video is saved to media/createdVideos and uploaded to youtube using the youtube api.

To use this create a file called reddit_creds.json is creds/ that follows this format

    {  
      "username": "",  
      "password": "",  
      "app_client_id": "",  
      "app_secret_token": ""  
    }
you also need a client_secret.json that you can download from the google cloud console for the youtube api, and a file named tts_key.json that you can download from the cloud console for the tts api.

To change the subreddit, best of time, or number of videos to upload change options.json
**command line args will be added eventually**