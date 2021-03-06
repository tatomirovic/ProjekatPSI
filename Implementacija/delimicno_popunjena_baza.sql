CREATE DATABASE  IF NOT EXISTS `kavijardb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `kavijardb`;
-- MySQL dump 10.13  Distrib 8.0.18, for Win64 (x86_64)
--
-- Host: localhost    Database: kavijardb
-- ------------------------------------------------------
-- Server version	8.0.18

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
-- Table structure for table `army`
--

DROP TABLE IF EXISTS `army`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `army` (
  `idArmy` int(11) NOT NULL AUTO_INCREMENT,
  `idCityFrom` int(11) NOT NULL,
  `idCityTo` int(11) DEFAULT NULL,
  `status` char(1) NOT NULL,
  `timeToArrival` datetime DEFAULT NULL,
  `lakaPesadija` int(11) DEFAULT NULL,
  `teskaPesadija` int(11) DEFAULT NULL,
  `lakaKonjica` int(11) DEFAULT NULL,
  `teskaKonjica` int(11) DEFAULT NULL,
  `strelci` int(11) DEFAULT NULL,
  `samostrelci` int(11) DEFAULT NULL,
  `katapult` int(11) DEFAULT NULL,
  `trebuset` int(11) DEFAULT NULL,
  PRIMARY KEY (`idArmy`),
  KEY `FK_DESTINATION_idx` (`idCityTo`),
  KEY `FK_STATIONED_idx` (`idCityFrom`),
  CONSTRAINT `FK_DESTINATION` FOREIGN KEY (`idCityTo`) REFERENCES `city` (`idCity`),
  CONSTRAINT `FK_STATIONED` FOREIGN KEY (`idCityFrom`) REFERENCES `city` (`idCity`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `army`
--

LOCK TABLES `army` WRITE;
/*!40000 ALTER TABLE `army` DISABLE KEYS */;
INSERT INTO `army` VALUES (1,1,NULL,'G',NULL,0,0,0,0,0,0,0,0),(2,2,NULL,'G',NULL,0,0,0,0,0,0,0,0),(5,3,NULL,'G',NULL,620,300,0,0,0,0,0,0);
/*!40000 ALTER TABLE `army` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `building`
--

DROP TABLE IF EXISTS `building`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `building` (
  `idCity` int(11) NOT NULL,
  `type` char(2) NOT NULL,
  `status` char(1) NOT NULL,
  `level` int(11) NOT NULL,
  `finishTime` datetime NOT NULL,
  PRIMARY KEY (`idCity`,`type`),
  CONSTRAINT `idCity` FOREIGN KEY (`idCity`) REFERENCES `city` (`idCity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `building`
--

