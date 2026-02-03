-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: mysql-sih25-alokg252-af3a.g.aivencloud.com    Database: govt_db
-- ------------------------------------------------------
-- Server version	8.0.35

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '3e74b646-ead9-11f0-a8ba-8a981e3aa997:1-72,
84eb3392-eace-11f0-855d-16baf86b1665:1-15,
a5b69a49-e637-11f0-9978-02be3982aa71:1-15,
c6f28a1d-cb76-11f0-96f5-62150e2fafbc:1-379';

--
-- Current Database: `govt_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `govt_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `govt_db`;

--
-- Table structure for table `AtrocitySections`
--

DROP TABLE IF EXISTS `AtrocitySections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AtrocitySections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Section` varchar(255) NOT NULL,
  `OffenseDescription` text NOT NULL,
  `MinimumCompensation` decimal(12,2) NOT NULL,
  `PaymentStages` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AtrocitySections`
--

LOCK TABLES `AtrocitySections` WRITE;
/*!40000 ALTER TABLE `AtrocitySections` DISABLE KEYS */;
INSERT INTO `AtrocitySections` VALUES (1,'3(1) a','Forced ingestion of obnoxious substance',100000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(2,'3(1) b','Dumping excreta/filth in premises',85000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(3,'3(1) d','Parading naked/semi-naked',100000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(4,'3(1) e','Tonsuring/removing clothes/moustache',100000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(5,'3(1) g','Wrongful dispossession of land',150000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(6,'3(1) h','Forced/bonded labor',100000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(7,'3(1) i','Forcing carcass/grave disposal',100000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(8,'3(1) j','Manual scavenging',250000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(9,'3(1) k','Devadasi dedication',500000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(10,'3(1) o','Preventing voting',100000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(11,'3(1) r','Public caste insult/humiliation',100000.00,'25% FIR, 50% Charge Sheet, 25% Conviction'),(12,'3(2) Va','Acid attack',200000.00,'10% FIR, balance per stages'),(13,'3(2) v','Rape (IPC 376)',400000.00,'Varies by state/severity'),(14,'3(2) v','Gang Rape',500000.00,'Varies by state/severity'),(15,'3(2) v','Murder/Death',825000.00,'50% FIR/Post-mortem, 50% Charge Sheet'),(16,'3(2) v','Disability 100%',825000.00,'50% FIR, 50% Charge Sheet');
/*!40000 ALTER TABLE `AtrocitySections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `JudgementRecord`
--

DROP TABLE IF EXISTS `JudgementRecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `JudgementRecord` (
  `FIR_NO` varchar(50) NOT NULL,
  `Chargesheet_No` varchar(50) NOT NULL,
  `Chargesheet_Date` date DEFAULT NULL,
  `Judgement_ID` varchar(50) NOT NULL,
  `Judgement_No` varchar(50) DEFAULT NULL,
  `Judgment_Result` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`Judgement_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `JudgementRecord`
--

