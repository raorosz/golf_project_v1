-- Set up basic configs
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- Drop tables if they exist to avoid errors on re-run
DROP TABLE IF EXISTS scores CASCADE;
DROP TABLE IF EXISTS teeboxes CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS league CASCADE;

-- Create League Table
CREATE TABLE league (
    leagueid SERIAL PRIMARY KEY,
    leaguename VARCHAR(255) NOT NULL
);

-- Create Players Table
CREATE TABLE players (
    playerid SERIAL PRIMARY KEY,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    handicap INTEGER,
    leagueid INTEGER 
);

-- Create Scores Table
CREATE TABLE scores (
    scoreid SERIAL PRIMARY KEY,
    playerid INTEGER REFERENCES players(playerid) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    date DATE NOT NULL,
    teeboxid INTEGER  -- ✅ <-- ADD this column so you match MySQL
);

-- Create Teeboxes Table
CREATE TABLE teeboxes (
    teeboxid SERIAL PRIMARY KEY,
    teebox_name VARCHAR(255) NOT NULL,
    slope_rating INTEGER NOT NULL,
    course_rating NUMERIC(4, 1),
    par INTEGER NOT NULL
);

-- Insert dummy league (optional)
INSERT INTO league (leaguename) VALUES ('Default League');

-- Done!