LOCK TABLES `building` WRITE;
/*!40000 ALTER TABLE `building` DISABLE KEYS */;
INSERT INTO `building` VALUES (1,'BK','A',0,'2020-06-01 23:53:29'),(1,'BO','A',0,'2020-05-31 01:14:08'),(1,'BP','A',0,'2020-05-31 12:04:34'),(1,'BS','A',0,'2020-05-31 01:14:08'),(1,'KL','A',0,'2020-06-01 21:29:29'),(1,'PI','A',0,'2020-06-01 21:26:49'),(1,'TH','A',2,'2020-06-01 21:28:49'),(1,'TS','A',1,'2020-06-01 21:29:59'),(1,'ZD','A',0,'2020-06-01 23:53:29'),(2,'BK','A',0,'2020-05-31 01:14:18'),(2,'BO','A',0,'2020-05-31 01:14:18'),(2,'BP','U',0,'2020-06-01 21:50:41'),(2,'BS','A',0,'2020-05-31 01:14:18'),(2,'KL','U',0,'2020-06-01 21:50:41'),(2,'PI','A',0,'2020-05-31 01:14:18'),(2,'TH','A',1,'2020-05-31 01:14:18'),(2,'TS','U',0,'2020-06-01 21:55:41'),(2,'ZD','U',0,'2020-06-01 21:50:41'),(3,'BK','A',1,'2020-05-31 21:16:18'),(3,'BO','A',2,'2020-05-31 22:34:44'),(3,'BP','A',3,'2020-06-01 20:30:05'),(3,'BS','A',1,'2020-05-31 21:16:16'),(3,'KL','A',2,'2020-06-01 20:17:53'),(3,'PI','A',1,'2020-05-31 20:59:41'),(3,'TH','A',3,'2020-06-01 17:20:59'),(3,'TS','A',4,'2020-06-01 20:27:45'),(3,'ZD','A',1,'2020-05-31 21:16:09');
/*!40000 ALTER TABLE `building` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chatmsg`
--

DROP TABLE IF EXISTS `chatmsg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chatmsg` (
  `idChat` int(11) NOT NULL AUTO_INCREMENT,
  `idSender` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `content` varchar(128) NOT NULL,
  PRIMARY KEY (`idChat`),
  KEY `idSender_idx` (`idSender`) /*!80000 INVISIBLE */,
  CONSTRAINT `FK_CHATSENDER` FOREIGN KEY (`idSender`) REFERENCES `user` (`idUser`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chatmsg`
--

LOCK TABLES `chatmsg` WRITE;
/*!40000 ALTER TABLE `chatmsg` DISABLE KEYS */;
INSERT INTO `chatmsg` VALUES (1,5,'2020-06-01 19:47:07','yo'),(2,4,'2020-06-01 19:47:16','whats up'),(3,4,'2020-06-01 19:47:20','nm'),(4,4,'2020-06-01 20:05:26','hhh');
/*!40000 ALTER TABLE `chatmsg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `city`
--

DROP TABLE IF EXISTS `city`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `city` (
  `idCity` int(11) NOT NULL AUTO_INCREMENT,
  `idOwner` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `xCoord` int(11) NOT NULL,
  `yCoord` int(11) NOT NULL,
  `population` float NOT NULL,
  `woodworkers` int(11) NOT NULL,
  `stoneworkers` int(11) NOT NULL,
  `civilians` int(11) NOT NULL,
  `gold` float NOT NULL,
  `wood` float NOT NULL,
  `stone` float NOT NULL,
  `lastUpdate` datetime NOT NULL,
  PRIMARY KEY (`idCity`),
  KEY `idOwner_idx` (`idOwner`),
  CONSTRAINT `FK_OWNER` FOREIGN KEY (`idOwner`) REFERENCES `user` (`idUser`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `city`
--

LOCK TABLES `city` WRITE;
/*!40000 ALTER TABLE `city` DISABLE KEYS */;
INSERT INTO `city` VALUES (1,2,'P1C',16,13,453.832,0,0,454,40.5684,16.8,9.6,'2020-06-01 21:26:38'),(2,3,'P2C',20,16,267.959,0,0,268,468.22,120,120,'2020-06-01 21:50:25'),(3,4,'P3C',14,13,21324.1,500,1000,19824,100000,25172.6,30269,'2020-06-01 21:50:41');
/*!40000 ALTER TABLE `city` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mailmsg`
--

DROP TABLE IF EXISTS `mailmsg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mailmsg` (
  `idMail` int(11) NOT NULL AUTO_INCREMENT,
  `idFrom` int(11) DEFAULT NULL,
  `idTo` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `content` varchar(4096) NOT NULL,
  `readFlag` bit(1) NOT NULL,
  PRIMARY KEY (`idMail`),
  KEY `idFrom_idx` (`idFrom`),
  KEY `idTo_idx` (`idTo`),
  CONSTRAINT `FK_RECIPIENT` FOREIGN KEY (`idTo`) REFERENCES `user` (`idUser`),
  CONSTRAINT `FK_SENDER` FOREIGN KEY (`idFrom`) REFERENCES `user` (`idUser`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mailmsg`
--

LOCK TABLES `mailmsg` WRITE;
/*!40000 ALTER TABLE `mailmsg` DISABLE KEYS */;
INSERT INTO `mailmsg` VALUES (3,4,2,'2020-06-01 19:09:37','Rezultat bitke izmedju napadača P3 i branioca P1 je\\n Igrač P3 je izgubio 0.9523809523809526 jedinica tipa Laka pešadija\\n Igrač P3 je izgubio 0.0 jedinica tipa Teška pešadija\\n Igrač P3 je izgubio 0.0 jedinica tipa Strelci\\n Igrač P3 je izgubio 0.0 jedinica tipa Samostrelci\\n Igrač P3 je izgubio 0.0 jedinica tipa Laka konjica\\n Igrač P3 je izgubio 0.0 jedinica tipa Teška konjica\\n Igrač P3 je izgubio 0.0 jedinica tipa Katapulti\\n Igrač P3 je izgubio 0.0 jedinica tipa Trebušeti\\n\\n\\n Igrač P1 je izgubio 0.9523809523809523 jedinica tipa Laka pešadija\\n Igrač P1 je izgubio 0.0 jedinica tipa Teška pešadija\\n Igrač P1 je izgubio 0.0 jedinica tipa Strelci\\n Igrač P1 je izgubio 0.0 jedinica tipa Samostrelci\\n Igrač P1 je izgubio 0.0 jedinica tipa Laka konjica\\n Igrač P1 je izgubio 0.0 jedinica tipa Teška konjica\\n Igrač P1 je izgubio 0.0 jedinica tipa Katapulti\\n Igrač P1 je izgubio 0.0 jedinica tipa Trebušeti',_binary '\0'),(6,4,2,'2020-06-01 21:13:03','Rezultat bitke izmedju napadača P3 i branioca P1 je\n Igrač P3 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P3 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P3 je izgubio 0 jedinica tipa Strelci\n Igrač P3 je izgubio 0 jedinica tipa Samostrelci\n Igrač P3 je izgubio 0 jedinica tipa Laka konjica\n Igrač P3 je izgubio 0 jedinica tipa Teška konjica\n Igrač P3 je izgubio 0 jedinica tipa Katapulti\n Igrač P3 je izgubio 0 jedinica tipa Trebušeti\n\n\n Igrač P1 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P1 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P1 je izgubio 0 jedinica tipa Strelci\n Igrač P1 je izgubio 0 jedinica tipa Samostrelci\n Igrač P1 je izgubio 0 jedinica tipa Laka konjica\n Igrač P1 je izgubio 0 jedinica tipa Teška konjica\n Igrač P1 je izgubio 0 jedinica tipa Katapulti\n Igrač P1 je izgubio 0 jedinica tipa Trebušeti',_binary '\0'),(7,4,2,'2020-06-01 21:14:23','Rezultat bitke izmedju napadača P3 i branioca P1 je\n Igrač P3 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P3 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P3 je izgubio 0 jedinica tipa Strelci\n Igrač P3 je izgubio 0 jedinica tipa Samostrelci\n Igrač P3 je izgubio 0 jedinica tipa Laka konjica\n Igrač P3 je izgubio 0 jedinica tipa Teška konjica\n Igrač P3 je izgubio 0 jedinica tipa Katapulti\n Igrač P3 je izgubio 0 jedinica tipa Trebušeti\n\n\n Igrač P1 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P1 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P1 je izgubio 0 jedinica tipa Strelci\n Igrač P1 je izgubio 0 jedinica tipa Samostrelci\n Igrač P1 je izgubio 0 jedinica tipa Laka konjica\n Igrač P1 je izgubio 0 jedinica tipa Teška konjica\n Igrač P1 je izgubio 0 jedinica tipa Katapulti\n Igrač P1 je izgubio 0 jedinica tipa Trebušeti',_binary '\0'),(8,4,2,'2020-06-01 21:29:29','Rezultat bitke izmedju napadača P3 i branioca P1 je\n Igrač P3 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P3 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P3 je izgubio 0 jedinica tipa Strelci\n Igrač P3 je izgubio 0 jedinica tipa Samostrelci\n Igrač P3 je izgubio 0 jedinica tipa Laka konjica\n Igrač P3 je izgubio 0 jedinica tipa Teška konjica\n Igrač P3 je izgubio 0 jedinica tipa Katapulti\n Igrač P3 je izgubio 0 jedinica tipa Trebušeti\n\n\n Igrač P1 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P1 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P1 je izgubio 0 jedinica tipa Strelci\n Igrač P1 je izgubio 0 jedinica tipa Samostrelci\n Igrač P1 je izgubio 0 jedinica tipa Laka konjica\n Igrač P1 je izgubio 0 jedinica tipa Teška konjica\n Igrač P1 je izgubio 0 jedinica tipa Katapulti\n Igrač P1 je izgubio 0 jedinica tipa Trebušeti\n\n Igrač P3 je osvojio 162.27360000000002 zlata, 67.2 drva i 38.400000000000006 kamena\n\nZgrada Kamenolom igrača P1 je oštećenaZgrada Trgovinska stanica igrača P1 je oštećenaZgrada Baraka za konjicu igrača P1 je oštećena',_binary '\0'),(9,4,3,'2020-06-01 21:40:00','sta ima',_binary '\0'),(10,4,3,'2020-06-01 21:50:41','Rezultat bitke izmedju napadača P3 i branioca P2 je\n Igrač P3 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P3 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P3 je izgubio 0 jedinica tipa Strelci\n Igrač P3 je izgubio 0 jedinica tipa Samostrelci\n Igrač P3 je izgubio 0 jedinica tipa Laka konjica\n Igrač P3 je izgubio 0 jedinica tipa Teška konjica\n Igrač P3 je izgubio 0 jedinica tipa Katapulti\n Igrač P3 je izgubio 0 jedinica tipa Trebušeti\n\n\n Igrač P2 je izgubio 0 jedinica tipa Laka pešadija\n Igrač P2 je izgubio 0 jedinica tipa Teška pešadija\n Igrač P2 je izgubio 0 jedinica tipa Strelci\n Igrač P2 je izgubio 0 jedinica tipa Samostrelci\n Igrač P2 je izgubio 0 jedinica tipa Laka konjica\n Igrač P2 je izgubio 0 jedinica tipa Teška konjica\n Igrač P2 je izgubio 0 jedinica tipa Katapulti\n Igrač P2 je izgubio 0 jedinica tipa Trebušeti\n\n Igrač P3 je osvojio 1872 zlata, 480 drva i 480 kamena\n\nZgrada Baraka za pešadiju igrača P2 je oštećena\nZgrada Kamenolom igrača P2 je oštećena\nZgrada Trgovinska stanica igrača P2 je oštećena\n',_binary '\0');
/*!40000 ALTER TABLE `mailmsg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade`
--

DROP TABLE IF EXISTS `trade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trade` (
  `idTrade` int(11) NOT NULL AUTO_INCREMENT,
  `idCity1` int(11) NOT NULL,
  `idCity2` int(11) NOT NULL,
  `status` char(1) NOT NULL,
  `gold1` int(11) NOT NULL,
  `wood1` int(11) NOT NULL,
  `stone1` int(11) NOT NULL,
  `gold2` int(11) NOT NULL,
  `wood2` int(11) NOT NULL,
  `stone2` int(11) NOT NULL,
  `timeToArrival` datetime DEFAULT NULL,
  PRIMARY KEY (`idTrade`),
  KEY `FK_SENDER_idx` (`idCity1`),
  KEY `FK_ACCEPTOR_idx` (`idCity2`),
  CONSTRAINT `FK_ACCEPTOR` FOREIGN KEY (`idCity2`) REFERENCES `city` (`idCity`),
  CONSTRAINT `FK_INITIATOR` FOREIGN KEY (`idCity1`) REFERENCES `city` (`idCity`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade`
--

LOCK TABLES `trade` WRITE;
/*!40000 ALTER TABLE `trade` DISABLE KEYS */;
/*!40000 ALTER TABLE `trade` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `idUser` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `password` varchar(10000) NOT NULL,
  `role` varchar(1) NOT NULL,
  `caviar` int(11) NOT NULL,
  `statusUpdate` int(11) NOT NULL,
  `dateUnban` datetime DEFAULT NULL,
  `dateCharLift` datetime DEFAULT NULL,
  PRIMARY KEY (`idUser`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (2,'P1','pbkdf2:sha256:150000$tkU2qP3w$6fe9b299e692da521e562b1d66a4a20c9a0d7a9870d17748c75de09fac826a7e','I',0,7,NULL,NULL),(3,'P2','pbkdf2:sha256:150000$K11cYxrY$a3feded33d89df16ccabcac99eccf8f68926b85caf14e46f3257acc4aba90a87','I',0,2,NULL,'2020-06-12 19:50:00'),(4,'P3','pbkdf2:sha256:150000$48oSBv5p$8d32834480543acec3f35370c1bbda743e2062b1094628020482eaeef536634b','I',0,0,NULL,NULL),(5,'root','pbkdf2:sha256:150000$fme8Xvsw$99e7d9641aab56ee0c315d901a87d77ee1ec3b77d075e5b7871705d89393fd7f','A',0,0,NULL,NULL),(6,'mod','pbkdf2:sha256:150000$ygUt2T9S$b3be4d28bb9ba25580e96c7877db95cef68133389eea93dc3f8fee3bdbd16f85','M',0,0,NULL,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-06-01 22:01:22
