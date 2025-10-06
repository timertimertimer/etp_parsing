-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: etp_parsing
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `addresses`
--

DROP TABLE IF EXISTS `addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addresses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `region_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `region_id` (`region_id`),
  CONSTRAINT `addresses_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auctions`
--

DROP TABLE IF EXISTS `auctions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auctions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ext_id` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `number` varchar(255) DEFAULT NULL,
  `type` enum('auction','competition','offer','pdo','rfp','tender','reduction') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `form` enum('open','closed') NOT NULL,
  `message_number` varchar(255) DEFAULT NULL,
  `organizer_id` int DEFAULT NULL,
  `arbitrator_id` int DEFAULT NULL,
  `debtor_id` int DEFAULT NULL,
  `trading_floor_id` int NOT NULL,
  `legal_case_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `property_type` enum('bankruptcy','arrested','commercial','legal_entities','fz44','capital_repair','fz223','rent','gis') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`),
  KEY `arbitrator_id` (`arbitrator_id`),
  KEY `debtor_id` (`debtor_id`),
  KEY `legal_case_id` (`legal_case_id`),
  KEY `organizer_id` (`organizer_id`),
  KEY `trading_floor_id` (`trading_floor_id`),
  CONSTRAINT `auctions_ibfk_1` FOREIGN KEY (`arbitrator_id`) REFERENCES `counterparties` (`id`),
  CONSTRAINT `auctions_ibfk_2` FOREIGN KEY (`debtor_id`) REFERENCES `counterparties` (`id`),
  CONSTRAINT `auctions_ibfk_3` FOREIGN KEY (`legal_case_id`) REFERENCES `legal_cases` (`id`),
  CONSTRAINT `auctions_ibfk_4` FOREIGN KEY (`organizer_id`) REFERENCES `counterparties` (`id`),
  CONSTRAINT `auctions_ibfk_5` FOREIGN KEY (`trading_floor_id`) REFERENCES `trading_floors` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cities`
--

DROP TABLE IF EXISTS `cities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `region_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `region_id` (`region_id`),
  CONSTRAINT `cities_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `counterparties`
--

DROP TABLE IF EXISTS `counterparties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `counterparties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inn` varchar(12) DEFAULT NULL,
  `kpp` varchar(9) DEFAULT NULL,
  `snils` varchar(11) DEFAULT NULL,
  `ogrn` varchar(13) DEFAULT NULL,
  `ogrnip` varchar(15) DEFAULT NULL,
  `okopf` varchar(5) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `short_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `fedresurs_url` varchar(255) DEFAULT NULL,
  `type` enum('individual','legal_entity') DEFAULT NULL,
  `address_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inn` (`inn`),
  KEY `address_id` (`address_id`),
  CONSTRAINT `counterparties_ibfk_1` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `counterparty_sro`
--

DROP TABLE IF EXISTS `counterparty_sro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `counterparty_sro` (
  `counterparty_id` int NOT NULL,
  `sro_id` int NOT NULL,
  `message_number` varchar(255) DEFAULT NULL,
  `activity_type` text,
  `entered_at` datetime DEFAULT NULL,
  PRIMARY KEY (`counterparty_id`,`sro_id`),
  KEY `sro_id` (`sro_id`),
  CONSTRAINT `counterparty_sro_ibfk_1` FOREIGN KEY (`counterparty_id`) REFERENCES `counterparties` (`id`),
  CONSTRAINT `counterparty_sro_ibfk_2` FOREIGN KEY (`sro_id`) REFERENCES `counterparties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `debtor_messages`
--

DROP TABLE IF EXISTS `debtor_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `debtor_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `content` mediumtext,
  `fedresurs_url` varchar(255) DEFAULT NULL,
  `published_at` datetime NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `debtor_id` int NOT NULL,
  `legal_case_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`),
  KEY `debtor_id` (`debtor_id`),
  KEY `legal_case_id` (`legal_case_id`),
  CONSTRAINT `debtor_messages_ibfk_1` FOREIGN KEY (`debtor_id`) REFERENCES `counterparties` (`id`),
  CONSTRAINT `debtor_messages_ibfk_2` FOREIGN KEY (`legal_case_id`) REFERENCES `legal_cases` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `files`
--

DROP TABLE IF EXISTS `files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `files` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `path` varchar(255) DEFAULT NULL,
  `url` text,
  `model_type` enum('Auction','Lot','DebtorMessage','LegalCase') NOT NULL,
  `model_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_image` tinyint(1) NOT NULL,
  `is_image_from_archive` tinyint(1) NOT NULL,
  `order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_model_type_model_id` (`model_type`,`model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `legal_cases`
--

DROP TABLE IF EXISTS `legal_cases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legal_cases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` varchar(255) NOT NULL,
  `status` varchar(255) DEFAULT NULL,
  `court_name` varchar(255) DEFAULT NULL,
  `fedresurs_url` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `debtor_category` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lot_categories`
--

DROP TABLE IF EXISTS `lot_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lot_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(7) NOT NULL,
  `lot_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lot_categories_ibfk_1` (`lot_id`),
  CONSTRAINT `lot_categories_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `lots` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lot_periods`
--

DROP TABLE IF EXISTS `lot_periods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lot_periods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `request_start_at` datetime NOT NULL,
  `request_end_at` datetime DEFAULT NULL,
  `trading_start_at` datetime DEFAULT NULL,
  `trading_end_at` datetime DEFAULT NULL,
  `price` float NOT NULL,
  `lot_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `lot_periods_ibfk_1` (`lot_id`),
  CONSTRAINT `lot_periods_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `lots` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lots`
--

DROP TABLE IF EXISTS `lots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lots` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ext_id` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `number` int NOT NULL,
  `name` text,
  `info` text,
  `property_info` text,
  `price_start` float DEFAULT NULL,
  `price_step` float DEFAULT NULL,
  `auction_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `lots_ibfk_1` (`auction_id`),
  CONSTRAINT `lots_ibfk_1` FOREIGN KEY (`auction_id`) REFERENCES `auctions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `parsers_status`
--

DROP TABLE IF EXISTS `parsers_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parsers_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `trading_floor_id` int NOT NULL,
  `status` enum('active','disabled','archived') NOT NULL,
  `counter` int NOT NULL,
  `duration` float NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `trading_floor_id` (`trading_floor_id`),
  CONSTRAINT `parsers_status_ibfk_1` FOREIGN KEY (`trading_floor_id`) REFERENCES `trading_floors` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `regions`
--

DROP TABLE IF EXISTS `regions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `regions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `oktmo` int NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oktmo` (`oktmo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trading_floors`
--

DROP TABLE IF EXISTS `trading_floors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trading_floors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `counterparty_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('active','disabled','archived') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `counterparty_id` (`counterparty_id`),
  CONSTRAINT `trading_floors_ibfk_1` FOREIGN KEY (`counterparty_id`) REFERENCES `counterparties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'etp_parsing'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-23 23:20:33
