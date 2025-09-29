

SET NAMES utf8mb4;
SET time_zone = '+00:00';


DROP TABLE IF EXISTS `admins`;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO `admins` (`id`, `name`, `password`) VALUES
(1, 'admin', 'retro123'); -- Password is 'retro123'


DROP TABLE IF EXISTS `cart_items`;
CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1',
  `added_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `user_id` int NOT NULL,
  `comment_text` text NOT NULL,
  `comment_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO `comments` VALUES
(27,1,1123,'Takes me right back to my childhood. The SID chip sounds as glorious as ever. 10/10.','2025-09-07 22:04:01'),
(28,1,1623,'Arrived in pristine condition. It''s amazing to play games like ''Maniac Mansion'' on the original hardware again.','2025-09-07 22:04:01'),
(29,1,8129,'LOAD "*",8,1. The magic words. Everything works perfectly. A fantastic piece of computing history.','2025-09-07 22:04:01'),
(30,2,4208,'The creative powerhouse! Fired up Deluxe Paint II and it was a total nostalgia trip. This machine was way ahead of its time.','2025-09-07 22:04:01'),
(31,2,5892,'Finally got my hands on one. The custom chips for graphics and sound are incredible. Gaming on this is a dream.','2025-09-07 22:04:01'),
(32,3,1516,'Pure, simple, fun. The woodgrain finish is iconic. Paired it with the CX40 joystick and it''s perfect.','2025-09-07 22:04:01'),
(33,3,3776,'Showed this to my kids and they were hooked on ''Pitfall!''. Proof that good gameplay never gets old.','2025-09-07 22:04:01'),
(34,5,1998,'The machine that started it all for so many. Built like a tank and runs like a charm. Playing ''The Oregon Trail'' feels so authentic.','2025-09-07 22:04:01'),
(35,5,6007,'An essential part of my vintage computer collection. The open architecture is amazing for tinkering.','2025-09-07 22:04:01'),
(36,6,3456,'The original blueprint. The satisfying clack of the keyboard is worth the price alone. A serious machine for a serious collector.','2025-09-07 22:04:01'),
(37,6,6652,'Running original MS-DOS and some classic CGA games. It''s a fantastic experience.','2025-09-07 22:04:01'),
(38,8,4321,'The all-in-one design with the built-in tape deck is so clever. The green screen is incredibly sharp and iconic.','2025-09-07 22:04:01'),
(39,8,4815,'A beloved British classic. I''m having a great time exploring its unique game library.','2025-09-07 22:04:01'),
(40,9,7890,'You can''t play Atari without one of these. The feel is unmistakable. My wrist hurts, but it''s worth it!','2025-09-07 22:04:01'),
(41,9,9014,'Bought a second one for 2-player ''Combat''. They just don''t make them like this anymore.','2025-09-07 22:04:01'),
(42,10,9981,'The sound of this drive is the sound of my youth. It''s slow, it''s loud, and it''s perfect.','2025-09-07 22:04:01'),
(43,10,8842,'Works great with my C64. Loading games from floppy is so much better than tape.','2025-09-07 22:04:01'),
(44,11,1123,'The difference is night and day. My old DOS games have never sounded better. A must-have for any retro PC build.','2025-09-07 22:04:01'),
(45,11,1998,'GAME OVER! The voice samples are crystal clear. This card gave the PC its voice.','2025-09-07 22:04:01'),
(46,12,2048,'The game that defined a genre. Still holds up today. IDDQD.','2025-09-07 22:04:01'),
(47,12,1623,'Grabbed this for my retro rig. It''s fast, brutal, and endlessly replayable.','2025-09-07 22:04:01'),
(48,13,3456,'I''m Bobbin Threadbare, are you my mother? The humor is as sharp as ever. Best adventure game ever made.','2025-09-07 22:04:01'),
(49,13,3776,'A swashbuckling classic. The insult sword fighting is genius.','2025-09-07 22:04:01'),
(50,14,4208,'It''s dangerous to go alone! Take this. The golden cartridge is a thing of beauty. A true adventure.','2025-09-07 22:04:01'),
(51,14,6007,'The birth of a legend. The sense of exploration is still unmatched.','2025-09-07 22:04:01'),
(52,15,5892,'Platforming perfection. The sheer amount of secrets and power-ups is staggering. The Tanooki Suit is the best.','2025-09-07 22:04:01'),
(53,15,7331,'Every level is a masterpiece of design. This is a must-own for any NES owner.','2025-09-07 22:04:01'),
(54,16,4815,'Gotta go fast! The speed and attitude of this game were revolutionary. Green Hill Zone is iconic.','2025-09-07 22:04:01'),
(55,16,7890,'SEGA at its absolute best. The blast processing is real!','2025-09-07 22:04:01'),
(56,17,8129,'HADOKEN! The definitive fighting game. The SNES port is legendary and plays like a dream.','2025-09-07 22:04:01'),
(57,17,9014,'Still settling scores with friends on this. Choose your fighter!','2025-09-07 22:04:01'),
(58,18,9981,'Wocka wocka wocka! It''s not the arcade, but it''s a fun and challenging version. A piece of history.','2025-09-07 22:04:01'),
(59,18,8842,'The game that caused a phenomenon. Simple, addictive, and timeless.','2025-09-07 22:04:01'),
(60,19,1516,'Pew pew! Defending the earth one pixelated alien at a time. The sound design is legendary.','2025-09-07 22:04:01'),
(61,19,1123,'A timeless classic. It gets faster and faster... so tense!','2025-09-07 22:04:01'),
(62,20,1623,'The perfect puzzle game. Simple to learn, impossible to master. The reason I bought a Game Boy in the first place.','2025-09-07 22:04:01'),
(63,20,4208,'This game is a work of genius. The music will be stuck in my head forever.','2025-09-07 22:04:01'),
(64,21,3456,'Right on, Commander. An entire galaxy on one floppy disk. The sense of freedom is incredible.','2025-09-07 22:04:01'),
(65,21,5892,'Still trying to achieve that ''Elite'' ranking. A masterpiece of procedural generation.','2025-09-07 22:04:01'),
(66,22,3776,'The start of the modern PC era. Comes with Solitaire, so it''s a 10/10 from me.','2025-09-07 22:04:01'),
(67,22,4815,'Set this up on my old PC. Program Manager and File Manager are a blast from the past.','2025-09-07 22:04:01'),
(68,23,4321,'The software that defined the look of a generation of games. Still an incredibly powerful pixel art tool.','2025-09-07 22:04:01'),
(69,23,7331,'So intuitive and fun to use. The animation features were groundbreaking.','2025-09-07 22:04:01'),
(70,24,7890,'A true collector''s item. It''s amazing to see the humble beginnings of the world''s most popular OS.','2025-09-07 22:04:01'),
(71,24,8129,'Got this running in a virtual machine. The tiled windows are a unique feature of this version.','2025-09-07 22:04:01'),
(72,25,9014,'A nice evolution from 1.0. Overlapping windows! The debut of Excel and Word was a game-changer.','2025-09-07 22:04:01'),
(73,25,8842,'An important step in the history of the GUI. Fun to play around with.','2025-09-07 22:04:01'),
(74,26,6652,'The original save icon! Needed these for my Apple IIe. They work perfectly.','2025-09-07 22:04:01'),
(75,26,1123,'Handle with care! A 10-pack of pure nostalgia. 360KB of raw power.','2025-09-07 22:04:01'),
(76,27,1516,'The rock-solid foundation for so many classic PCs. C:> format c:','2025-09-07 22:04:01'),
(77,27,1623,'Installed this on an old IBM clone. Pure, unfiltered command-line computing.','2025-09-07 22:04:01'),
(78,28,1998,'The final and greatest version. DoubleSpace, Defrag, ScanDisk... it had everything!','2025-09-07 22:04:01'),
(79,28,3456,'The peak of DOS. Essential for getting a retro gaming PC up and running.','2025-09-07 22:04:01'),
(80,99,5543,'Finally, a machine that can run Crysis. A bit loud, but the results are worth it.','2025-09-07 22:04:03'),
(81,99,8200,'Used it to brute force the answer to my security question, which I forgot. It worked! Now what was my favorite Metroidvania game that came out in 2025 again?','2025-09-07 22:04:03');


DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `release_year` int DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `img` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `show_on_page` tinyint(1) DEFAULT '0',
  `stock` tinyint(1) NOT NULL DEFAULT '1',
  `hidden` tinyint(1) NOT NULL DEFAULT '1',
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO `products` VALUES
(1,'Commodore 64',1982,595.00,'/static/imgs/products/img_product_1.jpg','Computer',0,1,0,'The best-selling home computer of all time. Unleash 64KB of power and legendary SID chip sound. A true icon of the 80s.'),
(2,'Amiga 500',1987,699.00,'/static/imgs/products/img_product_2.jpg','Computer',1,1,0,'The creative powerhouse. With its advanced graphics and sound, the Amiga 500 changed gaming and digital art forever. Experience the magic.'),
(3,'Atari 2600',1977,199.00,'/static/imgs/products/img_product_3.jpg','Console',0,1,0,'The console that started it all. Simple woodgrain, a classic joystick, and a library of unforgettable games. Pure, uncut nostalgia.'),
(5,'Apple IIe',1983,750.00,'/static/imgs/products/img_product_5.jpg','Computer',1,1,0,'A legend from the garage that stormed into classrooms and homes. Reliable, expandable, and the machine that built an empire. Think different, even back then.'),
(6,'IBM PC 5150',1981,950.00,'/static/imgs/products/img_product_6.jpg','Computer',0,1,0,'The original. The blueprint for the modern PC. This is where it all began for business computing. Serious hardware for serious work (and a bit of gaming).'),
(8,'Amstrad CPC 464',1984,420.00,'/static/imgs/products/img_product_8.jpg','Computer',0,1,0,'The all-in-one wonder with its integrated cassette deck and vibrant green-screen monitor. A beloved British classic that made computing accessible.'),
(9,'Atari CX40 Joystick',1977,25.00,'/static/imgs/products/img_product_9.jpg','Peripheral',0,1,0,'The unmistakable click, the iconic red button. The one and only way to truly experience Atari classics. Your wrist will never be the same.'),
(10,'Commodore 1541 Floppy Drive',1982,180.00,'/static/imgs/products/img_product_10.jpg','Peripheral',1,1,0,'The sound of a generation. Hear the unmistakable grind and whirl of the 1541 as it loads your favorite games. Patience is a virtue.'),
(11,'Sound Blaster 16',1992,120.00,'/static/imgs/products/img_product_11.jpg','Peripheral',0,1,0,'Upgrade your PC from beeps and boops to a full orchestral experience. The card that gave PC gaming its voice. Game Over? Not with this sound.'),
(12,'Doom (PC)',1993,59.00,'/static/imgs/products/img_product_12.jpg','Game',1,0,0,'Grab your shotgun, it''s time to fight demons on Mars. The game that defined the First-Person Shooter genre. IDDQD.'),
(13,'The Secret of Monkey Island',1990,45.00,'/static/imgs/products/img_product_13.jpg','Game',0,1,0,'A swashbuckling adventure filled with insult sword fighting, grog, and a three-headed monkey. The pinnacle of point-and-click comedy.'),
(14,'The Legend of Zelda (NES)',1986,49.00,'/static/imgs/products/img_product_14.jpg','Game',0,1,0,'It''s dangerous to go alone! Take this. Your epic adventure to save Hyrule and Princess Zelda starts here. A golden cartridge of pure magic.'),
(15,'Super Mario Bros. 3 (NES)',1988,55.00,'/static/imgs/products/img_product_15.jpg','Game',1,1,0,'Is it a game or a stage play? With the Tanooki Suit, Kuribo''s Shoe, and countless secrets, this is platforming perfection.'),
(16,'Sonic the Hedgehog (Genesis)',1991,50.00,'/static/imgs/products/img_product_16.jpg','Game',1,1,0,'Way past cool! Blast through Green Hill Zone at supersonic speeds. The game that gave SEGA its attitude. Gotta go fast!'),
(17,'Street Fighter II (SNES)',1992,65.00,'/static/imgs/products/img_product_17.jpg','Game',0,1,0,'HADOKEN! The king of the arcade comes home. Choose your fighter and battle for global supremacy. The definitive fighting game.'),
(18,'Pac-Man (Atari 2600)',1982,30.00,'/static/imgs/products/img_product_18.jpg','Game',1,1,0,'Wocka wocka wocka. The arcade phenomenon on your home console. Chase ghosts, eat dots, and aim for the high score.'),
(19,'Space Invaders (Atari 2600)',1980,30.00,'/static/imgs/products/img_product_19.jpg','Game',0,1,0,'The alien horde is descending! Move your laser cannon and defend the Earth in this timeless arcade classic. Pew pew!'),
(20,'Tetris (Game Boy)',1989,40.00,'/static/imgs/products/img_product_20.jpg','Game',0,1,0,'The perfect puzzle game. Simple to learn, impossible to master. The reason millions of batteries were drained worldwide.'),
(21,'Elite (C64)',1984,35.00,'/static/imgs/products/img_product_21.jpg','Game',0,1,0,'Command your Cobra Mk III, trade across the galaxy, and become Elite. An entire universe on a single floppy disk. Right on, Commander.'),
(22,'Windows 3.1',1992,149.00,'/static/imgs/products/img_product_22.jpg','Software',1,1,0,'The moment the PC became user-friendly. With Program Manager, File Manager, and the legendary Solitaire. The start of a new era.'),
(23,'Deluxe Paint II (Amiga)',1986,99.00,'/static/imgs/products/img_product_23.jpg','Software',0,1,0,'The ultimate pixel art toolkit. The software behind the iconic art of countless Amiga games. Let your creativity run wild.'),
(24,'Windows 1.0',1985,99.00,'/static/imgs/products/img_product_24.jpg','Software',1,1,0,'See where the revolution began. A graphical shell for MS-DOS, complete with windows, icons, and the Reversi game. A true collector''s item.'),
(25,'Windows 2.0',1987,79.00,'/static/imgs/products/img_product_25.jpg','Software',1,1,0,'An evolution of the GUI. Overlapping windows and improved performance bring more power to your desktop. Featuring the debut of Excel and Word for Windows.'),
(26,'5.25" Floppy Disk (10-Pack)',1984,15.00,'/static/imgs/products/img_product_26.jpg','Peripheral',1,1,0,'The original save icon. Store a whopping 360KB of data on these classic flexible disks. Handle with care! (10-Pack).'),
(27,'MS-DOS 3.3',1987,69.00,'/static/imgs/products/img_product_27.jpg','Software',1,1,0,'The rock-solid foundation for a generation of computing. Master the command prompt and feel the raw power of your PC. C:>_'),
(28,'MS-DOS 6.22',1994,89.00,'/static/imgs/products/img_product_28.jpg','Software',0,1,0,'The final and most feature-rich standalone version of DOS. Includes ScanDisk, Defrag, and DoubleSpace to get the most out of your hard drive.'),
(99,'Quantum Computer',2028,15000000.00,'/static/imgs/computers/Quantum computing.png','Supercomputer',0,1,1,NULL);


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `security_question` text,
  `security_answer` text,
  `money` bigint DEFAULT NULL,
  `internal` tinyint(1) NOT NULL DEFAULT '0',
  `is_dev` tinyint(1) NOT NULL DEFAULT '0',
  `dev_token` varchar(32) DEFAULT NULL,
  `dev_password` varchar(32) DEFAULT NULL,
  `does_own_qun` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO `users` (`id`, `username`, `password`, `security_question`, `security_answer`, `money`, `internal`, `is_dev`, `dev_token`, `dev_password`, `does_own_qun`) VALUES
