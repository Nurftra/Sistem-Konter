-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Dec 05, 2025 at 08:10 AM
-- Server version: 8.4.3
-- PHP Version: 8.3.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `konter_hp_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('fa56c2000b41');

-- --------------------------------------------------------

--
-- Table structure for table `produk`
--

CREATE TABLE `produk` (
  `id` int NOT NULL,
  `nama` varchar(128) NOT NULL,
  `harga` int NOT NULL,
  `stok` int NOT NULL,
  `kategori` varchar(64) DEFAULT NULL,
  `gambar` varchar(128) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `riwayat_aktivitas`
--

CREATE TABLE `riwayat_aktivitas` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `aktivitas` varchar(256) NOT NULL,
  `timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transaksi_keluar`
--

CREATE TABLE `transaksi_keluar` (
  `id` int NOT NULL,
  `produk_id` int NOT NULL,
  `jumlah` int NOT NULL,
  `tanggal_keluar` datetime DEFAULT NULL,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transaksi_masuk`
--

CREATE TABLE `transaksi_masuk` (
  `id` int NOT NULL,
  `produk_id` int NOT NULL,
  `jumlah` int NOT NULL,
  `tanggal_masuk` datetime DEFAULT NULL,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int NOT NULL,
  `username` varchar(64) NOT NULL,
  `password` varchar(128) NOT NULL,
  `role` varchar(64) NOT NULL,
  `otp_secret` varchar(32) DEFAULT NULL,
  `otp_enabled` tinyint(1) DEFAULT NULL,
  `failed_login_attempts` int NOT NULL,
  `lockout_until` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `username`, `password`, `role`, `otp_secret`, `otp_enabled`, `failed_login_attempts`, `lockout_until`) VALUES
(3, 'admin', '$2b$12$fAXD6MvI12t2TgFCo2ss4.QOdWP3Vx.DvI6lnLL8OD4WSlXUIR5oa', 'admin', 'HP2JY7H4RL65NB6UBM4AHI5RF57TPHB6', 1, 0, NULL),
(5, 'superadmin', '$2b$12$8t3c4OG4.3Ir1sp4ryA6SOSUIxwPoc2xyMA/AgQlmyVb9i5C3obL6', 'superadmin', 'GS5SXV3JIUDAISUU5YITL4P5L3AWUGMG', 1, 0, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `produk`
--
ALTER TABLE `produk`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_produk_nama` (`nama`);

--
-- Indexes for table `riwayat_aktivitas`
--
ALTER TABLE `riwayat_aktivitas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_riwayat_aktivitas_timestamp` (`timestamp`);

--
-- Indexes for table `transaksi_keluar`
--
ALTER TABLE `transaksi_keluar`
  ADD PRIMARY KEY (`id`),
  ADD KEY `produk_id` (`produk_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_transaksi_keluar_tanggal_keluar` (`tanggal_keluar`);

--
-- Indexes for table `transaksi_masuk`
--
ALTER TABLE `transaksi_masuk`
  ADD PRIMARY KEY (`id`),
  ADD KEY `produk_id` (`produk_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_transaksi_masuk_tanggal_masuk` (`tanggal_masuk`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_user_username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `produk`
--
ALTER TABLE `produk`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `riwayat_aktivitas`
--
ALTER TABLE `riwayat_aktivitas`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `transaksi_keluar`
--
ALTER TABLE `transaksi_keluar`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `transaksi_masuk`
--
ALTER TABLE `transaksi_masuk`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `riwayat_aktivitas`
--
ALTER TABLE `riwayat_aktivitas`
  ADD CONSTRAINT `riwayat_aktivitas_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `transaksi_keluar`
--
ALTER TABLE `transaksi_keluar`
  ADD CONSTRAINT `transaksi_keluar_ibfk_1` FOREIGN KEY (`produk_id`) REFERENCES `produk` (`id`),
  ADD CONSTRAINT `transaksi_keluar_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `transaksi_masuk`
--
ALTER TABLE `transaksi_masuk`
  ADD CONSTRAINT `transaksi_masuk_ibfk_1` FOREIGN KEY (`produk_id`) REFERENCES `produk` (`id`),
  ADD CONSTRAINT `transaksi_masuk_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