LOCK TABLES `JudgementRecord` WRITE;
/*!40000 ALTER TABLE `JudgementRecord` DISABLE KEYS */;
INSERT INTO `JudgementRecord` VALUES ('FIR/101/2025','CS/51/2025','2025-01-20','JID/001/2025','JUDG/001/2025','In-Favour'),('FIR/102/2025','CS/52/2025','2025-01-25','JID/002/2025','JUDG/002/2025','In-Favour'),('FIR/103/2025','CS/53/2025','2025-01-30','JID/003/2025','JUDG/003/2025','In-Favour'),('FIR/104/2025','CS/54/2025','2025-02-04','JID/004/2025','JUDG/004/2025','In-Favour'),('FIR/105/2025','CS/55/2025','2025-02-09','JID/005/2025','JUDG/005/2025','Not-In-Favour'),('FIR/106/2025','CS/56/2025','2025-02-14','JID/006/2025','JUDG/006/2025','Not-In-Favour'),('FIR/107/2025','CS/57/2025','2025-02-19','JID/007/2025','JUDG/007/2025','Not-In-Favour'),('FIR/108/2025','CS/58/2025','2025-02-24','JID/008/2025','JUDG/008/2025','Settlement'),('FIR/109/2025','CS/59/2025','2025-03-01','JID/009/2025','JUDG/009/2025','Settlement'),('FIR/110/2025','CS/60/2025','2025-03-06','JID/010/2025','JUDG/010/2025','Settlement'),('FIR-2025-002','CS-2025-0051','2025-01-20','JIDD-2025-00001','JUDG-2025-00001','In-Favour'),('FIR-2025-003','CS-2025-0052','2025-01-25','JIDD-2025-00002','JUDG-2025-00002','In-Favour'),('FIR-2025-004','CS-2025-0053','2025-01-30','JIDD-2025-00003','JUDG-2025-00003','In-Favour'),('FIR-2025-005','CS-2025-0054','2025-02-04','JIDD-2025-00004','JUDG-2025-00004','In-Favour'),('FIR-2025-006','CS-2025-0055','2025-02-09','JIDD-2025-00005','JUDG-2025-00005','Not-In-Favour'),('FIR-2025-007','CS-2025-0056','2025-02-14','JIDD-2025-00006','JUDG-2025-00006','Not-In-Favour'),('FIR-2025-008','CS-2025-0057','2025-02-19','JIDD-2025-00007','JUDG-2025-00007','Not-In-Favour'),('FIR-2025-009','CS-2025-0058','2025-02-24','JIDD-2025-00008','JUDG-2025-00008','Settlement'),('FIR-2025-0010','CS-2025-0059','2025-03-01','JIDD-2025-00009','JUDG-2025-00009','Settlement'),('FIR-2025-0011','CS-2025-0060','2025-03-06','JIDD-2025-00010','JUDG-2025-00010','Settlement');
/*!40000 ALTER TABLE `JudgementRecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `aadhaar_records`
--

DROP TABLE IF EXISTS `aadhaar_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `aadhaar_records` (
  `aadhaar_id` bigint NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `father_name` varchar(100) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `address_line1` varchar(150) DEFAULT NULL,
  `address_line2` varchar(150) DEFAULT NULL,
  `district` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `pincode` varchar(10) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `enrollment_date` date DEFAULT NULL,
  `last_update` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `mobile_verified` tinyint(1) DEFAULT NULL,
  `email_verified` tinyint(1) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`aadhaar_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aadhaar_records`
--

LOCK TABLES `aadhaar_records` WRITE;
/*!40000 ALTER TABLE `aadhaar_records` DISABLE KEYS */;
INSERT INTO `aadhaar_records` VALUES (112233445566,'Kavita Joshi','Mukesh Joshi','1984-07-27','Female','78 Hill View','Phase II','Dehradun','Uttarakhand','248001','9755501234','kavita@example.com','2013-09-03','2025-11-30 12:02:27',0,0,'inactive'),(123456781234,'Ramesh Kumar','Suresh Kumar','1989-04-10','Male','12 MG Road','Near Market','Pune','Maharashtra','411001','9876543210','ramesh@example.com','2017-03-21','2025-11-30 12:02:27',1,0,'active'),(234567892345,'Priya Singh','Mahesh Singh','1995-09-15','Female','22 Lake View','Sector 5','Lucknow','Uttar Pradesh','226001','9123456780','priya@example.com','2018-11-09','2025-11-30 12:02:27',1,1,'active'),(345678903456,'Amit Sharma','Vijay Sharma','1982-01-25','Male','7 Green Park','Block C','Jaipur','Rajasthan','302001','9988776655','amit@example.com','2016-01-10','2025-11-30 12:02:27',0,0,'inactive'),(456789014567,'Neha Patel','Kiran Patel','1990-12-05','Female','14 River Side','Floor 2','Ahmedabad','Gujarat','380001','9090909090','neha@example.com','2019-07-14','2025-11-30 12:02:27',1,1,'active'),(567890125678,'Arjun Verma','Raghav Verma','2000-06-22','Male','55 Civil Lines','Near Park','Delhi','Delhi','110001','9898989898','arjun@example.com','2020-02-18','2025-11-30 12:02:27',1,0,'active'),(678901236789,'Sunita Rao','Jagdeep Rao','1978-03-30','Female','89 Main Street','Opp Temple','Hyderabad','Telangana','500001','9700001111','sunita@example.com','2015-08-28','2025-11-30 12:02:27',1,1,'active'),(700100100101,'Ramesh Netam','Suresh Netam','1983-04-10','Male','Village Batro','Kondagaon','Kondagaon','Chhattisgarh','494226','9876543210','ramesh.netam@example.com','2017-03-21','2025-11-30 13:08:52',1,0,'active'),(700100100102,'Sanjay Netam','Ramesh Netam','2006-09-15','Male','Village Batro','Kondagaon','Kondagaon','Chhattisgarh','494226','9998887771','sanjay.netam@example.com','2019-11-09','2025-11-30 13:08:52',1,1,'active'),(700100100103,'Priya Dhruv','Mahesh Dhruv','1994-01-25','Female','Village Kohkameta','Narayanpur','Narayanpur','Chhattisgarh','494661','9123456780','priya.dhruv@example.com','2016-01-10','2025-11-30 13:08:52',1,1,'active'),(700100100104,'Anjali Markam','Rajesh Markam','1996-12-05','Female','Village Kohkameta','Narayanpur','Narayanpur','Chhattisgarh','494661','9090909090','anjali.markam@example.com','2019-07-14','2025-11-30 13:08:52',1,1,'active'),(700100100105,'Amit Poyam','Lakhiram Poyam','1989-06-22','Male','Village Barsoor','Dantewada','Dantewada','Chhattisgarh','494441','9898989898','amit.poyam@example.com','2020-02-18','2025-11-30 13:08:52',1,0,'active'),(700100100106,'Ravi Madiyam','Ganesh Madiyam','1991-03-30','Male','Village Barsoor','Dantewada','Dantewada','Chhattisgarh','494441','9700001111','ravi.madiyam@example.com','2015-08-28','2025-11-30 13:08:52',1,1,'active'),(700100100107,'Geeta Salam','Ramlal Salam','1987-02-18','Female','Village Kodenar','Kondagaon','Kondagaon','Chhattisgarh','494226','9800123456','geeta.salam@example.com','2014-12-01','2025-11-30 13:11:05',1,0,'active'),(700100100108,'Mukesh Uikey','Dhaniram Uikey','1984-07-27','Male','Village Kachnar','Narayanpur','Narayanpur','Chhattisgarh','494661','9755501234','mukesh.uikey@example.com','2013-09-03','2025-11-30 13:11:05',1,1,'active'),(700100100109,'Seema Poyam','Hariram Poyam','1998-05-22','Female','Village Barsoor','Dantewada','Dantewada','Chhattisgarh','494441','9823445566','seema.poyam@example.com','2020-05-18','2025-11-30 13:11:05',1,1,'active'),(700100100110,'Raju Markam','Suresh Markam','1992-11-12','Male','Village Kohkameta','Narayanpur','Narayanpur','Chhattisgarh','494661','9911223344','raju.markam@example.com','2018-03-09','2025-11-30 13:11:05',1,0,'active'),(700100100111,'Kamal Netam','Jagat Netam','1979-09-03','Male','Village Batro','Kondagaon','Kondagaon','Chhattisgarh','494226','9876512345','kamal.netam@example.com','2012-07-14','2025-11-30 13:11:05',1,1,'active'),(789012347890,'Mohit Khan','Salim Khan','1993-08-11','Male','44 Old City','Ward 3','Bhopal','Madhya Pradesh','462001','9301122334','mohit@example.com','2018-05-13','2025-11-30 12:02:27',0,1,'inactive'),(890123458901,'Anita Das','Ranjit Das','1987-02-18','Female','101 Garden Road','Near School','Kolkata','West Bengal','700001','9800123456','anita@example.com','2014-12-01','2025-11-30 12:02:27',1,0,'active'),(901234569012,'Rahul Nair','Suresh Nair','1991-10-09','Male','33 Beach Road','Flat 9A','Kochi','Kerala','682001','9600456123','rahul@example.com','2016-06-30','2025-11-30 12:02:27',1,1,'active');
/*!40000 ALTER TABLE `aadhaar_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `caste_certificates`
--

DROP TABLE IF EXISTS `caste_certificates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `caste_certificates` (
  `certificate_id` varchar(32) NOT NULL,
  `aadhaar_number` bigint NOT NULL,
  `person_name` varchar(150) DEFAULT NULL,
  `caste_category` varchar(32) DEFAULT NULL,
  `caste_name` varchar(100) DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `issuing_authority` varchar(150) DEFAULT NULL,
  `verification_date` date DEFAULT NULL,
  `certificate_status` varchar(32) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`certificate_id`),
  KEY `fk_caste_cert_aadhaar` (`aadhaar_number`),
  CONSTRAINT `fk_caste_cert_aadhaar` FOREIGN KEY (`aadhaar_number`) REFERENCES `aadhaar_records` (`aadhaar_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `caste_certificates`
--

LOCK TABLES `caste_certificates` WRITE;
/*!40000 ALTER TABLE `caste_certificates` DISABLE KEYS */;
INSERT INTO `caste_certificates` VALUES ('CASTE-2025-001',700100100101,'Ramesh Netam','ST','Gond','2020-01-12','SDM Kondagaon',NULL,NULL,NULL),('CASTE-2025-002',700100100102,'Sanjay Netam','ST','Gond','2019-03-18','SDM Narayanpur',NULL,NULL,NULL),('CASTE-2025-003',700100100103,'Priya Dhruv','SC','Dhruv','2021-07-25','SDM Dhamtari',NULL,NULL,NULL),('CASTE-2025-004',700100100104,'Anjali Markam','ST','Halba','2018-11-02','SDM Kanker',NULL,NULL,NULL),('CASTE-2025-005',700100100105,'Amit Poyam','ST','Gond','2017-05-14','SDM Bijapur',NULL,NULL,NULL),('CASTE-2025-006',700100100106,'Ravi Madiyam','ST','Madiyam','2016-09-19','SDM Bastar',NULL,NULL,NULL),('CASTE-2025-007',700100100107,'Geeta Salam','SC','Salam','2022-02-28','SDM Durg',NULL,NULL,NULL),('CASTE-2025-008',700100100108,'Mukesh Uikey','ST','Uikey','2020-12-07','SDM Balod',NULL,NULL,NULL),('CASTE-2025-009',700100100109,'Seema Poyam','ST','Gond','2023-01-10','SDM Keshkal',NULL,NULL,NULL),('CASTE-2025-010',700100100110,'Raju Markam','ST','Halba','2019-09-20','SDM Kondagaon',NULL,NULL,NULL),('CASTE-2025-011',700100100111,'Kamal Netam','ST','Gond','2021-03-15','SDM Jagdalpur',NULL,NULL,NULL),('CASTE-2025-012',112233445566,'Kavita Joshi','General','Joshi','2014-04-11','Tehsildar Dehradun',NULL,NULL,NULL),('CASTE-2025-013',123456781234,'Ramesh Kumar','OBC','Kurmi','2015-08-19','SDM Raipur',NULL,NULL,NULL),('CASTE-2025-014',234567892345,'Priya Singh','General','Singh','2017-02-27','Tehsildar Delhi',NULL,NULL,NULL),('CASTE-2025-015',345678903456,'Amit Sharma','General','Sharma','2018-06-30','Tehsildar Jaipur',NULL,NULL,NULL),('CASTE-2025-016',456789014567,'Neha Patel','OBC','Patel','2019-12-17','SDM Ahmedabad',NULL,NULL,NULL),('CASTE-2025-017',567890125678,'Arjun Verma','General','Verma','2021-04-05','SDM Lucknow',NULL,NULL,NULL),('CASTE-2025-018',678901236789,'Sunita Rao','General','Rao','2022-10-13','SDM Hyderabad',NULL,NULL,NULL),('CASTE-2025-019',789012347890,'Mohit Khan','OBC','Khan','2020-03-11','SDM Bhopal',NULL,NULL,NULL),('CASTE-2025-020',890123458901,'Anita Das','SC','Das','2018-11-07','SDM Kolkata',NULL,NULL,NULL),('CASTE-2025-021',901234569012,'Rahul Nair','OBC','Nair','2016-08-08','Tehsildar Kochi',NULL,NULL,NULL);
/*!40000 ALTER TABLE `caste_certificates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fir_records`
--

DROP TABLE IF EXISTS `fir_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fir_records` (
  `fir_no` varchar(50) NOT NULL,
  `police_station_code` varchar(50) DEFAULT NULL,
  `police_station_name` varchar(150) DEFAULT NULL,
  `district` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `filing_datetime` datetime DEFAULT NULL,
  `complainant_name` varchar(120) DEFAULT NULL,
  `complainant_age` int DEFAULT NULL,
  `complainant_gender` varchar(10) DEFAULT NULL,
  `complainant_address` varchar(200) DEFAULT NULL,
  `complainant_contact` varchar(20) DEFAULT NULL,
  `complainant_relation` varchar(50) DEFAULT NULL,
  `victim_name` varchar(120) DEFAULT NULL,
  `victim_age` int DEFAULT NULL,
  `victim_gender` varchar(10) DEFAULT NULL,
  `victim_address` varchar(200) DEFAULT NULL,
  `victim_contact` varchar(20) DEFAULT NULL,
  `accused_name` varchar(120) DEFAULT NULL,
  `accused_description` varchar(255) DEFAULT NULL,
  `incident_date` date DEFAULT NULL,
  `incident_time` time DEFAULT NULL,
  `incident_location` varchar(200) DEFAULT NULL,
  `incident_summary` text,
  `sections_invoked` varchar(200) DEFAULT NULL,
  `case_action` varchar(255) DEFAULT NULL,
  `investigating_officer` varchar(120) DEFAULT NULL,
  `case_status` varchar(50) DEFAULT NULL,
  `last_update` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`fir_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fir_records`
--

LOCK TABLES `fir_records` WRITE;
/*!40000 ALTER TABLE `fir_records` DISABLE KEYS */;
INSERT INTO `fir_records` VALUES ('FIR-2025-001','PS101','Kondagaon Rural Station','Kondagaon','Chhattisgarh','2025-01-12 10:30:00','Ramesh Netam',42,'Male','Village Batro, Kondagaon, Chhattisgarh','9876543210','Father','Sanjay Netam',19,'Male','Village Batro, Kondagaon, Chhattisgarh','N/A','Unknown','Wearing black shawl, approx 5ft6','2025-01-11','21:15:00','Near village marketplace','Reported snatching incident during weekly haat','3(1) r, 3(1) b','Theft','Officer Sahu','Under Investigation','2025-11-30 13:09:36'),('FIR-2025-002','PS202','Narayanpur Rural Station','Narayanpur','Chhattisgarh','2025-02-03 15:45:00','Priya Dhruv',30,'Female','Village Kohkameta, Narayanpur, Chhattisgarh','9123456780','Neighbour','Anjali Markam',28,'Female','Village Kohkameta, Narayanpur, Chhattisgarh','N/A','Rohit Salam','Known local dispute, approx 5ft9','2025-02-02','19:30:00','Kohkameta school grounds','Physical altercation after land boundary argument','3(1) d, 3(1) e, 3(1) g','Assault, Insult','Officer P. Uike','Registered','2025-11-30 13:09:36'),('FIR-2025-003','PS303','Dantewada Rural Station','Dantewada','Chhattisgarh','2025-03-08 11:00:00','Amit Poyam',36,'Male','Village Barsoor, Dantewada, Chhattisgarh','9988776655','Friend','Ravi Madiyam',34,'Male','Village Barsoor, Dantewada, Chhattisgarh','N/A','Unknown','Two individuals on motorcycle seen fleeing towards forest road','2025-03-07','20:10:00','Barsoor main road','Robbery attempt near evening haat area','3(2) v','Robbery','Officer Hemla','Under Investigation','2025-11-30 13:09:36'),('FIR-2025-004','PS404','Kodenar Rural Station','Kondagaon','Chhattisgarh','2025-04-02 09:20:00','Geeta Salam',38,'Female','Village Kodenar, Kondagaon, Chhattisgarh','9800123456','Mother','Sunil Salam',14,'Male','Village Kodenar, Kondagaon, Chhattisgarh','N/A','Unknown','Suspect seen near forest boundary','2025-04-01','18:40:00','Kodenar forest path','Minor missing case reported after boy did not return from gathering firewood','IPC 363','Kidnapping','Officer Rituraj','Under Investigation','2025-11-30 13:11:05'),('FIR-2025-005','PS505','Kachnar Rural Station','Narayanpur','Chhattisgarh','2025-04-18 17:55:00','Mukesh Uikey',41,'Male','Village Kachnar, Narayanpur, Chhattisgarh','9755501234','Brother','Suresh Uikey',35,'Male','Village Kachnar, Narayanpur, Chhattisgarh','N/A','Unknown','Footprints found near farmland','2025-04-18','06:30:00','Kachnar farmlands','Crop damage and suspected trespass during early morning hours','IPC 447','Trespass','Officer S. Markam','Registered','2025-11-30 13:11:05'),('FIR-2025-006','PS606','Barsoor Rural Station','Dantewada','Chhattisgarh','2025-05-12 14:15:00','Seema Poyam',27,'Female','Village Barsoor, Dantewada, Chhattisgarh','9823445566','Sister','Harish Poyam',22,'Male','Village Barsoor, Dantewada, Chhattisgarh','N/A','Two Unknown Persons','Seen fleeing on motorcycle','2025-05-11','20:05:00','Barsoor bridge area','Attempted robbery near river crossing at dusk','3(1) o, 3(1) k','Attempt Robbery','Officer Devangan','Under Investigation','2025-11-30 13:11:05'),('FIR-2025-007','PS202','Narayanpur Rural Station','Narayanpur','Chhattisgarh','2025-06-01 08:40:00','Raju Markam',32,'Male','Village Kohkameta, Narayanpur, Chhattisgarh','9911223344','Husband','Mina Markam',29,'Female','Village Kohkameta, Narayanpur, Chhattisgarh','N/A','Unknown','Suspect left bicycle near incident site','2025-05-31','22:00:00','Kohkameta main chowk','Harassment complaint filed following repeated disturbances at residence','IPC 354','Molestation','Officer L. Poyam','Registered','2025-11-30 13:11:05'),('FIR-2025-008','PS101','Kondagaon Rural Station','Kondagaon','Chhattisgarh','2025-06-15 19:10:00','Kamal Netam',45,'Male','Village Batro, Kondagaon, Chhattisgarh','9876512345','Uncle','Ritu Netam',17,'Female','Village Batro, Kondagaon, Chhattisgarh','N/A','Unknown','Footprints and broken bangles found near site','2025-06-14','20:55:00','Batro village outskirts','Missing person report after teenager did not return from friend’s house','IPC 363','Kidnapping','Officer T. Salam','Under Investigation','2025-11-30 13:11:05');
/*!40000 ALTER TABLE `fir_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `npci_bank_kyc`
--

DROP TABLE IF EXISTS `npci_bank_kyc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `npci_bank_kyc` (
  `kyc_id` varchar(32) NOT NULL,
  `account_number` varchar(32) NOT NULL,
  `account_type` varchar(20) NOT NULL,
  `primary_holder_name` varchar(150) NOT NULL,
  `primary_aadhaar` bigint NOT NULL,
  `primary_caste_category` varchar(20) DEFAULT NULL,
  `secondary_holder_name` varchar(150) NOT NULL,
  `secondary_aadhaar` bigint NOT NULL,
  `secondary_caste_category` varchar(20) DEFAULT NULL,
  `bank_name` varchar(150) DEFAULT NULL,
  `ifsc_code` varchar(20) DEFAULT NULL,
  `kyc_status` varchar(20) DEFAULT NULL,
  `kyc_completed_on` date DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`kyc_id`),
  KEY `fk_npci_primary_aadhaar` (`primary_aadhaar`),
  KEY `fk_npci_secondary_aadhaar` (`secondary_aadhaar`),
  CONSTRAINT `fk_npci_primary_aadhaar` FOREIGN KEY (`primary_aadhaar`) REFERENCES `aadhaar_records` (`aadhaar_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_npci_secondary_aadhaar` FOREIGN KEY (`secondary_aadhaar`) REFERENCES `aadhaar_records` (`aadhaar_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `npci_bank_kyc`
--

LOCK TABLES `npci_bank_kyc` WRITE;
/*!40000 ALTER TABLE `npci_bank_kyc` DISABLE KEYS */;
INSERT INTO `npci_bank_kyc` VALUES ('KYC-2025-001','550010000001','JOINT','Priya Dhruv',700100100103,'SC','Amit Sharma',345678903456,'General','State Bank of India','SBIN0001234','verified','2023-11-18','e-KYC OK'),('KYC-2025-002','550010000002','JOINT','Anjali Markam',700100100104,'ST','Arjun Verma',567890125678,'General','Bank of Baroda','BARB0RAIPUR','verified','2024-02-10','Linked to Aadhaar'),('KYC-2025-003','550010000003','JOINT','Amit Poyam',700100100105,'ST','Neha Patel',456789014567,'OBC','HDFC Bank','HDFC0004567','pending',NULL,'Secondary holder pending'),('KYC-2025-004','550010000004','JOINT','Geeta Salam',700100100107,'SC','Priya Singh',234567892345,'General','Central Bank of India','CBIN0287654','verified','2022-09-22','Biometric passed'),('KYC-2025-005','550010000005','JOINT','Raju Markam',700100100110,'ST','Ramesh Kumar',123456781234,'OBC','Punjab National Bank','PUNB0456100','rejected','2020-10-01','Address mismatch'),('KYC-2025-006','550010000006','JOINT','Kamal Netam',700100100111,'ST','Anita Das',890123458901,'SC','ICICI Bank','ICIC0005678','verified','2024-01-12','Both holders verified');
/*!40000 ALTER TABLE `npci_bank_kyc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'govt_db'
--

--
-- Dumping routines for database 'govt_db'
--

--
-- Current Database: `defaultdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `defaultdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `defaultdb`;

--
-- Table structure for table `ATROCITY`
--

DROP TABLE IF EXISTS `ATROCITY`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ATROCITY` (
  `Case_No` int NOT NULL AUTO_INCREMENT,
  `FIR_NO` varchar(50) DEFAULT NULL,
  `Victim_Name` varchar(150) NOT NULL,
  `Father_Name` varchar(150) NOT NULL,
  `Victim_DOB` date DEFAULT NULL,
  `Gender` varchar(10) DEFAULT NULL,
  `Victim_Mobile_No` varchar(15) NOT NULL,
  `Aadhar_No` bigint DEFAULT NULL,
  `Caste` varchar(50) DEFAULT NULL,
  `Caste_Certificate_No` varchar(100) DEFAULT NULL,
  `Applied_Acts` varchar(500) DEFAULT NULL,
  `Case_Description` varchar(500) DEFAULT NULL,
  `Victim_Image_No` varchar(100) DEFAULT NULL,
  `Location` varchar(200) DEFAULT NULL,
  `Date_of_Incident` date DEFAULT NULL,
  `Medical_Report_Image` varchar(100) DEFAULT NULL,
  `Passbook_Image` varchar(100) DEFAULT NULL,
  `Bank_Account_No` varchar(20) NOT NULL,
  `IFSC_Code` varchar(20) DEFAULT NULL,
  `Holder_Name` varchar(100) DEFAULT NULL,
  `Stage` int DEFAULT '0',
  `Fund_Type` varchar(100) DEFAULT NULL,
  `Fund_Ammount` varchar(50) DEFAULT NULL,
  `Pending_At` varchar(100) DEFAULT NULL,
  `Approved_By` varchar(100) DEFAULT NULL,
  `Limit_Delayed` int DEFAULT NULL,
  `Reason_for_Delay` varchar(300) DEFAULT NULL,
  `Applicant_Name` varchar(150) NOT NULL,
  `Applicant_Relation` varchar(100) DEFAULT NULL,
  `Applicant_Mobile_No` varchar(15) NOT NULL,
  `Applicant_Email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `Bank_Name` varchar(255) DEFAULT 'state bank of india',
  `State_UT` varchar(100) DEFAULT NULL,
  `District` varchar(100) DEFAULT NULL,
  `Vishesh_P_S_Name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Case_No`),
  UNIQUE KEY `FIR_NO` (`FIR_NO`),
  UNIQUE KEY `Aadhar_No` (`Aadhar_No`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ATROCITY`
--

LOCK TABLES `ATROCITY` WRITE;
/*!40000 ALTER TABLE `ATROCITY` DISABLE KEYS */;
INSERT INTO `ATROCITY` VALUES (33,'FIR-2025-004','Sunil Salam','Ramlal Salam','1987-02-18','female','9800123456',700100100107,'obc','FIRFIR-2025-004_user_CASTE.jpeg','3(1) i, 3(1) h','Minor missing case reported after boy did not return from gathering firewood','FIRFIR-2025-004_user_PHOTO.jpeg','Kodenar forest path','2025-04-01','FIRFIR-2025-004_user_MEDICAL.jpeg','','3243242','werere','werewr',7,NULL,'200000.0','','user',NULL,NULL,'Geeta Salam',NULL,'9800123456',NULL,'2025-12-09 13:42:25','state bank of india','chhattisgarh','durg','Ajak'),(35,'FIR-2025-002','Anjali Markam','Rajesh Markam','1996-12-05','female','9090909090',700100100104,'CASTE-2025-004','FIRFIR-2025-002_user_CASTE.pdf','3(1) d, 3(1) e, 3(1) g','Physical altercation after land boundary argument','FIRFIR-2025-002_user_PHOTO.png','Kohkameta school grounds','2025-02-02','','','2343432','2343243','afed',7,NULL,'350000.0','','user',NULL,NULL,'Priya Dhruv',NULL,'9123456780',NULL,'2026-01-22 13:31:11','state bank of india','chhattisgarh','durg','Ajak'),(36,'FIR-2025-003','Ravi Madiyam','Ganesh Madiyam','1991-03-30','male','9700001111',700100100106,'st','FIRFIR-2025-003_user_CASTE.png','3(2) v','Robbery attempt near evening haat area','FIRFIR-2025-003_user_PHOTO.png','Barsoor main road','2025-03-07','','','2343432','aefd','34324234',0,NULL,'825000.0',NULL,NULL,NULL,NULL,'Amit Poyam',NULL,'9988776655',NULL,'2026-01-23 11:43:49','state bank of india','chhattisgarh','durg','Ajak'),(37,'FIR-2025-001','Sanjay Netam','Ramesh Netam','2006-09-15','male','9998887771',700100100102,'SC','FIRFIR-2025-001_user_CASTE.png','3(1) r, 3(1) b','Reported snatching incident during weekly haat','FIRFIR-2025-001_user_PHOTO.jpeg','Near village marketplace','2025-01-11','','','984938893888','SBIN0000838','ANY NAME',7,NULL,'185009.0','','user',NULL,NULL,'Ramesh Netam',NULL,'9876543210',NULL,'2026-01-23 13:41:56','state bank of india','chhattisgarh','durg','Ajak');
/*!40000 ALTER TABLE `ATROCITY` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AtrocityReliefRules`
--

DROP TABLE IF EXISTS `AtrocityReliefRules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AtrocityReliefRules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Offence_Section` varchar(50) NOT NULL,
  `One_Word_Description` varchar(100) NOT NULL,
  `Monetary_Aid_INR` decimal(10,2) NOT NULL,
  `Acts_Rules` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AtrocityReliefRules`
--

LOCK TABLES `AtrocityReliefRules` WRITE;
/*!40000 ALTER TABLE `AtrocityReliefRules` DISABLE KEYS */;
INSERT INTO `AtrocityReliefRules` VALUES (1,'Sec 3(2)(v) with Sec 376 IPC','Gang Rape',825000.00,'PoA Act, PoA Rules (Annexure I)'),(2,'Sec 3(2)(v) with Sec 376 IPC','Rape',400000.00,'PoA Act, PoA Rules (Annexure I)'),(3,'Sec 3(2)(v) with Sec 302 IPC','Murder / Death',825000.00,'PoA Act, PoA Rules (Annexure I)'),(4,'Sec 3(2)(va) with Sec 326A/B IPC','Acid Attack',200000.00,'PoA Act, PoA Rules (Annexure I)'),(5,'Sec 3(2)(v) with Permanent Disability','Disability (100%)',825000.00,'PoA Act, PoA Rules (Annexure I)'),(6,'Sec 3(1)(a)','Forced Ingestion',100000.00,'PoA Act, PoA Rules (Annexure I)'),(7,'Sec 3(1)(b)','Filth Dumping',100000.00,'PoA Act, PoA Rules (Annexure I)'),(8,'Sec 3(1)(d)','Forced Nakedness / Garland',200000.00,'PoA Act, PoA Rules (Annexure I)'),(9,'Sec 3(1)(e)','Tonsuring / Face Painting',200000.00,'PoA Act, PoA Rules (Annexure I)'),(10,'Sec 3(1)(r) / 3(1)(s)','Caste Insult (Public)',100000.00,'PoA Act, PoA Rules (Annexure I)'),(11,'Sec 3(1)(i) / 3(1)(j)','Manual Scavenging / Carcass',200000.00,'PoA Act, PoA Rules (Annexure I)'),(12,'Sec 3(1)(k)','Devadasi / Dedication',400000.00,'PoA Act, PoA Rules (Annexure I)'),(13,'Sec 3(1)(g)','Forced Labour / Begar',120000.00,'PoA Act, PoA Rules (Annexure I)'),(14,'Sec 3(1)(f)','Land Seizure / Wrongful',120000.00,'PoA Act, PoA Rules (Annexure I)'),(15,'Sec 3(1)(q)','Property Destruction (Fire)',100000.00,'PoA Act, PoA Rules (Annexure I)'),(16,'Sec 3(1)(o)','Water Contamination',250000.00,'PoA Act, PoA Rules (Annexure I)'),(17,'Sec 3(2)(v) with Simple Hurt IPC','Simple Hurt / Assault',85000.00,'PoA Act, PoA Rules (Annexure I)'),(18,'Sec 3(2)(v) with Grievous Hurt IPC','Grievous Hurt',125000.00,'PoA Act, PoA Rules (Annexure I)'),(19,'Offences under PCR Act, 1955','Untouchability Enforcement',0.00,'PCR Act, PoA Rules, Centrally Sponsored Scheme');
/*!40000 ALTER TABLE `AtrocityReliefRules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CASE_EVENTS`
--

DROP TABLE IF EXISTS `CASE_EVENTS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CASE_EVENTS` (
  `event_id` bigint NOT NULL AUTO_INCREMENT,
  `case_no` int NOT NULL,
  `performed_by` varchar(150) NOT NULL,
  `performed_by_role` varchar(80) NOT NULL,
  `event_type` varchar(80) NOT NULL,
  `event_data` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`event_id`),
  KEY `idx_case_events_case_no_created_at` (`case_no`,`created_at`),
  CONSTRAINT `CASE_EVENTS_ibfk_1` FOREIGN KEY (`case_no`) REFERENCES `ATROCITY` (`Case_No`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CASE_EVENTS`
--

LOCK TABLES `CASE_EVENTS` WRITE;
/*!40000 ALTER TABLE `CASE_EVENTS` DISABLE KEYS */;
INSERT INTO `CASE_EVENTS` VALUES (42,33,'user','Investigation Officer','APPROVED','{\"comment\": null, \"next_stage\": 1}','2025-12-09 14:02:43'),(46,33,'user','Special Officer','SPECIAL_OFFICER_APPROVED','{\"comment\": null, \"fund_type\": \"Allowance Fund\", \"next_stage\": 2, \"fund_amount\": 200000.0}','2026-01-22 12:49:42'),(47,33,'user','PFMS Officer','PFMS_FIRST_TRANCHE','{\"amount\": 50000.0, \"txn_id\": \"234\", \"fund_type\": null, \"tranche_label\": \"First Tranche (25%)\", \"percent_of_total\": 25.0, \"bank_acknowledgement\": null}','2026-01-22 12:54:46'),(48,33,'user','Investigation Officer','CHARGESHEET_SUBMITTED','{\"severity\": \"Moderate\", \"court_name\": \"mycourt\", \"chargesheet_no\": \"123\", \"chargesheet_date\": \"2026-01-07\"}','2026-01-22 12:58:36'),(49,33,'user','PFMS Officer','PFMS_SECOND_TRANCHE','{\"amount\": 100000.0, \"txn_id\": \"321\", \"fund_type\": null, \"tranche_label\": \"Second Tranche (25-50%)\", \"percent_of_total\": 50.0, \"bank_acknowledgement\": null}','2026-01-22 12:59:55'),(50,33,'user','District Collector/DM/SJO','DM_JUDGMENT_RECORDED','{\"notes\": null, \"verdict\": \"Convicted\", \"judgment_ref\": \"256\", \"judgment_date\": \"2026-01-07\"}','2026-01-22 13:00:50'),(51,33,'user','PFMS Officer','PFMS_FINAL_TRANCHE','{\"amount\": 70000.0, \"txn_id\": \"354\", \"fund_type\": null, \"tranche_label\": \"Final Tranche\", \"percent_of_total\": 35.0, \"bank_acknowledgement\": null}','2026-01-22 13:01:58'),(52,35,'user','Investigation Officer','FIR_SUBMITTED','{\"comment\": \"FIR submitted by Investigation Officer\", \"is_draft\": false}','2026-01-22 13:31:15'),(53,35,'user','Investigation Officer','FIR_SUBMITTED','{\"comment\": null, \"next_stage\": 1}','2026-01-22 13:32:35'),(54,35,'user','Special Officer','SPECIAL_OFFICER_APPROVED','{\"comment\": null, \"fund_type\": \"Allowance Fund\", \"next_stage\": 2, \"fund_amount\": 350000.0}','2026-01-22 15:45:40'),(55,35,'user','PFMS Officer','PFMS_FIRST_TRANCHE','{\"amount\": 100000.0, \"txn_id\": \"123\", \"fund_type\": null, \"tranche_label\": \"First Tranche (25%)\", \"percent_of_total\": 28.57, \"bank_acknowledgement\": null}','2026-01-22 15:49:58'),(56,35,'user','Investigation Officer','CHARGESHEET_SUBMITTED','{\"severity\": null, \"court_name\": \"2345\", \"chargesheet_no\": \"234\", \"chargesheet_date\": \"2026-01-22\"}','2026-01-22 15:51:42'),(57,35,'user','PFMS Officer','PFMS_SECOND_TRANCHE','{\"amount\": 200000.0, \"txn_id\": \"315\", \"fund_type\": null, \"tranche_label\": \"Second Tranche (25-50%)\", \"percent_of_total\": 57.14, \"bank_acknowledgement\": null}','2026-01-22 15:54:25'),(58,35,'user','District Collector/DM/SJO','DM_JUDGMENT_RECORDED','{\"notes\": null, \"verdict\": \"Not Guilty\", \"judgment_ref\": \"123\", \"judgment_date\": \"2026-01-22\"}','2026-01-22 15:55:36'),(59,35,'user','PFMS Officer','PFMS_FINAL_TRANCHE','{\"amount\": 90000.0, \"txn_id\": \"246\", \"fund_type\": \"Medical Expenses\", \"tranche_label\": \"Final Tranche\", \"percent_of_total\": 25.71, \"bank_acknowledgement\": \"47\"}','2026-01-22 15:57:45'),(60,36,'user','Investigation Officer','FIR_SUBMITTED','{\"comment\": \"FIR submitted by Investigation Officer\", \"is_draft\": false}','2026-01-23 11:43:54'),(61,37,'user','Investigation Officer','FIR_SUBMITTED','{\"comment\": \"FIR submitted by Investigation Officer\", \"is_draft\": false}','2026-01-23 13:41:59'),(62,37,'user','Investigation Officer','FIR_SUBMITTED','{\"comment\": null, \"next_stage\": 1}','2026-01-23 13:42:17'),(63,37,'user','Special Officer','SPECIAL_OFFICER_APPROVED','{\"comment\": \"EDIT\", \"fund_type\": \"Allowance Fund\", \"next_stage\": 2, \"fund_amount\": 185009.0}','2026-01-23 13:43:22'),(64,37,'user','PFMS Officer','PFMS_FIRST_TRANCHE','{\"amount\": 46252.25, \"txn_id\": \"PFMS000446\", \"fund_type\": null, \"tranche_label\": \"First Tranche (25%)\", \"percent_of_total\": 25.0, \"bank_acknowledgement\": null}','2026-01-23 13:45:21'),(65,37,'user','Investigation Officer','CHARGESHEET_SUBMITTED','{\"severity\": \"Moderate\", \"court_name\": \"FDFG\", \"chargesheet_no\": \"CS-25-123\", \"chargesheet_date\": \"2026-01-15\"}','2026-01-23 13:47:00'),(66,37,'user','PFMS Officer','PFMS_SECOND_TRANCHE','{\"amount\": 92504.5, \"txn_id\": \"PFMS000446\", \"fund_type\": null, \"tranche_label\": \"Second Tranche (25-50%)\", \"percent_of_total\": 50.0, \"bank_acknowledgement\": null}','2026-01-23 13:47:38'),(67,37,'user','District Collector/DM/SJO','DM_JUDGMENT_RECORDED','{\"notes\": null, \"verdict\": \"Guilty\", \"judgment_ref\": \"CJ-25-123\", \"judgment_date\": \"2026-01-01\"}','2026-01-23 13:48:49'),(68,37,'user','PFMS Officer','PFMS_FINAL_TRANCHE','{\"amount\": 46252.25, \"txn_id\": \"PFMS000446\", \"fund_type\": null, \"tranche_label\": \"Final Tranche\", \"percent_of_total\": 25.0, \"bank_acknowledgement\": null}','2026-01-23 13:49:38');
/*!40000 ALTER TABLE `CASE_EVENTS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compensation_rules`
--

DROP TABLE IF EXISTS `compensation_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compensation_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_id` int NOT NULL,
  `section_code` varchar(64) NOT NULL,
  `action_name` varchar(255) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compensation_rules`
--

LOCK TABLES `compensation_rules` WRITE;
/*!40000 ALTER TABLE `compensation_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `compensation_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `icm_applications`
--

DROP TABLE IF EXISTS `icm_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `icm_applications` (
  `icm_id` int NOT NULL AUTO_INCREMENT,
  `citizen_id` int NOT NULL,
  `applicant_aadhaar` bigint NOT NULL,
  `groom_name` varchar(150) NOT NULL,
  `groom_age` int DEFAULT NULL,
  `groom_father_name` varchar(150) NOT NULL,
  `groom_pre_address` varchar(255) NOT NULL,
  `groom_current_address` varchar(255) NOT NULL,
  `groom_permanent_address` varchar(255) NOT NULL,
  `groom_aadhaar` bigint NOT NULL,
  `groom_caste_cert_id` varchar(32) DEFAULT NULL,
  `groom_dob` date NOT NULL,
  `groom_education` varchar(255) DEFAULT NULL,
  `groom_training` varchar(255) DEFAULT NULL,
  `groom_income` varchar(50) DEFAULT NULL,
  `groom_livelihood` varchar(255) DEFAULT NULL,
  `groom_future_plan` varchar(255) DEFAULT NULL,
  `groom_first_marriage` tinyint DEFAULT '1',
  `bride_name` varchar(150) NOT NULL,
  `bride_age` int DEFAULT NULL,
  `bride_father_name` varchar(150) NOT NULL,
  `bride_pre_address` varchar(255) NOT NULL,
  `bride_current_address` varchar(255) NOT NULL,
  `bride_permanent_address` varchar(255) NOT NULL,
  `bride_aadhaar` bigint NOT NULL,
  `bride_caste_cert_id` varchar(32) DEFAULT NULL,
  `bride_dob` date NOT NULL,
  `bride_education` varchar(255) DEFAULT NULL,
  `bride_training` varchar(255) DEFAULT NULL,
  `bride_income` varchar(50) DEFAULT NULL,
  `bride_livelihood` varchar(255) DEFAULT NULL,
  `bride_future_plan` varchar(255) DEFAULT NULL,
  `bride_first_marriage` tinyint DEFAULT '1',
  `marriage_date` date NOT NULL,
  `marriage_cert_number` varchar(100) DEFAULT NULL,
  `marriage_cert_file` varchar(255) DEFAULT NULL,
  `previous_benefit_taken` tinyint DEFAULT '0',
  `joint_photo_file` varchar(255) DEFAULT NULL,
  `groom_signature_file` varchar(255) DEFAULT NULL,
  `bride_signature_file` varchar(255) DEFAULT NULL,
  `witness_aadhaar` bigint DEFAULT NULL,
  `witness_name` varchar(150) DEFAULT NULL,
  `witness_address` varchar(255) DEFAULT NULL,
  `witness_signature_file` varchar(255) DEFAULT NULL,
  `witness_verified` tinyint DEFAULT '0',
  `joint_account_number` varchar(32) DEFAULT NULL,
  `joint_ifsc` varchar(20) DEFAULT NULL,
  `joint_passbook_file` varchar(255) DEFAULT NULL,
  `state_ut` varchar(100) DEFAULT NULL,
  `district` varchar(100) DEFAULT NULL,
  `current_stage` int DEFAULT '0',
  `pending_at` varchar(50) DEFAULT 'ADM',
  `application_status` varchar(50) DEFAULT 'Pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`icm_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `icm_applications`
--

LOCK TABLES `icm_applications` WRITE;
/*!40000 ALTER TABLE `icm_applications` DISABLE KEYS */;
INSERT INTO `icm_applications` VALUES (2,12,700100100104,'Arjun Verma',25,'Raghav Verma','','delhi','',567890125678,'CASTE-2025-017','2000-06-22',NULL,NULL,NULL,NULL,NULL,1,'Anjali Markam',29,'Rajesh Markam','','durg','',700100100104,'CASTE-2025-004','1996-12-05',NULL,NULL,NULL,NULL,NULL,1,'2025-12-03','3t6t773',NULL,0,NULL,'ICM2_citizen_12_GROOM_SIGN.jpeg','ICM2_citizen_12_BRIDE_SIGN.jpeg',212311231231,NULL,NULL,NULL,0,'550010000002','BARB0RAIPUR',NULL,'chhattisgarh','durg',5,'COMPLETED','Completed','2025-12-06 09:46:10','2025-12-08 12:49:18'),(3,9,890123458901,'Kamal Netam',46,'Jagat Netam','','durg cg','',700100100111,'CASTE-2025-011','1979-09-03',NULL,NULL,NULL,NULL,NULL,1,'Anita Das',38,'Ranjit Das','','durg cg','',890123458901,'CASTE-2025-020','1987-02-18',NULL,NULL,NULL,NULL,NULL,1,'2025-12-09','MC-123',NULL,0,NULL,'ICM3_citizen_9_GROOM_SIGN.png','ICM3_citizen_9_BRIDE_SIGN.png',212311231231,NULL,NULL,NULL,0,'550010000006','ICIC0005678',NULL,'chhattisgarh','durg',0,'Tribal Officer','Pending','2025-12-08 06:26:11','2026-01-07 20:51:41');
/*!40000 ALTER TABLE `icm_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `icm_events`
--

DROP TABLE IF EXISTS `icm_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `icm_events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `icm_id` int NOT NULL,
  `event_type` varchar(100) NOT NULL,
  `event_role` varchar(50) NOT NULL,
  `event_stage` int NOT NULL,
  `comment` text,
  `event_data` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`event_id`),
  KEY `fk_icm_events` (`icm_id`),
  CONSTRAINT `fk_icm_events` FOREIGN KEY (`icm_id`) REFERENCES `icm_applications` (`icm_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `icm_events`
--

LOCK TABLES `icm_events` WRITE;
/*!40000 ALTER TABLE `icm_events` DISABLE KEYS */;
INSERT INTO `icm_events` VALUES (1,2,'APPLICATION_SUBMITTED','Citizen',0,'Application submitted by citizen','{\"files\": [\"groom_signature_file\", \"bride_signature_file\"], \"action\": \"submitted\", \"bride_aadhaar\": 700100100104, \"groom_aadhaar\": 567890125678, \"applicant_aadhaar\": 700100100104}','2025-12-06 09:46:13'),(2,2,'TO_CORRECTION','Tribal Officer',0,'test correction','{\"role\": \"Tribal Officer\", \"actor\": \"user\", \"comment\": \"test correction\", \"corrections_required\": [\"correct something\"], \"stage_before_correction\": 0}','2025-12-07 14:58:42'),(3,3,'APPLICATION_SUBMITTED','Citizen',0,'Application submitted by citizen','{\"files\": [\"groom_signature_file\", \"bride_signature_file\"], \"action\": \"submitted\", \"bride_aadhaar\": 890123458901, \"groom_aadhaar\": 700100100111, \"applicant_aadhaar\": 890123458901}','2025-12-08 06:26:13'),(4,2,'TO_APPROVED','Tribal Officer',0,'Application approved','{\"role\": \"Tribal Officer\", \"actor\": \"user\", \"comment\": \"Application approved\", \"new_stage\": 1, \"previous_stage\": 0}','2025-12-08 06:30:23'),(5,2,'DM_APPROVED','District Collector/DM/SJO',1,'form approved','{\"role\": \"District Collector/DM/SJO\", \"actor\": \"user\", \"comment\": \"form approved\", \"new_stage\": 2, \"previous_stage\": 1}','2025-12-08 06:38:14'),(6,2,'SNO_APPROVED','State Nodal Officer',2,'approved for release','{\"role\": \"State Nodal Officer\", \"actor\": \"user\", \"comment\": \"approved for release\", \"new_stage\": 3, \"previous_stage\": 2}','2025-12-08 06:39:54'),(7,2,'PFMS_FUND_RELEASED','PFMS Officer',3,'Fund released: Rs. 250000, TxnID: ts-123567','{\"role\": \"PFMS Officer\", \"actor\": \"user\", \"amount\": 250000, \"txn_id\": \"ts-123567\", \"bank_ref\": null, \"grant_amount\": 250000}','2025-12-08 12:49:18');
/*!40000 ALTER TABLE `icm_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pending_alerts`
--

DROP TABLE IF EXISTS `pending_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pending_alerts` (
  `alert_id` int NOT NULL AUTO_INCREMENT,
  `case_no` int NOT NULL,
  `junior_role` varchar(100) NOT NULL,
  `senior_role` varchar(100) NOT NULL,
  `alerted_at` datetime NOT NULL,
  `pending_duration` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `senior_input` text,
  `junior_reason` text,
  `ticket_close_date` datetime DEFAULT NULL,
  PRIMARY KEY (`alert_id`),
  KEY `case_no` (`case_no`),
  KEY `senior_role` (`senior_role`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pending_alerts`
--

LOCK TABLES `pending_alerts` WRITE;
/*!40000 ALTER TABLE `pending_alerts` DISABLE KEYS */;
INSERT INTO `pending_alerts` VALUES (1,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-07 19:39:55',1,0,'Explain the delay of 5 days for this case.',NULL,'2025-12-09 02:03:32'),(2,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 02:03:36',5,0,'kgjjyhvjh',NULL,'2025-12-09 02:42:57'),(3,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 02:43:05',5,0,'mh v mhv\n',NULL,'2025-12-09 02:52:58'),(4,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 02:53:05',5,0,'.mknljb',NULL,'2025-12-09 02:56:32'),(5,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 02:56:35',5,0,'why are you not active on this case',NULL,'2025-12-09 03:14:36'),(6,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 03:14:44',5,0,'why are you not active on this case',NULL,'2025-12-09 03:16:19'),(7,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 03:16:24',5,0,'why are you not active in this case',NULL,'2025-12-09 03:25:04'),(8,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 03:25:09',5,0,'why are you not active on this case',NULL,'2025-12-09 03:28:22'),(9,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 03:28:30',5,0,'MHVJMHVMHV',NULL,'2025-12-09 04:25:02'),(10,29,'District Collector/DM/SJO','State Nodal Officer','2025-12-09 04:25:10',5,1,NULL,NULL,NULL);
/*!40000 ALTER TABLE `pending_alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `treasury`
--

DROP TABLE IF EXISTS `treasury`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `treasury` (
  `id` int NOT NULL AUTO_INCREMENT,
  `transaction_id` varchar(32) DEFAULT NULL,
  `case_id` varchar(32) DEFAULT NULL,
  `case_type` enum('ATROCITY','ICM') DEFAULT NULL,
  `amount` decimal(12,2) NOT NULL,
  `transaction_type` enum('CREDIT','DEBIT') NOT NULL,
  `balance_after` decimal(12,2) NOT NULL,
  `initiated_by` varchar(64) DEFAULT NULL,
  `state` varchar(40) NOT NULL,
  `district` varchar(40) NOT NULL,
  `remark` text,
  `transaction_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_case` (`case_id`,`case_type`),
  KEY `idx_time` (`transaction_time`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treasury`
--

LOCK TABLES `treasury` WRITE;
/*!40000 ALTER TABLE `treasury` DISABLE KEYS */;
INSERT INTO `treasury` VALUES (1,'ts-001',NULL,NULL,800000.00,'CREDIT',800000.00,NULL,'Chhattisgarh','Durg','amount credited by SNO','2025-12-08 19:42:04');
/*!40000 ALTER TABLE `treasury` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'defaultdb'
--

--
-- Dumping routines for database 'defaultdb'
--

--
-- Current Database: `Login_Credentials`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `Login_Credentials` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `Login_Credentials`;

--
-- Table structure for table `District_lvl_Officers`
--

DROP TABLE IF EXISTS `District_lvl_Officers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `District_lvl_Officers` (
  `LOGIN_ID` varchar(255) NOT NULL,
  `PASSWORD` varchar(255) NOT NULL,
  `ROLE` varchar(50) NOT NULL,
  `STATE_UT` varchar(100) NOT NULL,
  `DISTRICT` varchar(100) NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_login_id_role` (`LOGIN_ID`,`ROLE`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `District_lvl_Officers`
--

LOCK TABLES `District_lvl_Officers` WRITE;
/*!40000 ALTER TABLE `District_lvl_Officers` DISABLE KEYS */;
INSERT INTO `District_lvl_Officers` VALUES ('user','$2b$12$o/E.wYYf2eWhNU./P6GDUe44WCF/ok7aMAzBWm7/d1vftFxMuWj/m','District Collector/DM/SJO','chhattisgarh','durg',1),('user','$2b$12$2QCEPciikcnhas0Ttu2G/u9XG4Ij3S4v8ou8/MnLlqZqktbAJnFPK','Tribal Officer','chhattisgarh','durg',3),('user','$2b$12$ipp1L.Iz4rRvPjgcu7OatuNIUpfdO6Jv6fMWxEgBj/IEjXpixciKm','PFMS Officer','chhattisgarh','durg',4),('user','$2b$12$57sWQKyshzocGomI0fKj4Ofes2EoBTa./RYUI5HxpB.e1MedDYvwy','Nodal Officer','','',5),('user','$2b$12$57sWQKyshzocGomI0fKj4Ofes2EoBTa./RYUI5HxpB.e1MedDYvwy','Special Officer','chhattisgarh','durg',6);
/*!40000 ALTER TABLE `District_lvl_Officers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `State_Nodal_Officers`
--

DROP TABLE IF EXISTS `State_Nodal_Officers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `State_Nodal_Officers` (
  `LOGIN_ID` varchar(255) NOT NULL,
  `PASSWORD` varchar(255) NOT NULL,
  `ROLE` varchar(50) NOT NULL,
  `STATE_UT` varchar(100) NOT NULL,
  PRIMARY KEY (`LOGIN_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `State_Nodal_Officers`
--

LOCK TABLES `State_Nodal_Officers` WRITE;
/*!40000 ALTER TABLE `State_Nodal_Officers` DISABLE KEYS */;
INSERT INTO `State_Nodal_Officers` VALUES ('st','$2b$12$74yJMOIXEAj0QtGJZDq/hONMOcYPqYWT0bi4cm3HticrcorWrjdF.','State Nodal Officer','Chhattishgarh'),('try','try','State Nodal Officer','haryana'),('try1','try1','State Nodal Officer','Chhattishgarh'),('try12345','$2b$12$tn4P3Z.TIuGRdnri63KaS.oVCaVutOJPyeympoFE7JGFCLLjB2MJy','State Nodal Officer','Chhattishgarh'),('user','$2b$12$H75iGkbiINz7e5WzJUI7des3HULhx6XTkX5TFRereZyBOAQ5ParRO','State Nodal Officer','chhattisgarh');
/*!40000 ALTER TABLE `State_Nodal_Officers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Vishesh_Thana_Officers`
--

DROP TABLE IF EXISTS `Vishesh_Thana_Officers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Vishesh_Thana_Officers` (
  `LOGIN_ID` varchar(255) NOT NULL,
  `PASSWORD` varchar(255) NOT NULL,
  `ROLE` varchar(50) NOT NULL,
  `STATE_UT` varchar(100) NOT NULL,
  `DISTRICT` varchar(100) NOT NULL,
  `VISHESH_P_S_NAME` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`LOGIN_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Vishesh_Thana_Officers`
--

LOCK TABLES `Vishesh_Thana_Officers` WRITE;
/*!40000 ALTER TABLE `Vishesh_Thana_Officers` DISABLE KEYS */;
INSERT INTO `Vishesh_Thana_Officers` VALUES ('try1','try1','Investigation Officer','Chhattishgarh','Durg','Ajak'),('try12345','$2b$12$c5NtNGf6a1l9m3Gt4HNp4.03z49hL5n60fMp/zqGDV4hUYz4Bm6VO','Investigation Officer','Chhattishgarh','Durg','Ajak'),('user','$2b$12$NO6cang4G0PKQeO0QSzaz.H36pM77oqcvyhK2hsVylSEXtRgWdH0K','Investigation Officer','chhattisgarh','durg','Ajak'),('vt','$2b$12$445wGdqRk9Bh9/z3YnVax.S0skTcOzpUiyVgloNbul3uZq2.HkrRm','Investigation Officer','Chhattishgarh','Durg','Ajak');
/*!40000 ALTER TABLE `Vishesh_Thana_Officers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `citizen_users`
--

DROP TABLE IF EXISTS `citizen_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `citizen_users` (
  `citizen_id` int NOT NULL AUTO_INCREMENT,
  `login_id` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `aadhaar_number` bigint NOT NULL,
  `caste_certificate_id` varchar(32) DEFAULT NULL,
  `full_name` varchar(150) NOT NULL,
  `mobile_number` varchar(15) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `state_ut` varchar(50) DEFAULT NULL,
  `district` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`citizen_id`),
  UNIQUE KEY `login_id` (`login_id`),
  UNIQUE KEY `aadhaar_number` (`aadhaar_number`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `citizen_users`
--

LOCK TABLES `citizen_users` WRITE;
/*!40000 ALTER TABLE `citizen_users` DISABLE KEYS */;
INSERT INTO `citizen_users` VALUES (1,'kavita.joshi','$2b$12$WP6yfcjArKqG4afquLfaPuXOH0dV20wN415FPLpjFRrg8/4TxTiL.',112233445566,'CASTE-001','Kavita Joshi','9755501234','kavita.joshi@example.com','2025-12-05 06:04:24','2025-12-07 14:51:37','Dehradun','Uttarakhand'),(2,'ramesh.kumar','$2b$12$E.s6biSajtglLc.vo52QoOcQTYazF19eVQlpcrKPsWt8pezaZ0N2.',123456781234,'CASTE-2025-013','Ramesh Kumar','9876543210','ramesh.kumar@example.com','2025-12-05 06:04:24','2025-12-08 06:04:03','Chhattisgarh','raipur'),(3,'priya.singh','$2b$12$d23PB6EhmRd92zaEEtnA7.7EjSokz1roTDcE6fk541Lxew8Vq4r7m',234567892345,'CASTE-003','Priya Singh','9123456780','priya.singh@example.com','2025-12-05 06:04:24','2025-12-05 06:30:34',NULL,NULL),(4,'amit.sharma','$2b$12$0fDy2GVp9zTmJqwT2occt.heEurDkdcfSBHXL5OW4ErvK316gQeU2',345678903456,'CASTE-004','Amit Sharma','9822334455','amit.sharma@example.com','2025-12-05 06:04:24','2025-12-05 06:30:37',NULL,NULL),(5,'neha.patel','$2b$12$DuzB43O3xcEl8rFbmwrNweamDzby9dlfBjrnXutxBq0.SMgqWTHLS',456789014567,'CASTE-005','Neha Patel','9988776655','neha.patel@example.com','2025-12-05 06:04:24','2025-12-05 06:30:38',NULL,NULL),(6,'arjun.verma','$2b$12$EjNR9x78yKYr5y6o4euo2O64LTi0EDZDD.5fVErknIECHsO07Ozee',567890125678,'CASTE-006','Arjun Verma','9345612789','arjun.verma@example.com','2025-12-05 06:04:24','2025-12-05 06:30:40',NULL,NULL),(7,'sunita.rao','$2b$12$igaraF70S9ZVW2Hl.Xtxt.4g6Cr7uYFbOKkNAi8fmRpJr.K6/uFA.',678901236789,'CASTE-007','Sunita Rao','9871203456','sunita.rao@example.com','2025-12-05 06:04:24','2025-12-05 06:30:41',NULL,NULL),(8,'ramesh.netam','$2b$12$.X3h8.gD9Z9u3QZJ6gLyh.z0dnf3oYeZ9GXzwwQmnY45RBSjwYGEy',700100100101,'CASTE-2025-001','Ramesh Netam','9900112233','ramesh.netam@example.com','2025-12-05 06:04:24','2025-12-05 08:45:56',NULL,NULL),(9,'anita.das','$2b$12$TO3Q6UhRfE4//DxuDk4FPOEGLzujNY01ZXSfLZKs38BNr0hPJ76u2',890123458901,'CASTE-009','Anita Das','9812345600','anita.das@example.com','2025-12-05 06:04:24','2025-12-08 06:04:03','Chhattisgarh','Durg'),(10,'rahul.nair','$2b$12$sCMesYGMAihRPoF.E71x8uw/WOqlNM1Tj0RQtXPCimA3O06J8X/uu',901234569012,'CASTE-010','Rahul Nair','9080706050','rahul.nair@example.com','2025-12-05 06:04:24','2025-12-05 06:30:45',NULL,NULL),(11,'harsh.poyam','$2b$12$0fDy2GVp9zTmJqwT2occt.heEurDkdcfSBHXL5OW4ErvK316gQeU2',700100100109,'CASTE-2025-002','Harsh Poyam','9822001100','harsh.poyam@example.com','2025-12-05 08:40:26','2025-12-09 13:28:18',NULL,NULL),(12,'anjali.markam','$2b$12$WP6yfcjArKqG4afquLfaPuXOH0dV20wN415FPLpjFRrg8/4TxTiL.',700100100104,'CASTE-2025-004','Anjali Markam','9876605500','anjali.markam@example.com','2025-12-05 08:40:26','2025-12-07 14:51:37','Chhattisgarh','Durg');
/*!40000 ALTER TABLE `citizen_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'Login_Credentials'
--

--
-- Dumping routines for database 'Login_Credentials'
--
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-03 15:38:40
