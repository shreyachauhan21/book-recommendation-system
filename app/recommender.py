from thefuzz import process
import pandas as pd

class GenreRecommender:
    def __init__(self, books_df):
        self.books = books_df
        self.books['genres'] = self.books['genres'].fillna('').str.lower()
        self.books['title_lower'] = self.books['title'].str.lower()
        self.titles = self.books['title_lower'].tolist()

    def get_closest_title(self, user_input):
        match, score = process.extractOne(user_input.lower(), self.titles)
        return match if score > 60 else None

    def recommend_by_genre(self, user_input, top_n=10):
        closest_title = self.get_closest_title(user_input)
        if not closest_title:
            return None, []

        selected_book = self.books[self.books['title_lower'] == closest_title].iloc[0]
        genre_keywords = selected_book['genres'].split(',')[:3]  # pick top 3 genres/tags

        # Find books sharing any of these top genres
        filtered_books = self.books[
            self.books['genres'].apply(lambda g: any(tag in g for tag in genre_keywords))
        ].drop_duplicates(subset='title')

        # Remove the input book
        filtered_books = filtered_books[filtered_books['title_lower'] != closest_title]

        return selected_book['title'], filtered_books.head(top_n)[['title', 'authors', 'average_rating', 'image_url']]
