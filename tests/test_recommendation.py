import pytest
import pandas as pd
import sys
import os

# Add parent directory to path to import recommendation.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation import get_recommendations, load_data

def test_load_data():
    df = load_data('movies.csv', 'ott_mapping.csv')
    assert not df.empty
    assert 'content' in df.columns
    assert 'platforms' in df.columns
    # Check if only Indian OTTs are present (or empty if not available)
    # Since our dummy data is all mapped to valid OTTs, we expect rows.
    assert len(df) > 0

def test_get_recommendations_returns_list():
    # Test with a valid movie ID (e.g., 1 for The Matrix)
    recommendations = get_recommendations([1], movies_path='movies.csv', ott_path='ott_mapping.csv')
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert len(recommendations) <= 10
    # Check for new fields
    assert 'score' in recommendations[0]
    assert 'explanation' in recommendations[0]
    assert 'hype_rating' in recommendations[0]

def test_get_recommendations_excludes_selected():
    selected_id = 1
    recommendations = get_recommendations([selected_id], movies_path='movies.csv', ott_path='ott_mapping.csv')
    rec_ids = [r['id'] for r in recommendations]
    assert selected_id not in rec_ids

def test_get_recommendations_content_relevance():
    # Selecting "Toy Story" (Animation) should recommend other animations
    # Toy Story ID is 11
    recommendations = get_recommendations([11], movies_path='movies.csv', ott_path='ott_mapping.csv')
    
    rec_ids = [r['id'] for r in recommendations]
    
    # Relevant animations in our dataset
    relevant_ids = [12, 13, 14, 17, 18, 19, 20] 
    
    intersection = set(rec_ids).intersection(relevant_ids)
    assert len(intersection) > 0

def test_get_recommendations_with_mood():
    # Test mood boosting
    # "laugh" mood should boost Comedy/Animation
    recommendations = get_recommendations([], mood='laugh', movies_path='movies.csv', ott_path='ott_mapping.csv')
    
    # Check if we got recommendations even without selected movies
    assert len(recommendations) > 0
    
    # Check if explanation references the mood
    has_mood_explanation = any("laugh" in r['explanation'] or "Comedy" in r['genres'] for r in recommendations)
    assert has_mood_explanation
