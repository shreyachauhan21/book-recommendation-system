import pandas as pd

# Load datasets
books = pd.read_csv("data/books.csv")
book_tags = pd.read_csv("data/book_tags.csv")
tags = pd.read_csv("data/tags.csv")

# Map tag_id to tag_name
tag_map = tags.set_index('tag_id')['tag_name']
book_tags['tag'] = book_tags['tag_id'].map(tag_map)

# Group by book and select top 5 tags (you can also filter out noisy tags here)
book_tags_grouped = (
    book_tags
    .groupby('goodreads_book_id')['tag']
    .apply(lambda x: ', '.join(x.head(5)))  # comma-separated top 5 tags
    .reset_index()
)

# Merge with books on the correct keys
books = books.merge(book_tags_grouped, left_on='book_id', right_on='goodreads_book_id', how='left')

# Rename and clean up
books = books.rename(columns={"tag": "genres"})
books = books.drop(columns=['goodreads_book_id'])

# Optional: Preview
print(books[['title', 'genres']].head())

books.to_csv("merged_books.csv", index=False)
