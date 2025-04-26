import mysql.connector
from mysql.connector import Error
import psycopg2
from psycopg2 import Error as PsycopgError  # Import the Error class

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="mysql_db",
            port="3306",
            user="root",
            password="P@ssword",
            database="golf_db"
        )
        print("Connected to the database")
        return connection
    except Error as err:
        print("Error connecting to the database:", err)
        # Log the error for debugging purposes
        # logger.error("Error connecting to the database: %s", err)
        raise  # Raising the exception for the calling code to handle

def get_players_with_handicaps_and_leagues():
    connection = connect_to_database()
    players_with_handicaps_and_leagues = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # Fetch players' first names, last names, handicaps, and league names
            cursor.execute("""
                SELECT players.FirstName, players.LastName, players.Handicap, league.LeagueName
                FROM players
                INNER JOIN league ON players.LeagueID = league.LeagueID
                ORDER BY league.leagueName ASC          
            """)
            players_with_handicaps_and_leagues = cursor.fetchall()
        except mysql.connector.Error as err:
            print("Error fetching players, handicap, and leagues from the database:", err)
        finally:
            connection.close()
    return players_with_handicaps_and_leagues

def add_player(connection, first_name, last_name, handicap, league_id):
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO players (FirstName, LastName, Handicap, LeagueID) VALUES (%s, %s, %s, %s)"
        val = (first_name, last_name, handicap, league_id)
        cursor.execute(sql, val)
        connection.commit()
        print("Player added successfully")
    except mysql.connector.Error as err:
        print("Error adding player:", err)

def add_league(connection, league_name):
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO league (LeagueName) VALUES (%s)"
        val = (league_name,)
        cursor.execute(sql, val)
        connection.commit()
        league_id = cursor.lastrowid
        print("League added successfully")
        return league_id
    except mysql.connector.Error as err:
        print("Error adding league:", err)
        return None

def get_leagues_from_database():
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM league")
            leagues = cursor.fetchall()
            return leagues
        except mysql.connector.Error as err:
            print("Error fetching leagues from the database:", err)
        finally:
            connection.close()
    return []

def insert_player_score(connection, player_id, score, score_date, teebox_id):
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO scores (PlayerID, Score, Date, TeeboxID) VALUES (%s, %s, %s, %s)"
        val = (player_id, score, score_date, teebox_id)
        cursor.execute(sql, val)
        connection.commit()
        print("Score added successfully")
    except mysql.connector.Error as err:
        print("Error adding score:", err)

def update_player_and_league(connection, player_id, first_name, last_name, handicap, league_name):
    try:
        cursor = connection.cursor()

        # Get the LeagueID corresponding to the provided LeagueName
        cursor.execute("SELECT LeagueID FROM league WHERE LeagueName = %s", (league_name,))
        league_id = cursor.fetchone()[0]

        # Update player details
        sql_update_player = "UPDATE players SET FirstName = %s, LastName = %s, Handicap = %s, LeagueID = %s WHERE PlayerID = %s"
        val_update_player = (first_name, last_name, handicap, league_id, player_id)
        cursor.execute(sql_update_player, val_update_player)

        # Update league details
        sql_update_league = "UPDATE league SET LeagueName = %s WHERE LeagueID = %s"
        val_update_league = (league_name, league_id)
        cursor.execute(sql_update_league, val_update_league)

        connection.commit()
        print("Player and league details updated successfully")
    except mysql.connector.Error as err:
        print("Error updating player and league details:", err)

