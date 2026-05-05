import pandas as pd
from datetime import datetime
import json
import os

class InteractionTracker:
    def __init__(self, storage_file = 'user_interactions.json'):
        self.storage_file = storage_file
        self.interactions = self._load_interactions()
        
        self.weights = {
            'view_poster': 1.0,      
            'view_overview': 1.5,     
            'view_cast': 2.0,         
            'hover': 1.0,             
            'like': 4.5,              
            'dislike': 0.5,           
            'add_to_watchlist': 4.0,  
            'click_details': 3.0      
        }
    
    
    def _load_interactions(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {}
    
    
    def _save_interactions(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.interactions, f, indent = 2)
    
    
    def track(self, user_id, movie_id, interaction_type, duration = 0):
        if user_id not in self.interactions:
            self.interactions[user_id] = []
        
        interaction = {
            'movie_id': int(movie_id),
            'type': interaction_type,
            'timestamp': datetime.now().isoformat(),
            'duration': duration
        }
        
        self.interactions[user_id].append(interaction)
        self._save_interactions()
        
        print(f"Tracked: User {user_id} - {interaction_type} on movie {movie_id}")
    
    
    def get_user_interactions(self, user_id):
        return self.interactions.get(user_id, [])
    
    
    def calculate_implicit_rating(self, user_id, movie_id):
        user_interactions = self.get_user_interactions(user_id)
        movie_interactions = [i for i in user_interactions if i['movie_id'] == movie_id]
        
        if not movie_interactions:
            return None
        
        total_score = 0
        
        for interaction in movie_interactions:
            base_score = self.weights.get(interaction['type'], 1.0)
            
            duration_boost = min(interaction['duration'] / 30, 0.5)  
            
            timestamp = datetime.fromisoformat(interaction['timestamp'])
            
            days_ago = (datetime.now() - timestamp).days
            
            recency_weight = 1.0 / (1 + days_ago / 7)  
            
            total_score += (base_score + duration_boost) * recency_weight
        
        avg_score = total_score / len(movie_interactions)
        normalized = min(5.0, max(0.5, avg_score))
        
        return round(normalized, 1)
    
    
    def get_all_ratings(self, user_id):
        user_interactions = self.get_user_interactions(user_id)
        
        if not user_interactions:
            return pd.DataFrame(columns=['movieId', 'implicit_rating'])
        
        unique_movies = list(set([i['movie_id'] for i in user_interactions]))
        
        ratings = []
        for movie_id in unique_movies:
            rating = self.calculate_implicit_rating(user_id, movie_id)
            if rating:
                ratings.append({
                    'movieId': movie_id,
                    'implicit_rating': rating
                })
        
        return pd.DataFrame(ratings)
    
    
    def get_interaction_count(self, user_id):
        return len(self.get_user_interactions(user_id))