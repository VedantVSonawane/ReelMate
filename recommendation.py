import os
import google.generativeai as genai
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from models import Movie
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def load_data():
    """
    Loads movie data from the SQLite database into a pandas DataFrame.
    """
    movies = Movie.query.all()
    if not movies:
        return pd.DataFrame()
    
    data = [m.to_dict() for m in movies]
    df = pd.DataFrame(data)
    
    # Create 'content' column for TF-IDF
    df['content'] = df['genres'].fillna('') + " " + df['description'].fillna('')
    return df

def generate_ai_explanation(target_movie, mood, selected_titles):
    """
    Uses Gemini to generate a custom, hype-man explanation.
    """
    if not GEMINI_API_KEY:
        return None

    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = (
            f"The user loves movies like {', '.join(selected_titles[:3])}. "
            f"They are currently in a '{mood}' mood. "
            f"Write a short, funny, 1-sentence 'hype-man' reason why they MUST watch '{target_movie}'. "
            "Use emojis. Be casual and enthusiastic."
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def get_recommendations(selected_movie_ids, mood=None, top_n=10):
    """
    Generates weighted recommendations with explanations.
    Weights: Genre/Content (50%), Year Proximity (10%), Platform Match (20%), Mood (20%)
    """
    df = load_data()
    
    if df.empty:
        return []

    selected_movies = df[df['id'].isin(selected_movie_ids)]
    selected_titles = selected_movies['title'].tolist() if not selected_movies.empty else []
    
    # Mood Mapping
    mood_genres = {
        'think': ['Sci-Fi', 'Thriller', 'Mystery', 'Drama'],
        'laugh': ['Comedy', 'Animation'],
        'cry': ['Drama', 'Romance'],
        'chill': ['Action', 'Adventure']
    }
    target_genres = mood_genres.get(mood, [])

    if selected_movies.empty and not target_genres:
        return df.head(top_n).to_dict('records')

    # 1. Content Similarity (TF-IDF)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['content'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # 2. Calculate Scores
    recommendations = []
    
    for idx, row in df.iterrows():
        if row['id'] in selected_movie_ids:
            continue
            
        # Calculate average similarity to selected movies
        content_score = 0
        year_score = 0
        platform_score = 0
        mood_score = 0
        explanations = []
        
        # Content & Year & Platform from selected movies
        if not selected_movies.empty:
            for _, selected_row in selected_movies.iterrows():
                selected_idx = df.index[df['id'] == selected_row['id']].tolist()[0]
                
                # Content
                sim = cosine_sim[idx][selected_idx]
                content_score += sim
                
                # Year
                diff = abs(row['year'] - selected_row['year'])
                y_score = 1 / (1 + diff/10)
                year_score += y_score
                
                # Platform
                p1 = set(row['platforms'].split('|'))
                p2 = set(selected_row['platforms'].split('|'))
                if not p1.isdisjoint(p2):
                    platform_score += 1

            n_selected = len(selected_movies)
            content_score /= n_selected
            year_score /= n_selected
            platform_score /= n_selected
        
        # Mood Score
        if target_genres:
            movie_genres = row['genres'].split('|')
            if any(g in target_genres for g in movie_genres):
                mood_score = 1.0
                explanations.append(f"Matches your '{mood}' vibe")

        # Weighted Final Score
        # Adjust weights if no movies selected (cold start with mood)
        if selected_movies.empty:
            final_score = mood_score
        else:
            final_score = (content_score * 0.5) + (year_score * 0.1) + (platform_score * 0.2) + (mood_score * 0.2)
        
        # Generate "Hype-Man" Explanation (Fallback)
        if content_score > 0.3:
            explanations.append("Totally your style")
        if year_score > 0.8:
            explanations.append(f"Classic {row['year']} energy")
        if platform_score > 0.5:
            explanations.append("Ready to watch on your apps")
            
        # Randomize tone slightly
        import random
        intros = ["OMG, you have to see this!", "This one is a GEM.", "Absolute banger alert!", "Trust me on this one."]
        explanation_str = f"{random.choice(intros)} {', '.join(explanations)}."

        recommendations.append({
            **row.to_dict(),
            'score': final_score,
            'explanation': explanation_str,
            'hype_rating': min(5, int(final_score * 5) + 3) # Fake hype rating 3-5
        })

    # Sort and return
    recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)
    top_recs = recommendations[:top_n]

    # 3. AI Enhancement (Only for top 3 to save time/quota)
    if GEMINI_API_KEY:
        for i in range(min(3, len(top_recs))):
            ai_exp = generate_ai_explanation(top_recs[i]['title'], mood, selected_titles)
            if ai_exp:
                top_recs[i]['explanation'] = ai_exp

    return top_recs
