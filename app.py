from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/recommendations/', methods=['GET'])
def recommendations():
    movie = request.args['movie']
    df = pd.read_csv("movie_dataset.csv")

    def get_title_from_index(index):
        return df[df.index == index]["title"].values[0]

    def get_index_from_title(title):
        return df[df.title == title]["index"].values[0]

    features = ['keywords', 'cast', 'genres', 'director']

    for feature in features:
        df[feature] = df[feature].fillna('')

    def combine_features(row):
        try:
            return row['keywords'] + " " + row['cast'] + " " + row['genres'] + " " + row['director']
        except:
            return ("Error")

    df["combined_features"] = df.apply(combine_features, axis=1)

    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["combined_features"])

    cosine_sim = cosine_similarity(count_matrix)
    movie_user_likes = movie

    movie_index = get_index_from_title(movie_user_likes)
    similar_movies = list(enumerate(cosine_sim[movie_index]))

    sorted_similar_movies = sorted(similar_movies, key=lambda x: [1], reverse=True)

    recommendations_list = []

    i = 0
    for movie in sorted_similar_movies:
        recommendations_list.append(get_title_from_index(movie[0]))
        i = i + 1
        if i > 10:
            break

    return jsonify(recommendations_list)










