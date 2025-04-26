from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from database import connect_to_database, get_players_low_rounds, delete_score, get_handicap_statistics, get_golf_rounds_statistics, get_score_details, update_score_in_database, get_all_teeboxes, add_player, add_league, insert_player_score, get_leagues_from_database, get_players_with_handicaps_and_leagues, get_all_player_scores, get_players_list, update_player_and_league, delete_player_and_league, get_player_details
import mysql.connector
from psycopg2 import Error as PsycopgError  # Import the Error class
from mysql.connector import Error as MySQLError

app = Flask(__name__)


@app.route('/')
def index():
       return render_template('index.html')

@app.route('/players')
def all_players_scores():
    # Retrieve and display a list of scores for all players from the database
    scores = get_all_player_scores()
    return render_template('players.html', scores=scores)

@app.route('/standings')
def standings():
    # Retrieve league standings from the database (you need to implement this)
    leagues = get_leagues_from_database()
    return render_template('standings.html', leagues=leagues)


@app.route('/players_and_handicaps')
def players_and_handicaps():
    # Retrieve players with their handicaps and league names
    players_with_handicaps_and_leagues = get_players_with_handicaps_and_leagues()
    return render_template('players_and_handicaps.html', players_with_handicaps_and_leagues=players_with_handicaps_and_leagues)

@app.route('/player_scores')
def player_scores():
    # Retrieve and display a list of scores for the specified player from the database
    scores = get_all_player_scores()
    return render_template('player_scores.html', scores=scores)

@app.route('/add_league_and_player', methods=['GET','POST'])
def add_league_and_player():
    if request.method == 'POST':
        league_name = request.form['LeagueName']
        first_name = request.form['FirstName']
        last_name = request.form['LastName']
        handicap = request.form['Handicap']
        
        # Connect to the database
        connection = connect_to_database()
        if connection:
            try:
                league_id = add_league(connection, league_name)
                add_player(connection, first_name, last_name, handicap, league_id)
                connection.close()
                return redirect(url_for('add_league_and_player', success_message='League and player added successfully'))
            except Exception as e:
                # Handle any exceptions
                return f'Error: {e}'
        else:
            return 'Failed to connect to the database'
    elif request.method == 'GET':
        # Render the form for adding league and player
        return render_template('players.html')

@app.route('/add_player_score', methods=['GET', 'POST'])
def add_player_score():
    if request.method == 'POST':
        player_id = int(request.form['PlayerID'])
        score = int(request.form['Score'])
        score_date = datetime.strptime(request.form['Date'], '%Y-%m-%d').date()
        teebox_id = int(request.form['TeeboxID'])  # Assuming the teebox ID is sent in the form data


        # Connect to the database
        connection = connect_to_database()
        if connection:
            try:
                insert_player_score(connection, player_id, score, score_date, teebox_id)
                connection.close()
                return redirect(url_for('add_player_score', success_message='Score added successfullly'))
            except Exception as e:
                # Handle any exceptions
                return f'Error: {e}'
        else:
            return 'Failed to connect to the database'
    elif request.method == 'GET':
        # Fetch the list of players from the database
        connection = connect_to_database()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT PlayerID, FirstName, LastName FROM players")
                players = cursor.fetchall()

                cursor.execute("SELECT TeeboxID, TeeboxName FROM teeboxes")
                teeboxes = cursor.fetchall()

                connection.close()
            except Exception as e:
                # Handle any exceptions
                return f'Error: {e}'
        else:
            return 'Failed to connect to the database'

        # Render the form for adding a score, passing the list of players to the template
        return render_template('add_player_score.html', players=players, teeboxes=teeboxes)
    else:
        return 'Invalid request method'

@app.route('/edit_player', methods=['GET', 'POST'])
def edit_player():
    connection = connect_to_database()
    if connection:
        if request.method == 'POST':
            player_id = request.form['PlayerID']
            return redirect(url_for('edit_player_details', player_id=player_id))
        else:
            players = get_players_list(connection)
            connection.close()
            return render_template('edit_player.html', players=players)
    else:
        return 'Failed to connect to the database'
  
@app.route('/update_player_and_league/<int:player_id>', methods=['GET', 'POST'])
def edit_player_details(player_id):
    connection = connect_to_database()
    if connection:
        if request.method == 'POST':
            # Process the form data to update player and league details
            
            # Redirect to the /players route after updating the details
            return redirect(url_for('index'))
        else:
            # Fetch player details from the database based on the player_id
            player_details = get_player_details(connection, player_id)
            connection.close()
            return render_template('update_player_and_league.html', player_details=player_details)
    else:
     return 'Failed to connect to the database' 

@app.route('/update_player_and_league', methods=['POST'])
def update_player_and_league():
    if request.method == 'POST':
        player_id = request.form['PlayerID']
        league_name = request.form['LeagueName']
        first_name = request.form['FirstName']
        last_name = request.form['LastName']
        handicap = request.form['Handicap']
        
        # Connect to the database
        connection = connect_to_database()
        if connection:
            try:
                # Update league details
                cursor = connection.cursor()
                sql_update_league = "UPDATE league SET LeagueName = %s WHERE LeagueID = (SELECT LeagueID FROM players WHERE PlayerID = %s)"
                cursor.execute(sql_update_league, (league_name, player_id))

                # Update player details
                sql_update_player = "UPDATE players SET FirstName = %s, LastName = %s, Handicap = %s WHERE PlayerID = %s"
                cursor.execute(sql_update_player, (first_name, last_name, handicap, player_id))

                connection.commit()
                connection.close()
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                return f'Error updating player and league details: {err}'
        else:
            return 'Failed to connect to the database'
    else:
        return 'Invalid request method'
    
