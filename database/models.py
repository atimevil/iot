"""Database models for game scores"""
import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'scores.db')


class Database:
    """SQLite database manager for game scores"""

    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Game statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_name TEXT NOT NULL,
                total_plays INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                highest_score INTEGER DEFAULT 0,
                last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Initialize game stats for each game if not exists
        games = ['snake', 'tetris', 'suika']
        for game in games:
            cursor.execute('''
                INSERT OR IGNORE INTO game_stats (id, game_name, total_plays, total_score, highest_score)
                VALUES (?, ?, 0, 0, 0)
            ''', (games.index(game) + 1, game))

        conn.commit()
        conn.close()

    def add_score(self, game_name, player_name, score, difficulty=None):
        """Add a new score to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Insert score
        cursor.execute('''
            INSERT INTO scores (game_name, player_name, score, difficulty)
            VALUES (?, ?, ?, ?)
        ''', (game_name, player_name, score, difficulty))

        # Update game statistics
        cursor.execute('''
            UPDATE game_stats
            SET total_plays = total_plays + 1,
                total_score = total_score + ?,
                highest_score = MAX(highest_score, ?),
                last_played = CURRENT_TIMESTAMP
            WHERE game_name = ?
        ''', (score, score, game_name))

        conn.commit()
        conn.close()

    def get_top_scores(self, game_name, limit=10, difficulty=None):
        """Get top scores for a specific game"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if difficulty:
            cursor.execute('''
                SELECT player_name, score, difficulty, created_at
                FROM scores
                WHERE game_name = ? AND difficulty = ?
                ORDER BY score DESC
                LIMIT ?
            ''', (game_name, difficulty, limit))
        else:
            cursor.execute('''
                SELECT player_name, score, difficulty, created_at
                FROM scores
                WHERE game_name = ?
                ORDER BY score DESC
                LIMIT ?
            ''', (game_name, limit))

        scores = cursor.fetchall()
        conn.close()

        return [dict(row) for row in scores]

    def get_all_top_scores(self, limit=10):
        """Get top scores across all games"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT game_name, player_name, score, difficulty, created_at
            FROM scores
            ORDER BY score DESC
            LIMIT ?
        ''', (limit,))

        scores = cursor.fetchall()
        conn.close()

        return [dict(row) for row in scores]

    def get_game_stats(self, game_name):
        """Get statistics for a specific game"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM game_stats
            WHERE game_name = ?
        ''', (game_name,))

        stats = cursor.fetchone()
        conn.close()

        return dict(stats) if stats else None

    def get_all_stats(self):
        """Get statistics for all games"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM game_stats ORDER BY game_name')
        stats = cursor.fetchall()
        conn.close()

        return [dict(row) for row in stats]

    def clear_scores(self, game_name=None):
        """Clear scores (for testing/admin purposes)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if game_name:
            cursor.execute('DELETE FROM scores WHERE game_name = ?', (game_name,))
            cursor.execute('''
                UPDATE game_stats
                SET total_plays = 0, total_score = 0, highest_score = 0
                WHERE game_name = ?
            ''', (game_name,))
        else:
            cursor.execute('DELETE FROM scores')
            cursor.execute('UPDATE game_stats SET total_plays = 0, total_score = 0, highest_score = 0')

        conn.commit()
        conn.close()


# Create global database instance
db = Database()
