-- שימוש במסד הנתונים הנכון
USE app;

-- מחיקת טבלאות קיימות כדי לאפשר הרצה נקייה בכל פעם
DROP TABLE IF EXISTS admins, cart_items, comments, products, users;

-- יצירת טבלת מנהלים
CREATE TABLE `admins` (
  `id` int DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL
);

-- יצירת טבלת פריטים בעגלה
CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `added_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

-- יצירת טבלת תגובות
CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `user_id` int NOT NULL,
  `comment_text` text NOT NULL,
  `comment_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

-- יצירת טבלת מוצרים
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `release_year` int DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `img` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `show_on_page` tinyint(1) DEFAULT '0',
  `stock` tinyint(1) NOT NULL DEFAULT '1',
  `hidden` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
);

-- יצירת טבלת משתמשים
CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `security_question` text,
  `security_answer` text,
  `money` bigint DEFAULT NULL,
  `internal` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
);


-- הוספת מידע לטבלאות --

INSERT INTO `admins` (`id`, `name`, `password`) VALUES
(1, 'admin', 'b889ae6563199a48682521e5944d42a6');

INSERT INTO `products` (`id`, `name`, `release_year`, `price`, `img`, `category`, `show_on_page`, `stock`, `hidden`) VALUES
(1, 'Commodore 64', 1982, 595.00, '/static/imgs/products/img_product_1.jpg', 'Computer', 0, 1, 0),
(2, 'Amiga 500', 1987, 600.00, '/static/imgs/products/img_product_2.jpg', 'Computer', 1, 1, 0),
(3, 'Atari 2600', 1977, 199.00, '/static/imgs/products/img_product_3.jpg', 'Console', 0, 1, 0),
(5, 'Apple IIe', 1983, 750.00, '/static/imgs/products/img_product_5.jpg', 'Computer', 1, 1, 0),
(6, 'IBM PC 5150', 1981, 950.00, '/static/imgs/products/img_product_6.jpg', 'Computer', 0, 1, 0),
(8, 'Amstrad CPC 464', 1984, 420.00, '/static/imgs/products/img_product_8.jpg', 'Computer', 0, 1, 0),
(9, 'Atari CX40 Joystick', 1977, 25.00, '/static/imgs/products/img_product_9.jpg', 'Peripheral', 0, 1, 0),
(10, 'Commodore 1541 Floppy Drive', 1982, 180.00, '/static/imgs/products/img_product_10.jpg', 'Peripheral', 1, 1, 0),
(11, 'Sound Blaster 16', 1992, 120.00, '/static/imgs/products/img_product_11.jpg', 'Peripheral', 0, 1, 0),
(12, 'Doom (PC)', 1993, 59.00, '/static/imgs/products/img_product_12.jpg', 'Game', 1, 0, 0),
(13, 'The Secret of Monkey Island', 1990, 45.00, '/static/imgs/products/img_product_13.jpg', 'Game', 0, 1, 0),
(14, 'The Legend of Zelda (NES)', 1986, 49.00, '/static/imgs/products/img_product_14.jpg', 'Game', 0, 1, 0),
(15, 'Super Mario Bros. 3 (NES)', 1988, 55.00, '/static/imgs/products/img_product_15.jpg', 'Game', 1, 1, 0),
(16, 'Sonic the Hedgehog (Genesis)', 1991, 50.00, '/static/imgs/products/img_product_16.jpg', 'Game', 1, 1, 0),
(17, 'Street Fighter II (SNES)', 1992, 65.00, '/static/imgs/products/img_product_17.jpg', 'Game', 0, 1, 0),
(18, 'Pac-Man (Atari 2600)', 1982, 30.00, '/static/imgs/products/img_product_18.jpg', 'Game', 1, 1, 0),
(19, 'Space Invaders (Atari 2600)', 1980, 30.00, '/static/imgs/products/img_product_19.jpg', 'Game', 0, 1, 0),
(20, 'Tetris (Game Boy)', 1989, 40.00, '/static/imgs/products/img_product_20.jpg', 'Game', 0, 1, 0),
(21, 'Elite (C64)', 1984, 35.00, '/static/imgs/products/img_product_21.jpg', 'Game', 0, 1, 0),
(22, 'Windows 3.1', 1992, 149.00, '/static/imgs/products/img_product_22.jpg', 'Software', 1, 1, 0),
(23, 'Deluxe Paint II (Amiga)', 1986, 99.00, '/static/imgs/products/img_product_23.jpg', 'Software', 0, 1, 0),
(24, 'Windows 1.0', 1985, 99.00, '/static/imgs/products/img_product_24.jpg', 'Software', 1, 1, 0),
(25, 'Windows 2.0', 1987, 79.00, '/static/imgs/products/img_product_25.jpg', 'Software', 1, 1, 0),
(26, '5.25\" Floppy Disk (10-Pack)', 1984, 15.00, '/static/imgs/products/img_product_26.jpg', 'Peripheral', 1, 1, 0),
(27, 'MS-DOS 3.3', 1987, 69.00, '/static/imgs/products/img_product_27.jpg', 'Software', 1, 1, 0),
(28, 'MS-DOS 6.22', 1994, 89.00, '/static/imgs/products/img_product_28.jpg', 'Software', 0, 1, 0),
(99, 'Quantum Computer', 2028, 15000000.00, '/static/imgs/computers/Quantum computing.png', 'Supercomputer', 0, 1, 1);