def delete_player_and_league(connection, player_id):
    try:
        cursor = connection.cursor()

        # Get the LeagueID of the player to delete
        cursor.execute("SELECT LeagueID FROM players WHERE PlayerID = %s", (player_id,))
        league_id = cursor.fetchone()

        if league_id:
            league_id = league_id[0]
            print("LeagueID:", league_id)  # Print the fetched LeagueID

            # Delete player's scores from Scores table
            cursor.execute("DELETE FROM scores WHERE PlayerID = %s", (player_id,))

            # Delete player from Players table
            cursor.execute("DELETE FROM players WHERE PlayerID = %s", (player_id,))

            # Delete associated league from League table
            cursor.execute("DELETE FROM league WHERE LeagueID = %s", (league_id,))

            connection.commit()
            print("Player and associated league deleted successfully")
        else:
            print("Player not found or associated with a league")
    except mysql.connector.Error as err:
        print("Error deleting player and league:", err)

def get_players_list(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT PlayerID, FirstName, LastName FROM players")
        player_details = cursor.fetchall()
        return player_details
    except mysql.connector.Error as err:
        print("Error fetching player details:", err)
        return None
    
def get_player_details(connection, player_id):
    try:
        cursor = connection.cursor(dictionary=True)
        sql_query = """
            SELECT players.PlayerID, players.FirstName, players.LastName, players.Handicap, league.LeagueName 
            FROM players 
            LEFT JOIN league ON players.LeagueID = league.LeagueID 
            WHERE players.PlayerID = %s
        """
        cursor.execute(sql_query, (player_id,))
        player_details = cursor.fetchone()
        return player_details
    except mysql.connector.Error as err:
        print("Error fetching player details:", err)
        return None   

def get_all_player_scores():
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT scores.*, players.FirstName, players.LastName 
                FROM scores 
                JOIN players ON scores.PlayerID = players.PlayerID 
                ORDER BY players.FirstName ASC, scores.Date ASC           
            """)
            scores = cursor.fetchall()
            return scores
        except mysql.connector.Error as err:
            print("Error fetching scores for all players from the database:", err)
        finally:
            connection.close()
    return []


def get_scores_for_player():
    connection = connect_to_database()
    all_scores = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Fetch all scores from the Scores table
            cursor.execute("""
                SELECT scores.*, players.FirstName, players.LastName 
                FROM scores 
                JOIN players ON scores.PlayerID = players.PlayerID
            """)
            scores = cursor.fetchall()

            # Append each score entry with player's name
            for score in scores:
                all_scores.append({
                    'PlayerID': score['PlayerID'],
                    'Score': score['Score'],
                    'Date': score['Date'],
                    'FirstName': score['FirstName'],
                    'LastName': score['LastName']
                })

            return all_scores
        except mysql.connector.Error as err:
            print("Error fetching all players' scores from the database:", err)
        finally:
            connection.close()
    return []

def get_all_teeboxes(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT TeeboxID, TeeboxName FROM teeboxes")
        teeboxes = cursor.fetchall()
        return teeboxes
    except mysql.connector.Error as e:
        print(f"Error fetching teebox information: {e}")
        return None
    
def update_score_in_database(connection, score_id, new_score, new_date, teebox_id):
    try:
        cursor = connection.cursor()
        sql_update_score = "UPDATE scores SET Score = %s, Date = %s, TeeboxID = %s WHERE ScoreID = %s"
        val_update_score = (new_score, new_date, teebox_id, score_id)
        cursor.execute(sql_update_score, val_update_score)
        connection.commit()
    except Exception as e:
        # Rollback changes if an error occurs
        connection.rollback()
        raise e

def get_score_details(connection, score_id):
    """
    Fetch details of a score from the database based on the score ID.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT scores.*, players.FirstName, players.LastName 
            FROM scores 
            JOIN players ON scores.PlayerID = players.PlayerID
            WHERE scores.ScoreID = %s
        """
        cursor.execute(query, (score_id,))
        score_details = cursor.fetchone()
        return score_details
    except mysql.connector.Error as err:
        # Handle any exceptions, such as database errors
        print("Error fetching score details from the database:", err)
        return None
    
def delete_score(connection, score_id):
    """Delete a score from the database."""
    try:
        with connection.cursor() as cursor:
            # Execute the SQL query to delete the score
            sql = "DELETE FROM scores WHERE ScoreID = %s"
            cursor.execute(sql, (score_id,))
            # Commit the transaction
            connection.commit()
            return True  # Deletion successful
    except Exception as e:
        # Handle any errors
        print(f"Error deleting score: {e}")
        return False  # Deletion failed
    
def execute_postgres_query(query):
    """
    Execute a PostgreSQL query.
    """
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="P@ssword",
            host="postgres_db",
            port="5432"
        )
        cursor = connection.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows

    except PsycopgError as e:
        return f"Error executing query: {e}"

def get_golf_rounds_statistics():
    query = """
        SELECT
            COUNT(CASE WHEN score <= 39 THEN 1 END) AS rounds_39_and_under,
            COUNT(CASE WHEN score BETWEEN 40 AND 49 THEN 1 END) AS rounds_between_40_and_49,
            COUNT(CASE WHEN score > 50 THEN 1 END) AS rounds_above_50,
            COUNT(*) AS total_rounds,
            CASE WHEN COUNT(*) > 0 THEN COUNT(CASE WHEN score <= 39 THEN 1 END) * 100.0 / COUNT(*) ELSE 0 END AS percentage_39_and_under,
            CASE WHEN COUNT(*) > 0 THEN COUNT(CASE WHEN score BETWEEN 40 AND 49 THEN 1 END) * 100.0 / COUNT(*) ELSE 0 END AS percentage_between_40_and_49,
            CASE WHEN COUNT(*) > 0 THEN COUNT(CASE WHEN score > 50 THEN 1 END) * 100.0 / COUNT(*) ELSE 0 END AS percentage_above_50
        FROM scores;
    """
    result = execute_postgres_query(query)
    return result if result else []  # Ensure a safe return value


def get_handicap_statistics():
    """
    Retrieve handicap statistics from the database.
    """
    query = """
        SELECT
            COUNT(CASE WHEN Handicap < 0 THEN 1 END) AS handicap_less_than_0,
            COUNT(CASE WHEN Handicap BETWEEN 1 AND 5 THEN 1 END) AS handicap_1_to_5,
            COUNT(CASE WHEN Handicap BETWEEN 6 AND 10 THEN 1 END) AS handicap_6_to_10,
            COUNT(CASE WHEN Handicap BETWEEN 11 AND 15 THEN 1 END) AS handicap_11_to_15,
            COUNT(CASE WHEN Handicap BETWEEN 16 AND 20 THEN 1 END) AS handicap_16_to_20,
            COUNT(*) AS total_players,
            COUNT(CASE WHEN Handicap < 0 THEN 1 END) * 100.0 / COUNT(*) AS percentage_less_than_0,
            COUNT(CASE WHEN Handicap BETWEEN 1 AND 5 THEN 1 END) * 100.0 / COUNT(*) AS percentage_1_to_5,
            COUNT(CASE WHEN Handicap BETWEEN 6 AND 10 THEN 1 END) * 100.0 / COUNT(*) AS percentage_6_to_10,
            COUNT(CASE WHEN Handicap BETWEEN 11 AND 15 THEN 1 END) * 100.0 / COUNT(*) AS percentage_11_to_15,
            COUNT(CASE WHEN Handicap BETWEEN 16 AND 20 THEN 1 END) * 100.0 / COUNT(*) AS percentage_16_to_20
        FROM
            players;
    """
    return execute_postgres_query(query)


def get_players_low_rounds():
    """
    Retrieve handicap statistics from the database.
    """
    query = """
                SELECT p.FirstName, p.LastName, s.Score, s.Date
                FROM players p
                INNER JOIN (
                SELECT PlayerID, MIN(Score) AS LowestScore
                FROM scores
                GROUP BY PlayerID
                ) AS min_scores ON p.PlayerID = min_scores.PlayerID
                INNER JOIN scores s ON p.PlayerID = s.PlayerID AND s.Score = min_scores.LowestScore
                ORDER BY s.Score;
            """      
    return execute_postgres_query(query)