(1123, 'alice', '3d29b35b6d73f15b819f7f45719d29b2', 'Favorite color?', 'blue', 452, 0, 0, NULL, NULL, 0),
(1516, 'bob', '06c39f1c8413a21696010b9913165a25', 'First pet name?', 'max', 112, 0, 0, NULL, NULL, 0),
(1623, 'charlie', '18e11a22026f8d0a4e7601f010998f82', 'City of birth?', 'new york', 589, 0, 0, NULL, NULL, 0),
(1998, 'david', '095a5f1d1f7602a81878d6537536d5c5', 'Favorite food?', 'pizza', 230, 0, 0, NULL, NULL, 0),
(2048, 'eve', '0f9f315a61d15401121d4d3d4e8c1568', 'What is 1+1?', '2', 377, 0, 0, NULL, NULL, 0),
(2381, 'guest', '0d28383a886d34e9e1c22144d18770ca', 'Favorite color?', 'red', 501, 1, 0, NULL, NULL, 0),
(3354, 'customer35', '81dc9bdb52d04dc20036dbd8313ed055', '@Y@@!!#^@@^!@!!!@#!%', '!!#%^@^@&^&^##^%HETHGGGGDD', 350, 0, 1, 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4', '9f9c78601a4f4820874e03f0b07a5f67', 0),
(3456, 'frank', 'e4a2c58e5f22f7a9d5d5b7a08e1a61c3', 'City of birth?', 'london', 419, 0, 0, NULL, NULL, 0),
(3776, 'grace', '48b043a139174542289139f7278d91f6', 'First pet name?', 'shadow', 299, 0, 0, NULL, NULL, 0),
(4208, 'heidi', 'c82736b412b1b369941a37c356396821', 'Favorite food?', 'sushi', 523, 0, 0, NULL, NULL, 0),
(4321, 'ivan', 'f1a33501062955f1f513f1c1f109210e', 'What is 2+2?', '4', 15, 0, 0, NULL, NULL, 0),
(4815, 'judy', '7c84b12574e954c34e8f78d9a1353279', 'Favorite color?', 'green', 333, 0, 0, NULL, NULL, 0),
(5543, 'mallory', 'c36d2c4b75a06987f61c3c57a5e01b44', 'First pet name?', 'buddy', 248, 1, 0, NULL, NULL, 0),
(5892, 'mike', '876b539a2b535d4e1a0673418c397b91', 'City of birth?', 'tokyo', 489, 0, 0, NULL, NULL, 0),
(6007, 'nancy', '3f6b4d3a01c3858c5a0b73e52e505a76', 'Favorite food?', 'burger', 176, 0, 0, NULL, NULL, 0),
(6652, 'oscar', '678d3e9e8f4b1d3d5d7e4c1d6b8f3e0f', 'What is 3+3?', '6', 550, 0, 0, NULL, NULL, 0),
(7331, 'peggy', 'a2d1033b092a76e931e5f8b9d3e8a4d7', 'Favorite color?', 'yellow', 9, 0, 0, NULL, NULL, 0),
(7890, 'quentin', 'e674c6d6c3c5e8b4e4a6c4c3e8e6e5e4', 'First pet name?', 'max', 599, 0, 0, NULL, NULL, 0),
(8129, 'rupert', 'f5c0a3f4e2d2e1d1c0b0a8a7a6a5a4a3', 'City of birth?', 'paris', 101, 0, 0, NULL, NULL, 0),
(8200, 'trudy', 'b3e0c0a9a8a7a6a5a4a3a2a1a0989796', 'What is your favorite Metroidvania game that came out in september 2025?', 'Hollow Knight: Silksong', 444, 1, 0, NULL, NULL, 0),
(8842, 'victor', '9d1f9a8f7e6d5c4b3a29180f6e5d4c3b', 'Favorite movie?', 'The Matrix', 287, 0, 0, NULL, NULL, 0),
(9014, 'walter', '1e2d3c4b5a6987f6e5d4c3b2a19087f6', 'Favorite food?', 'pasta', 365, 0, 0, NULL, NULL, 0),
(9981, 'wendy', '7f6e5d4c3b2a190876543210fedcba98', 'Favorite color?', 'black', 512, 0, 0, NULL, NULL, 0),
(9984, 'carlos', '678d3e9e8f4b1d3d5d7e4c1d6b8f3e0f', '&^#@!()@!@#$%', '#@!%^&*()_+|}{POIUYTREWQ', 296, 0, 1, 'f1e2d3c4b5a6f1e2d3c4b5a6f1e2d3c4', 'b9a18f7d6e5c4b3a291807f6e5d4c3b2', 0);


DROP TABLE IF EXISTS `dev_transactions`;
CREATE TABLE `dev_transactions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `dev_user_id` int NOT NULL,
    `target_user_id` int NOT NULL,
    `amount` int NOT NULL,
    `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`dev_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`target_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


