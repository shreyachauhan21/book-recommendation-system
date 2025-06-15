import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def fetch_description_safe(row):
    title, author = row['title'], row['authors']
    query = f"{title} {author}" if author else title
    url = f"https://openlibrary.org/search.json?q={requests.utils.quote(query)}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['docs']:
            work_key = data['docs'][0].get('key')
            if work_key:
                work_url = f"https://openlibrary.org{work_key}.json"
                work_response = requests.get(work_url, timeout=10)
                work_response.raise_for_status()
                work_data = work_response.json()
                desc = work_data.get('description')
                if isinstance(desc, dict):
                    return desc.get('value', '')
                return desc if isinstance(desc, str) else None
    except Exception as e:
        print(f"❌ Error for {title}: {e}", flush=True)
    return None

# Load dataset
books_df = pd.read_csv("data/merged_books.csv")

# Ensure 'description' column exists
if 'description' not in books_df.columns:
    books_df['description'] = None

# Filter rows that need description
rows_to_update = books_df[pd.isna(books_df['description']) | (books_df['description'] == '')]
print(f"🔁 Updating {len(rows_to_update)} missing descriptions...\n", flush=True)

# Multithreaded fetching with progress bar
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_idx = {
        executor.submit(fetch_description_safe, row): idx
        for idx, row in rows_to_update.iterrows()
    }

    for future in tqdm(as_completed(future_to_idx), total=len(future_to_idx)):
        idx = future_to_idx[future]
        try:
            desc = future.result()
            books_df.at[idx, 'description'] = desc
            short_title = books_df.at[idx, 'title'][:40]
            short_desc = desc[:60] if desc else "No description"
            print(f"✅ {short_title} → {short_desc}", flush=True)
        except Exception as e:
            print(f"❌ Exception in future for index {idx}: {e}", flush=True)

# Save the updated CSV
try:
    books_df.to_csv("data/merged_books.csv", index=False)
    print("\n🎉 Done updating descriptions and saved to CSV!", flush=True)
except Exception as e:
    print(f"❌ Failed to save CSV: {e}", flush=True)