INSERT INTO `users` (`id`, `username`, `password`, `security_question`, `security_answer`, `money`, `internal`) VALUES
(1123, 'itai', '8f8f0a24dca5cf5370106a59f782696d', 'First pet\'s name?', 'Simba', 159, 0),
(1516, 'noa', '2d141a8263a609a45ff4eaabf9975c04', 'Mother\'s maiden name?', 'Shapira', 99, 0),
(1623, 'maya', '601116b41c2c7bd4273a12f4bd327294', 'First pet\'s name?', 'Milo', 184, 0),
(1998, 'michael', 'f12139d3808d82188047805652c364c8', 'First pet\'s name?', 'Lucy', 412, 0),
(2048, 'matan', '485b100455226e5b8b5c6e77cde25bf4', 'City of birth?', 'Rishon LeZion', 333, 0),
(2381, 'john', 'c6586b2e09d0ed0ee6431a1bb280657f', 'Favorite food?', 'Pizza', 273, 0),
(3354, 'customer45', '1c383cd30b7c298ab50293adfecb7b18', '*$@^Y@$@!!#^@$^@$^!@!!!$@$#!%', '!$!#%$^@$^@&^$&^##^%HETHGGGGDD', 63, 0),
(3456, 'tom', 'bb073f2855d769be5bf191f6378f7150', 'What was your high school mascot?', 'Eagle', 2075, 0),
(3776, 'hila', '4359d009e6a9e7f87bf105f7caadf29b', 'What is the name of the street you grew up on?', 'Herzl', 491, 0),
(4208, 'daniel', '74a0545dcba3eddcd0cf6d03223fe4cb', 'City of birth?', 'Tel Aviv', 321, 0),
(4321, 'guy', 'ef422969e9635cc7064ff445d3d71f37', 'What is your favorite movie?', 'The Matrix', 278, 0),
(4815, 'lior', 'bb073f2855d769be5bf191f6378f7150', 'What is your favorite color?', 'Blue', 67, 0),
(5543, 'shira', '81dc9bdb52d04dc20036dbd8313ed055', 'City of birth?', 'Jerusalem', 387, 1),
(5892, 'adi', 'dfa8c4222289b7c23966f903744568d2', 'Favorite food?', 'Pasta', 450, 0),
(6007, 'keren', '1818ed4ad07349235f52801084eb4ca2', 'City of birth?', 'Ashdod', 289, 0),
(6652, 'yael', '63c57732f6d6079aa88db2d386532ab7', 'First pet\'s name?', 'Oscar', 422, 0),
(7331, 'tamar', '0838ecfb969d782bae32f24d02057e26', 'Favorite food?', 'Sushi', 210, 0),
(7890, 'rotem', '3759a5c590f8f571e5115901abfadb4b', 'Mother\'s maiden name?', 'Biton', 199, 0),
(8129, 'adam', '7917a832f52259031f7d4991bba92231', 'What was your high school mascot?', 'Lion', 123, 0),
(8200, 'ori', '486c0401c56bf7ec2daa9eba58907da9', 'What is your Game?', 'Portal 2', 105248705, 1),
(8842, 'yosef', '81dc9bdb52d04dc20036dbd8313ed055', 'What is your favorite movie?', 'Inception', 365, 0),
(9014, 'omer', '88d18f7ba1e9c421f09f8bba1ea3f0bc', 'What is your favorite color?', 'Green', 245, 0),
(9981, 'ziv', '791b685be311521a9c0666ce16792084', 'What is your favorite movie?', 'Gladiator', 111, 0);