@app.route('/delete_player_and_league', methods=['POST'])
def delete_player_and_league():
    if request.method == 'POST':
        player_id = request.form['PlayerID']
        
        # Connect to the database
        connection = connect_to_database()
        if connection:
            try:
                # Delete player
                cursor = connection.cursor()

                # Delete associated league
                sql_delete_league = "DELETE FROM league WHERE LeagueID IN (SELECT LeagueID FROM players WHERE PlayerID = %s)"
                cursor.execute(sql_delete_league, (player_id,))

                sql_delete_player = "DELETE FROM players WHERE PlayerID = %s"
                cursor.execute(sql_delete_player, (player_id,))

                # Delete associated league
                # sql_delete_league = "DELETE FROM League WHERE LeagueID IN (SELECT LeagueID FROM Players WHERE PlayerID = %s)"
                # cursor.execute(sql_delete_league, (player_id,))

                connection.commit()
                connection.close()
                return redirect(url_for('edit_player', success_message='Score added successfullly'))
            except mysql.connector.Error as err:
                return f'Error deleting player and league: {err}'
        else:
            return 'Failed to connect to the database'
    elif request.method == 'GET':
        # Fetch the list of players from the database
        connection = connect_to_database()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT PlayerID, FirstName, LastName FROM players ORDER BY FirstName, LastName")
                players = cursor.fetchall()
                connection.close()
            except Exception as e:
                # Handle any exceptions
                return f'Error: {e}'
        else:
            return 'Failed to connect to the database'

        # Render the form for adding a score, passing the list of players to the template
        return render_template('edit_player.html', players=players)
    else:
        return 'Invalid request method'

@app.route('/select_teebox', methods=['GET'])
def select_teebox():
    # Connect to the database
    connection = connect_to_database()
    if connection:
        try:
            # Fetch all teebox information from the database
            teeboxes = get_all_teeboxes(connection)
            connection.close()
            
            # Render the template with teebox options
            return render_template('select_teebox.html', teeboxes=teeboxes)
        except Exception as e:
            return f'Error: {e}'
    else:
        return 'Failed to connect to the database'

@app.route('/edit_score/<int:score_id>', methods=['GET', 'POST'])
def edit_score(score_id):
    if request.method == 'POST':
        # Process the form data to update the score in the database
        # You'll need to implement this logic based on your database structure
        return redirect(url_for('player_scores'))
    else:
        # Fetch score, player, and teebox details from the database based on the score ID
        connection = connect_to_database()
        if connection:
            try:
                score_details = get_score_details(connection, score_id)
                player_details = get_player_details(connection, score_details['PlayerID'])
                teeboxes = get_all_teeboxes(connection)  # Fetch teebox options

                connection.close()
                return render_template('edit_score.html', score_details=score_details, player_details=player_details, teeboxes=teeboxes)
            except Exception as e:
                # Handle any exceptions
                return f'Error: {e}'
        else:
            return 'Failed to connect to the database'
        
@app.route('/update_score/<int:score_id>', methods=['POST'])
def update_score(score_id):
    if request.method == 'POST':
        new_score = int(request.form['new_score'])
        new_date = datetime.strptime(request.form['new_date'], '%Y-%m-%d').date()
        teebox_id = int(request.form['teebox_id'])

        # print(new_score)

        # Connect to the database
        connection = connect_to_database()
        if connection:
            try:
                update_score_in_database(connection, score_id, new_score, new_date, teebox_id)
                connection.close()
                return redirect(url_for('player_scores'))  # Redirect to the page displaying all player scores
            except Exception as e:
                # Handle any exceptions
                return f'Error: {e}'
        else:
            return 'Failed to connect to the database'
        

@app.route('/delete_score/<int:score_id>', methods=['POST'])
def delete_score_route(score_id):
    # Connect to the database
    connection = connect_to_database()
    if not connection:
        return 'Failed to connect to the database'

    # Call the delete_score function to delete the score
    if delete_score(connection, score_id):
        return redirect(url_for('player_scores'))
    else:
        return 'Failed to delete the score'  # Handle deletion failure

        
@app.route('/api/players/<int:player_id>/handicap', methods=['POST'])
def update_player_handicap(player_id):
    if request.method == 'POST':
        new_handicap = request.json.get('handicap')

        # Call a function to update the player's handicap in the database
        # Example: update_player_handicap_in_database(player_id, new_handicap)

        return jsonify({'message': 'Player handicap updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request method'}), 405
 

@app.route('/results')
def show_combined_results():
    """
    Route to display combined golf rounds and handicap statistics.
    Handles cases where there's no data gracefully.
    """
    try:
        golf_rounds_results = get_golf_rounds_statistics() or []
        handicap_results = get_handicap_statistics() or []
        low_round_scores = get_players_low_rounds() or []

        print("Golf Round Results: ", golf_rounds_results)
        print("Handicap Results:", handicap_results)
        print("Low Round Scores:", low_round_scores)
        

        return render_template(
            'results.html',
            golf_rounds_results=golf_rounds_results,
            handicap_results=handicap_results,
            low_round_scores=low_round_scores
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred while fetching results: {e}")
        
        # Return a fallback message or an error page if needed
        return render_template(
            'results.html',
            golf_rounds_results=[],
            handicap_results=[],
            low_round_scores=[],
            error_message="No data available or an error occurred."
        )



if __name__ == '__main__':
    app.run(debug=True)