-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema kavijardb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema kavijardb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `kavijardb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `kavijardb` ;

-- -----------------------------------------------------
-- Table `kavijardb`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`user` (
  `idUser` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(30) NOT NULL,
  `password` VARCHAR(10000) NOT NULL,
  `role` VARCHAR(1) NOT NULL,
  `caviar` INT(11) NOT NULL,
  `statusUpdate` INT(11) NOT NULL,
  `dateUnban` DATETIME NULL DEFAULT NULL,
  `dateCharLift` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`idUser`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `kavijardb`.`city`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`city` (
  `idCity` INT(11) NOT NULL AUTO_INCREMENT,
  `idOwner` INT(11) NOT NULL,
  `name` VARCHAR(30) NOT NULL,
  `xCoord` INT(11) NOT NULL,
  `yCoord` INT(11) NOT NULL,
  `population` float NOT NULL,
  `woodworkers` INT(11) NOT NULL,
  `stoneworkers` INT(11) NOT NULL,
  `civilians` INT(11) NOT NULL,
  `gold` float NOT NULL,
  `wood` float NOT NULL,
  `stone` float NOT NULL,
  `lastUpdate` datetime NOT NULL,
  PRIMARY KEY (`idCity`),
  INDEX `idOwner_idx` (`idOwner` ASC) VISIBLE,
  CONSTRAINT `FK_OWNER`
    FOREIGN KEY (`idOwner`)
    REFERENCES `kavijardb`.`user` (`idUser`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `kavijardb`.`army`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`army` (
  `idArmy` INT(11) NOT NULL AUTO_INCREMENT,
  `idCityFrom` INT(11) NOT NULL,
  `idCityTo` INT(11) NULL DEFAULT NULL,
  `status` CHAR(1) NOT NULL,
  `timeToArrival` DATETIME NULL DEFAULT NULL,
  `lakaPesadija` INT(11) NULL DEFAULT NULL,
  `teskaPesadija` INT(11) NULL DEFAULT NULL,
  `lakaKonjica` INT(11) NULL DEFAULT NULL,
  `teskaKonjica` INT(11) NULL DEFAULT NULL,
  `strelci` INT(11) NULL DEFAULT NULL,
  `samostrelci` INT(11) NULL DEFAULT NULL,
  `katapult` INT(11) NULL DEFAULT NULL,
  `trebuset` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`idArmy`),
  INDEX `FK_DESTINATION_idx` (`idCityTo` ASC) VISIBLE,
  INDEX `FK_STATIONED_idx` (`idCityFrom` ASC) VISIBLE,
  CONSTRAINT `FK_DESTINATION`
    FOREIGN KEY (`idCityTo`)
    REFERENCES `kavijardb`.`city` (`idCity`),
  CONSTRAINT `FK_STATIONED`
    FOREIGN KEY (`idCityFrom`)
    REFERENCES `kavijardb`.`city` (`idCity`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `kavijardb`.`building`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`building` (
  `idCity` INT(11) NOT NULL,
  `type` CHAR(2) NOT NULL,
  `status` CHAR(1) NOT NULL,
  `level` INT(11) NOT NULL,
  `finishTime` DATETIME NOT NULL,
  PRIMARY KEY (`idCity`, `type`),
  CONSTRAINT `idCity`
    FOREIGN KEY (`idCity`)
    REFERENCES `kavijardb`.`city` (`idCity`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `kavijardb`.`chatmsg`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`chatmsg` (
  `idChat` INT(11) NOT NULL AUTO_INCREMENT,
  `idSender` INT(11) NOT NULL,
  `time` DATETIME NOT NULL,
  `content` VARCHAR(128) NOT NULL,
  PRIMARY KEY (`idChat`),
  INDEX `idSender_idx` (`idSender` ASC) INVISIBLE,
  CONSTRAINT `FK_CHATSENDER`
    FOREIGN KEY (`idSender`)
    REFERENCES `kavijardb`.`user` (`idUser`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `kavijardb`.`mailmsg`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`mailmsg` (
  `idMail` INT(11) NOT NULL AUTO_INCREMENT,
  `idFrom` INT(11),
  `idTo` INT(11) NOT NULL,
  `time` DATETIME NOT NULL,
  `content` VARCHAR(256) NOT NULL,
  `readFlag` BIT(1) NOT NULL,
  PRIMARY KEY (`idMail`),
  INDEX `idFrom_idx` (`idFrom` ASC) VISIBLE,
  INDEX `idTo_idx` (`idTo` ASC) VISIBLE,
  CONSTRAINT `FK_RECIPIENT`
    FOREIGN KEY (`idTo`)
    REFERENCES `kavijardb`.`user` (`idUser`),
  CONSTRAINT `FK_SENDER`
    FOREIGN KEY (`idFrom`)
    REFERENCES `kavijardb`.`user` (`idUser`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `kavijardb`.`recruiting`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`recruiting` (
  `idRecruiting` INT(11) NOT NULL AUTO_INCREMENT,
  `idCity` INT(11) NOT NULL,
  `type` CHAR(1) NOT NULL,
  `finishTime` DATETIME NOT NULL,
  `lowTier` INT(11) NULL DEFAULT NULL,
  `highTier` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`idRecruiting`),
  INDEX `idCity_idx` (`idCity` ASC) VISIBLE,
  CONSTRAINT `FK_FORCITY`
    FOREIGN KEY (`idCity`)
    REFERENCES `kavijardb`.`city` (`idCity`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `kavijardb`.`trade`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `kavijardb`.`trade` (
  `idTrade` INT(11) NOT NULL AUTO_INCREMENT,
  `idCity1` INT(11) NOT NULL,
  `idCity2` INT(11) NOT NULL,
  `status` CHAR(1) NOT NULL,
  `gold1` INT(11) NOT NULL,
  `wood1` INT(11) NOT NULL,
  `stone1` INT(11) NOT NULL,
  `gold2` INT(11) NOT NULL,
  `wood2` INT(11) NOT NULL,
  `stone2` INT(11) NOT NULL,
  `timeToArrival` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`idTrade`),
  INDEX `FK_SENDER_idx` (`idCity1` ASC) VISIBLE,
  INDEX `FK_ACCEPTOR_idx` (`idCity2` ASC) VISIBLE,
  CONSTRAINT `FK_ACCEPTOR`
    FOREIGN KEY (`idCity2`)
    REFERENCES `kavijardb`.`city` (`idCity`),
  CONSTRAINT `FK_INITIATOR`
    FOREIGN KEY (`idCity1`)
    REFERENCES `kavijardb`.`city` (`idCity`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
