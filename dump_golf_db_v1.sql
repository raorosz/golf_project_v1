USE golf_db;

-- Drop old tables
DROP TABLE IF EXISTS `players`;
DROP TABLE IF EXISTS `scores`;
DROP TABLE IF EXISTS `teeboxes`;
DROP TABLE IF EXISTS `league`;

-- Re-create League Table
CREATE TABLE `league` (
  `LeagueID` int NOT NULL AUTO_INCREMENT,
  `LeagueName` varchar(255) NOT NULL,
  PRIMARY KEY (`LeagueID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert a dummy league
INSERT INTO `league` (`LeagueID`, `LeagueName`) VALUES
(1, 'Dummy League');

-- Re-create Players Table (still with LeagueID foreign key)
CREATE TABLE `players` (
  `PlayerID` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(255) DEFAULT NULL,
  `LastName` varchar(255) DEFAULT NULL,
  `Handicap` int NOT NULL,
  `LeagueID` int DEFAULT NULL,  -- Keep leagueid field if you want, just no constraint
  PRIMARY KEY (`PlayerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Optional: Insert starter player
INSERT INTO `players` (FirstName, LastName, Handicap, LeagueID) VALUES
('Robert', 'Orosz', 2, 1);

-- Re-create Scores Table
CREATE TABLE `scores` (
  `ScoreID` int NOT NULL AUTO_INCREMENT,
  `PlayerID` int DEFAULT NULL,
  `Score` int NOT NULL,
  `Date` date NOT NULL,
  `TeeboxID` int DEFAULT NULL,
  PRIMARY KEY (`ScoreID`),
  KEY `fk_scores_players` (`PlayerID`),
  CONSTRAINT `fk_scores_players` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Re-create Teeboxes Table
CREATE TABLE `teeboxes` (
  `TeeboxID` int NOT NULL AUTO_INCREMENT,
  `TeeboxName` varchar(50) NOT NULL,
  `SlopeRating` int NOT NULL,
  `CourseRating` decimal(5,2) NOT NULL,
  `Par` int NOT NULL,
  PRIMARY KEY (`TeeboxID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert your Teeboxes
INSERT INTO `teeboxes` (TeeboxID, TeeboxName, SlopeRating, CourseRating, Par) VALUES
(1,'Blue, Front 9',63,34.80,35),
(2,'Blue, Back 9',63,34.80,36),
(3,'White, Front 9',59,33.30,35),
(4,'White, Back 9',59,33.30,36),
(5,'Silver, Front 9',57,32.90,35),
(6,'Silver, Back 9',57,32.90,36),
(7,'Gold, Front 9',55,32.50,35),
(8,'Gold, Back 9',55,32.50,36);
