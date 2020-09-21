import instaloader
from flask import Flask, render_template, request, jsonify
from instaloader import Profile, Post
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np


app = Flask(__name__)
loader = instaloader.Instaloader()


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

def getSentiments(captions):
    if len(captions) > 0 and type(captions) == list:
        analyser = SentimentIntensityAnalyzer()
        neutral = []
        positive = []
        negative = []
        compound = []

        for caption in captions:
            neutral.append(analyser.polarity_scores(caption)['neu'])
            positive.append(analyser.polarity_scores(caption)['pos'])
            negative.append(analyser.polarity_scores(caption)['neg'])
            compound.append(analyser.polarity_scores(caption)['compound'])

        positive = np.array(positive)
        negative = np.array(negative)
        neutral = np.array(neutral)
        compound = np.array(compound)

        return {
            'Neutral':round(neutral.mean(),2)*100.0,
            'Positive':round(positive.mean(),2)*100.0,
            'Negative':round(negative.mean(), 2) * 100.0,
            'Compound':round(compound.mean(), 2) * 100.0
                }
    else:
        return '{"Negative":0.0,"Neutral":0.0,"Overall":0.0,"Positive":0.0}'

@app.route('/checkPrivacy/', methods=['GET'])
def checkAccountPrivacy():
    username = request.args['username']
    profile = Profile.from_username(loader.context, username)
    privacy = str(profile.is_private)
    return privacy



@app.route('/basicProfile/', methods=['GET'])
def getBasicPublicProfile():
    username = request.args['username']
    profile = Profile.from_username(loader.context, username)

    profileInformation = []
    profileInformation.append(profile.full_name)
    profileInformation.append(profile.get_profile_pic_url())


    information = {
        "name": profile.full_name,
        "profilePicture": profile.get_profile_pic_url(),
        "bio": profile.biography,
        "followers": profile.followers,
        "following": profile.followees,
    }

    return jsonify(information)

@app.route('/deepProfile/', methods=['GET'])
def getDeepPublicProfile():
    username = request.args['username']
    profile = Profile.from_username(loader.context, username)

    profileInformation = []
    profileInformation.append(profile.full_name)
    profileInformation.append(profile.get_profile_pic_url())

    postsWithHashtags = 0
    likesTotal = 0
    videoPosts = 0

    captions = []
    for post in profile.get_posts():
        if post.caption != None:
            captions.append(post.caption)
        if post.caption_hashtags != None:
            postsWithHashtags = postsWithHashtags + 1
        if post.likes != None:
            likesTotal = likesTotal + post.likes
        if post.is_video:
            videoPosts = videoPosts + 1

    information = {
        "name": profile.full_name,
        "profilePicture": profile.get_profile_pic_url(),
        "bio": profile.biography,
        "followers": profile.followers,
        "following": profile.followees,
        "totalProfileLikes": likesTotal,
        "totalVideoPosts": videoPosts,
        "postsWithHashtags": postsWithHashtags,
        "captionSentiments": getSentiments(captions),
    }

    return jsonify(information)




