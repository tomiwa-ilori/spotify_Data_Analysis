# Import required libraries
import numpy as np
import pandas as pd
import seaborn as sns
import spotipy
import matplotlib.pyplot as plt
from collections import Counter
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyDataAnalyzer:
    # Initialize the analyzer with Spotify credentials
    def __init__(self, client_id, client_secret):
        """ 
            Initialize the analyzer with Spotify credentials
        """
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    
    # Load and combine data from multiple JSON files into a single DataFrame
    def load_data(self, *file_paths):
        """ 
            Load and combine data from multiple JSON files into a single DataFrame
        """
        dataframes = [pd.read_json(file) for file in file_paths]
        self.df = pd.concat(dataframes, ignore_index=True)
        # Convert milliseconds to minutes and round to 2 decimal places
        self.df['msPlayed (minutes)'] = (self.df['msPlayed'] / 60000).round(2)
    
    # Plot the top 20 artists by song play count
    def plot_top_artists_by_play_count(self):
        """ 
            Plot the top 20 artists by song play count
        """
        artist_by_count = self.df['artistName'].value_counts().head(20).sort_values()
        artist_by_count.plot(kind='barh', figsize=(10, 5), color='blue')
        plt.title("Top 20 Artists by Number of Times Played")
        plt.xlabel("Play Count of Songs")
        plt.ylabel("Artist Name")
        plt.show()

    # Plot the top 20 artists by total minutes their songs have been played
    def plot_top_artists_by_minutes_played(self):
        """ 
            Plot the top 20 artists by total minutes their songs have been played
        """
        artist_by_minutes = self.df.groupby('artistName')['msPlayed (minutes)'].sum().nlargest(20).sort_values()
        artist_by_minutes.plot(kind='barh', figsize=(10, 5), color='green')
        plt.title("Top 20 Artists by Number of Minutes Played")
        plt.xlabel("Number of Minutes Played")
        plt.ylabel("Artist Name")
        plt.show()

    # Analyze and visualize the top 20 songs by year
    def analyze_and_visualize_top_songs_by_year(self):
        # Extract year and month from endTime
        """ 
            Analyze and visualize the top 20 songs by year
        """
        self.df['year'] = pd.to_datetime(self.df['endTime']).dt.year
        top_songs_year = self.df.groupby(['year', 'trackName']).size().reset_index(name='playCount')
        top_songs_year = top_songs_year.sort_values(['year', 'playCount'], ascending=[True, False])
        top_songs_year = top_songs_year.groupby('year').head(20)

        # Plot the top 20 songs for each year
        for year in top_songs_year['year'].unique():
            plt.figure(figsize=(10, 6))
            df_year = top_songs_year[top_songs_year['year'] == year]
            df_year = df_year.sort_values('playCount', ascending=True)
            plt.barh(df_year['trackName'], df_year['playCount'], color='blue')
            plt.xlabel('Play Count')
            plt.ylabel('Track Name')
            plt.title(f'Top 20 Songs in {year}')
            plt.show()

    # Analyze and visualize the top 20 songs by month
    def analyze_and_visualize_top_songs_by_month(self):
        """
            Analyze and visualize the top 20 songs by month       
        """
        top_songs_month = self.df.groupby(['year', 'month', 'trackName'])['msPlayed (minutes)'].sum().reset_index()
        top_songs_month = top_songs_month.sort_values(['year', 'month', 'msPlayed (minutes)'], ascending=[True, True, False])
        top_songs_month = top_songs_month.groupby(['year', 'month']).head(20)

        # Plot the top 20 songs for each month
        for (year, month), group in top_songs_month.groupby(['year', 'month']):
            plt.figure(figsize=(10, 6))
            plt.barh(group['trackName'], group['msPlayed (minutes)'])
            plt.xlabel('Minutes Played')
            plt.ylabel('Track Name')
            plt.title(f'Top 20 Songs in {year}-{month:02d}')
            plt.show()

    # Visualize the distribution of streams across different hours of the day
    def visualize_streams_by_hour_of_day(self):
        """ 
            Visualize the distribution of streams across different hours of the day
        """
        self.df['hour'] = pd.to_datetime(self.df['endTime']).dt.hour
        distribution = self.df['hour'].value_counts().sort_index()
        distribution.plot(kind='bar', figsize=(10, 5))
        plt.xlabel('Hour of the Day')
        plt.ylabel('Number of Streams')
        plt.title('Distribution of Streams Across Different Hours of the Day')
        plt.show()

    # Authenticate with Spotify and fetch genre data
    def fetch_and_visualize_genre_data(self):
        # Fetch genres for tracks in the specific year
        for year in self.df['year'].unique():
            genres_counter = Counter()
            df_year = self.df[self.df['year'] == year]
            for track in df_year['trackName'].unique():
                track_data = self.sp.search(q=track, type='track')
                if track_data['tracks']['items']:
                    first_track = track_data['tracks']['items'][0]
                    artist_id = first_track['artists'][0]['id']
                    artist_details = self.sp.artist(artist_id)
                    genres_counter.update(artist_details['genres'])
            
            # Visualize the top genres for the specific year
            top_genres = dict(genres_counter.most_common(10))
            plt.figure(figsize=(10, 6))
            plt.bar(top_genres.keys(), top_genres.values(), color='green')
            plt.xlabel('Genres')
            plt.ylabel('Frequency')
            plt.title(f'Top Genres in {year}')
            plt.xticks(rotation=45)
            plt.show()


if __name__ == "__main__":
    client_ID = "xxxxxxxxxxx"
    client_SECRET = "xxxxxxxxxxx"
    # Create an instance of the analyzer
    analyzer = SpotifyDataAnalyzer(client_ID, client_SECRET)

    # Load and combine data from multiple JSON files into a single DataFrame
    analyzer.load_data('data.json', 'data2.json', 'data3.json', 'data4.json')

    # Plot the top 20 artists by song play count
    analyzer.plot_top_artists_by_play_count()

    # Plot the top 20 artists by total minutes their songs have been played
    analyzer.plot_top_artists_by_minutes_played()

    # Analyze and visualize the top 20 songs by year
    analyzer.analyze_and_visualize_top_songs_by_year()

    # Analyze and visualize the top 20 songs by month
    analyzer.analyze_and_visualize_top_songs_by_month()

    # Visualize the distribution of streams across different hours of the day
    analyzer.visualize_streams_by_hour_of_day()

    # Analyze and visualize the top 20 songs by month
    analyzer.fetch_and_visualize_genre_data()
