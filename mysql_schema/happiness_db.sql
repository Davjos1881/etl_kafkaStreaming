CREATE DATABASE  IF NOT EXISTS `happiness_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `happiness_db`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: happiness_db
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dim_country`
--

DROP TABLE IF EXISTS `dim_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_country` (
  `country_id` int NOT NULL AUTO_INCREMENT,
  `country` varchar(100) NOT NULL,
  `region` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`country_id`),
  UNIQUE KEY `country` (`country`)
) ENGINE=InnoDB AUTO_INCREMENT=165 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dim_date`
--

DROP TABLE IF EXISTS `dim_date`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_date` (
  `date_id` int NOT NULL AUTO_INCREMENT,
  `year` int NOT NULL,
  PRIMARY KEY (`date_id`),
  UNIQUE KEY `year` (`year`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dim_raw_event`
--

DROP TABLE IF EXISTS `dim_raw_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dim_raw_event` (
  `dim_raw_event_id` int NOT NULL AUTO_INCREMENT,
  `raw_event_id` int NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `received_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`dim_raw_event_id`),
  UNIQUE KEY `raw_event_id` (`raw_event_id`),
  CONSTRAINT `dim_raw_event_ibfk_1` FOREIGN KEY (`raw_event_id`) REFERENCES `raw_happiness_events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=783 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fact_predictions`
--

DROP TABLE IF EXISTS `fact_predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fact_predictions` (
  `prediction_id` int NOT NULL AUTO_INCREMENT,
  `raw_event_id` int DEFAULT NULL,
  `country_id` int DEFAULT NULL,
  `date_id` int DEFAULT NULL,
  `actual_score` float DEFAULT NULL,
  `predicted_score` float DEFAULT NULL,
  `prediction_error` float DEFAULT NULL,
  `prediction_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`prediction_id`),
  KEY `raw_event_id` (`raw_event_id`),
  KEY `country_id` (`country_id`),
  KEY `date_id` (`date_id`),
  CONSTRAINT `fact_predictions_ibfk_1` FOREIGN KEY (`raw_event_id`) REFERENCES `raw_happiness_events` (`id`),
  CONSTRAINT `fact_predictions_ibfk_2` FOREIGN KEY (`country_id`) REFERENCES `dim_country` (`country_id`),
  CONSTRAINT `fact_predictions_ibfk_3` FOREIGN KEY (`date_id`) REFERENCES `dim_date` (`date_id`)
) ENGINE=InnoDB AUTO_INCREMENT=783 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `raw_happiness_events`
--

DROP TABLE IF EXISTS `raw_happiness_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_happiness_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `country` varchar(100) DEFAULT NULL,
  `region` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `gdp` float DEFAULT NULL,
  `family` float DEFAULT NULL,
  `health` float DEFAULT NULL,
  `freedom` float DEFAULT NULL,
  `generosity` float DEFAULT NULL,
  `trust` float DEFAULT NULL,
  `actual_score` float DEFAULT NULL,
  `status` varchar(20) DEFAULT 'VALID',
  `received_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=783 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-13 19:19:56
