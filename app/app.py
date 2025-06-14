# app.py
import streamlit as st
import pandas as pd
from recommender import GenreRecommender

books = pd.read_csv("data/merged_books.csv")  # after joining tags
recommender = GenreRecommender(books)

st.title("📚 Genre-Based Book Recommendation")

user_input = st.text_input("Enter a book title:")

if user_input:
    matched_title, results = recommender.recommend_by_genre(user_input)

    if results.empty:
        st.warning("Couldn't find similar books.")
    else:
        st.info(f"Recommendations based on: **{matched_title}**")
        for _, row in results.iterrows():
            st.image(row['image_url'], width=120)
            st.markdown(f"**{row['title']}** by *{row['authors']}*  \n⭐ {row['average_rating']}")
            st.markdown("---")
