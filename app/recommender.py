# recommender.py

from thefuzz import process
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class GenreRecommender:
    def __init__(self, books_df):
        self.books = books_df.copy()
        self.books['genres'] = self.books['genres'].fillna('').str.lower()
        self.books['title_lower'] = self.books['title'].str.lower()
        self.titles = self.books['title_lower'].tolist()

        self.vectorizer = TfidfVectorizer()
        self.genre_matrix = self.vectorizer.fit_transform(self.books['genres'])

    def get_closest_title(self, user_input):
        match, score = process.extractOne(user_input.lower(), self.titles)
        return match if score > 60 else None

    def recommend_by_genre(self, user_input, top_n=10):
        closest_title = self.get_closest_title(user_input)
        if not closest_title:
            return None, pd.DataFrame()

        idx = self.books[self.books['title_lower'] == closest_title].index[0]

        cosine_similarities = linear_kernel(self.genre_matrix[idx:idx+1], self.genre_matrix).flatten()

        related_indices = cosine_similarities.argsort()[::-1][1:top_n+1]
        recommended_books = self.books.iloc[related_indices]

        return self.books.iloc[idx]['title'], recommended_books[['title', 'authors', 'average_rating', 'image_url']]
