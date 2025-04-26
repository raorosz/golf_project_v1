using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading;
using MySql.Data.MySqlClient;
using Npgsql;
using NpgsqlTypes;

namespace Worker
{
    class Program
    {
        static void Main(string[] args)
        {
            var mysqlConnectionString = "Server=mysql_db;Database=golf_db;Uid=root;Pwd=P@ssword;";
            var postgresConnectionString = "Host=postgres_db;Username=postgres;Password=P@ssword;Database=postgres;";

            while (true)
            {
                Thread.Sleep(5000); // Wait for 5 seconds between each iteration

                try
                {
                    using (var mysqlConnection = new MySqlConnection(mysqlConnectionString))
                    using (var postgresConnection = new NpgsqlConnection(postgresConnectionString))
                    {
                        mysqlConnection.Open();
                        postgresConnection.Open();

                        // Fetch initial data from MySQL
                        var data = FetchDataFromMySQL(mysqlConnection);

                        // Update handicaps in MySQL
                        CalculateAndStoreHandicap(data, mysqlConnection);

                        // REFRESH players table to get updated handicaps
                        data.Tables.Remove("players");
                        var updatedPlayers = new DataTable("players");
                        using (var cmd = new MySqlCommand("SELECT * FROM players", mysqlConnection))
                        using (var reader = cmd.ExecuteReader())
                        {
                            updatedPlayers.Load(reader);
                        }
                        data.Tables.Add(updatedPlayers);

                        // Transfer updated data into Postgres
                        InsertDataIntoPostgres(data, postgresConnection);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error: {ex.Message}");
                }
            }
        }

        static DataSet FetchDataFromMySQL(MySqlConnection connection)
        {
            var dataSet = new DataSet();
            var tables = new[] { "players", "league", "scores", "teeboxes" };

            foreach (var table in tables)
            {
                var dataTable = new DataTable(table);
                string orderByClause = table == "scores" ? "ORDER BY Date DESC" : "";
                using (var cmd = new MySqlCommand($"SELECT * FROM {table} {orderByClause}", connection))
                using (var reader = cmd.ExecuteReader())
                {
                    dataTable.Load(reader);
                }
                dataSet.Tables.Add(dataTable);
            }
            return dataSet;
        }

        static void CalculateAndStoreHandicap(DataSet data, MySqlConnection mySqlConnection)
        {
            foreach (DataRow playerRow in data.Tables["players"].Rows)
            {
                int playerId = Convert.ToInt32(playerRow["PlayerID"]);
                var playerScores = data.Tables["scores"].AsEnumerable()
                    .Where(row => Convert.ToInt32(row["PlayerID"]) == playerId)
                    .OrderByDescending(row => row["Date"])
                    .Take(5)
                    .ToList();

                if (playerScores.Any())
                {
                    double handicapIndex = CalculateHandicapIndex(playerScores);
                    int lastTeeboxId = Convert.ToInt32(playerScores.First()["TeeboxID"]);
                    var teebox = data.Tables["teeboxes"].AsEnumerable()
                        .FirstOrDefault(row => Convert.ToInt32(row["TeeboxID"]) == lastTeeboxId);

                    if (teebox != null)
                    {
                        int slopeRating = Convert.ToInt32(teebox["Slope"]);
                        decimal courseRating = Convert.ToDecimal(teebox["Rating"]);
                        int par = Convert.ToInt32(teebox["Par"]);

                        double differentialSum = playerScores.Sum(row => (Convert.ToInt32(row["Score"]) - par) * 113.0 / slopeRating);
                        double averageDifferential = differentialSum / playerScores.Count;

                        double handicap = ((handicapIndex - 36)) * (slopeRating / 56.5) + (Convert.ToDouble(courseRating) - par);

                        StoreOrUpdateHandicap(playerId, handicap, mySqlConnection);
                    }
                    else
                    {
                        Console.WriteLine($"Teebox not found for player {playerId}.");
                    }
                }
                else
                {
                    Console.WriteLine($"No scores found for player {playerId}.");
                }
            }
        }

        static double CalculateHandicapIndex(List<DataRow> playerScores)
        {
            var scores = playerScores.Select(row => Convert.ToDouble(row["Score"]));
            return scores.Average();
        }

        static void StoreOrUpdateHandicap(int playerId, double handicap, MySqlConnection mysqlConnection)
        {
            try
            {
                Console.WriteLine($"Updating handicap for player ID: {playerId}");
                using (var cmd = new MySqlCommand("UPDATE players SET Handicap = @handicap WHERE PlayerID = @playerId", mysqlConnection))
                {
                    cmd.Parameters.AddWithValue("@handicap", handicap);
                    cmd.Parameters.AddWithValue("@playerId", playerId);
                    int rowsAffected = cmd.ExecuteNonQuery();

                    if (rowsAffected == 0)
                        Console.WriteLine($"Player with ID {playerId} not found.");
                    else
                        Console.WriteLine($"Handicap updated successfully for player {playerId}.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error updating handicap: {ex.Message}");
            }
        }

        static void InsertDataIntoPostgres(DataSet data, NpgsqlConnection postgresConnection)
        {
            try
            {
                TruncatePostgresTables(postgresConnection);

                foreach (DataTable table in data.Tables)
                {
                    TransferDataToPostgres(table, table.TableName, postgresConnection);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error inserting into PostgreSQL: {ex.Message}");
            }
        }

        static void TruncatePostgresTables(NpgsqlConnection postgresConnection)
        {
            using (var cmd = new NpgsqlCommand("TRUNCATE TABLE players, league, scores, teeboxes", postgresConnection))
            {
                cmd.ExecuteNonQuery();
            }
        }

        static void TransferDataToPostgres(DataTable dataTable, string tableName, NpgsqlConnection connection)
        {
            Console.WriteLine($"Transferring data for table: {tableName}");

            if (tableName == "scores")
            {
                using (var writer = connection.BeginBinaryImport("COPY scores (ScoreID, PlayerID, Score, Date) FROM STDIN (FORMAT BINARY)"))
                {
                    foreach (DataRow row in dataTable.Rows)
                    {
                        writer.StartRow();
                        writer.Write(Convert.ToInt32(row["ScoreID"]), NpgsqlDbType.Integer);
                        writer.Write(Convert.ToInt32(row["PlayerID"]), NpgsqlDbType.Integer);
                        writer.Write(Convert.ToInt32(row["Score"]), NpgsqlDbType.Integer);
                        writer.Write(Convert.ToDateTime(row["Date"]), NpgsqlDbType.Date);
                    }
                    writer.Complete();
                }
            }
            else
            {
                using (var writer = connection.BeginBinaryImport($"COPY {tableName} FROM STDIN (FORMAT BINARY)"))
                {
                    foreach (DataRow row in dataTable.Rows)
                    {
                        writer.StartRow();
                        foreach (var item in row.ItemArray)
                        {
                            if (item is int)
                                writer.Write((int)item, NpgsqlDbType.Integer);
                            else if (item is string)
                                writer.Write(item.ToString(), NpgsqlDbType.Text);
                            else if (item is DateTime)
                                writer.Write((DateTime)item, NpgsqlDbType.Date);
                            else if (item is decimal)
                                writer.Write((decimal)item, NpgsqlDbType.Numeric);
                            else
                                writer.WriteNull();
                        }
                    }
                    writer.Complete();
                }
            }
        }
    }
}