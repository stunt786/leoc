BEGIN TRANSACTION;
CREATE TABLE app_settings (
	id INTEGER NOT NULL, 
	setting_key VARCHAR(100) NOT NULL, 
	setting_value TEXT NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (setting_key)
);
INSERT INTO "app_settings" VALUES(1,'relief_items','["\u0924\u094d\u0930\u093f\u092a\u093e\u0932", "\u092a\u093f-\u092b\u092e", "\u092c\u0947\u0921 \u0935\u093f\u0938\u094d\u0924\u0930\u093e \u0924\u0928\u094d\u0928\u093e \u0938\u093f\u0930\u093e\u0928\u0940", "\u091a\u093e\u092e\u0932", "\u0926\u093e\u0932", "\u0915\u0941\u0915\u0930", "\u0915\u091f\u094c\u0930\u093e/\u0932\u094b\u091f\u093e", "\u0925\u093e\u0932\u0940 \u092a\u093f\u0932\u0947\u091f", "\u0935\u093e\u0932\u094d\u091f\u0940\u0928", "\u091c\u0917", "\u0915\u0930\u093e\u0908", "\u0917\u094d\u092f\u093e\u0901\u0938 \u091a\u0941\u0932\u094b", "\u0928\u0941\u0928", "\u0924\u0947\u0932", "\u0938\u093e\u092c\u0941\u0928", "\u092e\u0938\u0932\u093e", "\u0932\u093e\u0907\u091f\u0930", "\u0917\u093f\u0932\u093e\u0938", "\u091a\u0915\u094d\u0915\u0941", "\u0921\u0947\u0915", "\u0921\u093e\u0921\u0941/\u092a\u0928\u094d\u092f\u0941", "\u092c\u0947\u0932\u0928\u093e \u091a\u094b\u0915", "\u091a\u093f\u0928\u0940", "\u091a\u093f\u092f\u093e\u092a\u0924\u094d\u0924\u0940", "\u092c\u093f\u0932\u0947\u0919\u094d\u0915\u0947\u091f", "\u091a\u093e\u0930\u094d\u091c/\u0938\u0947\u0932 \u0932\u093e\u0907\u091f"]','2026-01-29 01:15:59.278139','2026-01-29 07:41:08.751465');
INSERT INTO "app_settings" VALUES(2,'fiscal_years','["2079/80", "2080/81", "2081/82", "2082/83"]','2026-01-29 01:15:59.285124','2026-01-29 01:18:13.725097');
INSERT INTO "app_settings" VALUES(3,'ssf_types','["\u091c\u0947\u0937\u094d\u0920 \u0928\u093e\u0917\u0930\u093f\u0915", "\u091c\u0947\u0937\u094d\u0920 \u0928\u093e\u0917\u0930\u093f\u0915 \u0905\u0928\u094d\u092f", "\u090f\u0915\u0932 \u092e\u0939\u093f\u0932\u093e", "\u0935\u093f\u0927\u0941\u0935\u093e", "\u092a\u0942\u0930\u094d\u0923 \u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e", "\u0905\u0924\u093f \u0905\u0936\u0915\u094d\u0924 \u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e", "\u092c\u093e\u0932\u092c\u093e\u0932\u093f\u0915\u093e"]','2026-01-29 01:15:59.289903','2026-01-29 01:20:44.044776');
INSERT INTO "app_settings" VALUES(4,'disaster_types','["\u092d\u0942\u0915\u092e\u094d\u092a", "\u092c\u093e\u0922\u0940", "\u092a\u0939\u093f\u0930\u094b", "\u0906\u0901\u0927\u0940", "\u0906\u0917\u0932\u093e\u0917\u0940", "\u0916\u0921\u0947\u0930\u0940", "\u092e\u0939\u093e\u092e\u093e\u0930\u0940", "\u091c\u0919\u094d\u0917\u0932\u0940 \u091c\u0928\u093e\u0935\u0930", "\u0905\u0938\u093f\u0928\u093e \u092a\u093e\u0928\u0940", "\u0906\u0930\u094d\u0925\u093f\u0915 \u0938\u0902\u0915\u091f", "\u0905\u0928\u094d\u092f"]','2026-01-29 01:15:59.291980','2026-01-29 01:23:34.737261');
INSERT INTO "app_settings" VALUES(5,'active_fiscal_year','2082/83','2026-02-09 15:19:39.123551','2026-02-09 15:36:38.389565');
CREATE TABLE daily_report_log (
	id INTEGER NOT NULL, 
	report_date_bs VARCHAR(10) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "daily_report_log" VALUES(1,'2082-10-19','2026-02-02 10:53:06.931309');
INSERT INTO "daily_report_log" VALUES(2,'2082-10-20','2026-02-03 00:33:43.403310');
INSERT INTO "daily_report_log" VALUES(3,'2082-10-21','2026-02-04 07:07:25.471529');
INSERT INTO "daily_report_log" VALUES(4,'2082-10-22','2026-02-05 06:24:22.364122');
INSERT INTO "daily_report_log" VALUES(5,'2082-10-23','2026-02-06 06:23:56.001132');
INSERT INTO "daily_report_log" VALUES(6,'2082-10-24','2026-02-07 16:02:04.811440');
INSERT INTO "daily_report_log" VALUES(7,'2082-10-25','2026-02-08 08:02:29.120299');
INSERT INTO "daily_report_log" VALUES(8,'2082-10-26','2026-02-09 05:27:28.072508');
INSERT INTO "daily_report_log" VALUES(9,'2082-09-26','2026-02-09 07:37:55.704290');
INSERT INTO "daily_report_log" VALUES(10,'2082-10-27','2026-02-10 01:26:16.069400');
INSERT INTO "daily_report_log" VALUES(11,'2082-10-28','2026-02-11 16:13:02.536364');
INSERT INTO "daily_report_log" VALUES(12,'2082-10-29','2026-02-12 05:31:30.874416');
INSERT INTO "daily_report_log" VALUES(13,'2082-11-04','2026-02-16 07:15:36.401806');
INSERT INTO "daily_report_log" VALUES(14,'2082-11-05','2026-02-17 05:14:15.361213');
INSERT INTO "daily_report_log" VALUES(15,'2082-11-06','2026-02-18 07:04:15.161581');
INSERT INTO "daily_report_log" VALUES(16,'2082-11-08','2026-02-20 04:49:41.296540');
INSERT INTO "daily_report_log" VALUES(17,'2082-11-10','2026-02-22 06:19:33.186765');
INSERT INTO "daily_report_log" VALUES(18,'2082-11-12','2026-02-24 11:42:13.366689');
INSERT INTO "daily_report_log" VALUES(19,'2082-11-13','2026-02-25 09:16:18.437804');
INSERT INTO "daily_report_log" VALUES(20,'2082-11-14','2026-02-26 05:02:30.345802');
INSERT INTO "daily_report_log" VALUES(21,'2082-11-15','2026-02-27 04:39:33.109339');
INSERT INTO "daily_report_log" VALUES(22,'2082-11-17','2026-03-01 04:46:15.488910');
INSERT INTO "daily_report_log" VALUES(23,'2082-11-25','2026-03-09 05:00:52.246935');
INSERT INTO "daily_report_log" VALUES(24,'2082-11-27','2026-03-11 04:41:53.575032');
INSERT INTO "daily_report_log" VALUES(25,'2082-11-28','2026-03-12 09:35:49.230047');
INSERT INTO "daily_report_log" VALUES(26,'2082-12-01','2026-03-15 04:18:44.855803');
INSERT INTO "daily_report_log" VALUES(27,'2082-12-02','2026-03-16 07:41:26.344658');
INSERT INTO "daily_report_log" VALUES(28,'2082-12-03','2026-03-17 06:51:22.012736');
INSERT INTO "daily_report_log" VALUES(29,'2082-12-04','2026-03-18 04:46:06.696941');
INSERT INTO "daily_report_log" VALUES(30,'2082-12-06','2026-03-20 07:01:51.459491');
INSERT INTO "daily_report_log" VALUES(31,'2082-12-09','2026-03-23 07:31:23.927110');
INSERT INTO "daily_report_log" VALUES(32,'2082-12-08','2026-03-23 07:31:34.797137');
INSERT INTO "daily_report_log" VALUES(33,'2082-12-10','2026-03-24 09:08:23.859066');
INSERT INTO "daily_report_log" VALUES(34,'2082-12-12','2026-03-26 04:55:08.390261');
INSERT INTO "daily_report_log" VALUES(35,'2082-12-15','2026-03-29 07:19:25.582891');
INSERT INTO "daily_report_log" VALUES(36,'2082-12-16','2026-03-30 04:48:23.703715');
INSERT INTO "daily_report_log" VALUES(37,'2082-12-17','2026-03-31 04:42:41.304825');
INSERT INTO "daily_report_log" VALUES(38,'2082-12-18','2026-04-01 03:34:10.261708');
INSERT INTO "daily_report_log" VALUES(39,'2082-12-19','2026-04-02 10:31:11.053829');
INSERT INTO "daily_report_log" VALUES(40,'2082-12-20','2026-04-03 06:04:28.508322');
INSERT INTO "daily_report_log" VALUES(41,'2082-12-23','2026-04-06 08:12:49.080651');
INSERT INTO "daily_report_log" VALUES(42,'2082-12-24','2026-04-07 05:32:51.207238');
INSERT INTO "daily_report_log" VALUES(43,'2082-12-26','2026-04-09 05:45:40.984030');
INSERT INTO "daily_report_log" VALUES(44,'2082-12-27','2026-04-10 13:54:31.126697');
INSERT INTO "daily_report_log" VALUES(45,'2082-12-30','2026-04-13 04:06:36.420499');
INSERT INTO "daily_report_log" VALUES(46,'2083-01-02','2026-04-15 01:17:02.792010');
INSERT INTO "daily_report_log" VALUES(47,'2083-01-03','2026-04-16 04:15:54.208708');
INSERT INTO "daily_report_log" VALUES(48,'2083-01-04','2026-04-17 06:47:19.345370');
INSERT INTO "daily_report_log" VALUES(49,'2083-01-08','2026-04-21 02:00:30.754762');
INSERT INTO "daily_report_log" VALUES(50,'2083-01-09','2026-04-22 04:46:13.548916');
INSERT INTO "daily_report_log" VALUES(51,'2083-01-11','2026-04-24 06:05:58.123392');
INSERT INTO "daily_report_log" VALUES(52,'2083-01-14','2026-04-27 09:08:03.088854');
INSERT INTO "daily_report_log" VALUES(53,'2083-01-15','2026-04-28 06:08:55.386740');
INSERT INTO "daily_report_log" VALUES(54,'2083-01-21','2026-05-04 07:19:11.210795');
INSERT INTO "daily_report_log" VALUES(55,'2083-01-22','2026-05-05 05:18:58.855567');
INSERT INTO "daily_report_log" VALUES(56,'2083-01-23','2026-05-06 09:19:22.804022');
INSERT INTO "daily_report_log" VALUES(57,'2083-01-25','2026-05-08 05:09:51.379695');
INSERT INTO "daily_report_log" VALUES(58,'2083-01-28','2026-05-11 04:06:40.600837');
INSERT INTO "daily_report_log" VALUES(59,'2083-01-29','2026-05-12 06:35:56.668421');
INSERT INTO "daily_report_log" VALUES(60,'2083-01-30','2026-05-13 07:32:20.360654');
INSERT INTO "daily_report_log" VALUES(61,'2083-01-31','2026-05-14 07:36:10.483032');
INSERT INTO "daily_report_log" VALUES(62,'2083-02-01','2026-05-15 04:19:02.412187');
INSERT INTO "daily_report_log" VALUES(63,'2083-02-04','2026-05-18 04:24:12.606696');
INSERT INTO "daily_report_log" VALUES(64,'2083-02-05','2026-05-19 03:56:02.606370');
INSERT INTO "daily_report_log" VALUES(65,'2083-02-07','2026-05-21 08:19:29.704795');
INSERT INTO "daily_report_log" VALUES(66,'2083-02-08','2026-05-22 08:50:32.830597');
INSERT INTO "daily_report_log" VALUES(67,'2083-02-11','2026-05-25 05:01:14.186292');
INSERT INTO "daily_report_log" VALUES(68,'2083-02-13','2026-05-27 04:53:33.003938');
INSERT INTO "daily_report_log" VALUES(69,'2083-02-18','2026-06-01 05:30:48.979867');
INSERT INTO "daily_report_log" VALUES(70,'2083-02-19','2026-06-02 03:40:33.125975');
INSERT INTO "daily_report_log" VALUES(71,'2083-02-20','2026-06-03 06:20:03.662312');
INSERT INTO "daily_report_log" VALUES(72,'2083-02-21','2026-06-04 07:41:26.819845');
INSERT INTO "daily_report_log" VALUES(73,'2083-02-25','2026-06-08 03:36:14.804801');
INSERT INTO "daily_report_log" VALUES(74,'2083-02-26','2026-06-09 08:07:16.839808');
INSERT INTO "daily_report_log" VALUES(75,'2083-02-27','2026-06-10 02:10:00.009828');
INSERT INTO "daily_report_log" VALUES(76,'2083-03-01','2026-06-15 10:14:26.970557');
INSERT INTO "daily_report_log" VALUES(77,'2083-03-02','2026-06-16 08:23:22.770808');
INSERT INTO "daily_report_log" VALUES(78,'2083-03-03','2026-06-17 15:38:45.254902');
INSERT INTO "daily_report_log" VALUES(79,'2083-03-04','2026-06-18 05:07:14.054512');
INSERT INTO "daily_report_log" VALUES(80,'2083-03-05','2026-06-19 00:29:04.791059');
INSERT INTO "daily_report_log" VALUES(81,'2083-03-08','2026-06-22 03:55:58.118965');
CREATE TABLE disaster (
	id INTEGER NOT NULL, 
	disaster_type VARCHAR(100) NOT NULL, 
	disaster_date DATE NOT NULL, 
	ward INTEGER NOT NULL, 
	tole VARCHAR(200), 
	latitude FLOAT, 
	longitude FLOAT, 
	fiscal_year VARCHAR(20), 
	description TEXT, 
	affected_households INTEGER, 
	affected_people INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, is_locked BOOLEAN DEFAULT 0, deaths INTEGER DEFAULT 0, missing_persons INTEGER DEFAULT 0, road_blocked_status BOOLEAN DEFAULT 0, electricity_blocked_status BOOLEAN DEFAULT 0, communication_blocked_status BOOLEAN DEFAULT 0, drinking_water_status BOOLEAN DEFAULT 0, public_building_destruction INTEGER DEFAULT 0, public_building_damage INTEGER DEFAULT 0, livestock_injured INTEGER DEFAULT 0, livestock_death INTEGER DEFAULT 0, cattle_lost INTEGER DEFAULT 0, cattle_injured INTEGER DEFAULT 0, poultry_lost INTEGER DEFAULT 0, poultry_injured INTEGER DEFAULT 0, goats_sheep_lost INTEGER DEFAULT 0, goats_sheep_injured INTEGER DEFAULT 0, other_livestock_lost INTEGER DEFAULT 0, other_livestock_injured INTEGER DEFAULT 0, agriculture_crop_damage TEXT, affected_people_male INTEGER DEFAULT 0, affected_people_female INTEGER DEFAULT 0, estimated_loss REAL DEFAULT 0.0, disaster_date_bs VARCHAR(10), injured INTEGER DEFAULT 0, casualties INTEGER DEFAULT 0, house_destroyed INTEGER DEFAULT 0, severity VARCHAR(20) DEFAULT 'medium', 
	PRIMARY KEY (id)
);
INSERT INTO "disaster" VALUES(1,'आगलागी','2026-01-05',7,'अदुकाली',29.463077,81.069416,'2082/83','विधुत सत भइ आगलागि भइ पूर्ण घर जलेको ',0,7,'2026-02-09 05:56:36.227260','2026-02-09 10:59:00.019021',0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'२ कोरु धान र गहु ',5,2,60000.0,'2082-09-20',0,0,1,'medium');
INSERT INTO "disaster" VALUES(2,'आगलागी','2025-10-16',6,'पिखेत खौला ',29.473174,81.026126,'2082/83','बिधुत सट भइ आगलागी भएकोले घर पूर्ण जलेको ',0,6,'2026-02-09 06:15:07.069035','2026-02-09 10:51:30.747236',0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'',3,3,150000.0,'2082-06-30',0,0,1,'medium');
INSERT INTO "disaster" VALUES(3,'अन्य','2025-12-25',4,'पलाई ',29.46109,80.962457,'2082/83','२०८० सालको भूकम्पले चर्केको घर अहिले आएर घर भत्तेको ',1,1,'2026-02-09 06:20:43.027608','2026-02-09 06:20:43.027615',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'',0,1,0.0,'2082-09-09',0,0,0,'medium');
INSERT INTO "disaster" VALUES(4,'अन्य','2026-01-24',4,'डिक्ला ',29.449709,80.98737,'2082/83','भूकम्पले घर चर्केका कारण पछि पूर्णरुपमा घर भत्केको',0,8,'2026-02-09 06:27:24.701228','2026-02-09 10:50:10.049651',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'घर भित्र भएको सबै अन्न वाली र भाडाकुडा पुरिएको ',2,6,0.0,'2082-10-10',0,0,1,'medium');
INSERT INTO "disaster" VALUES(5,'भूकम्प','2026-03-23',1,'वडाहरु',NULL,NULL,'2082/83','',0,0,'2026-03-23 09:10:51.209753','2026-03-23 09:10:51.209755',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'',0,0,0.0,'2082-12-09',0,0,0,'medium');
INSERT INTO "disaster" VALUES(6,'अन्य','2026-04-16',6,'पिखेत खौला ',29.468986,81.027674,'2082/83','थलारा गाँउपालिका अन्तरर्गत वडा न ६ हुवेडा डाडामा मोटरसाइकल र अटो एक आपसमा ठोक्किदा  मोटरसाइकल छेदविछेद भएको र मानविय क्षेति भएको ',0,2,'2026-04-17 06:50:18.306581','2026-04-17 06:50:18.306585',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'',2,0,0.0,'2083-01-03',0,2,0,'medium');
INSERT INTO "disaster" VALUES(7,'आँधी','2026-05-08',9,'आमबगर',29.489438,81.097207,'2082/83','हावाहुरीका कारण घरको छाना पुरै उडाएको ',1,3,'2026-05-08 05:09:46.220682','2026-05-08 05:09:46.220687',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'',1,2,0.0,'2083-01-25',0,0,0,'medium');
CREATE TABLE event_log (
	id INTEGER NOT NULL, 
	timestamp DATETIME, 
	event_type VARCHAR(100) NOT NULL, 
	description TEXT NOT NULL, 
	location VARCHAR(200), 
	responsible_unit VARCHAR(100), 
	status VARCHAR(50), 
	created_at DATETIME, 
	updated_at DATETIME, 
	is_locked BOOLEAN, 
	PRIMARY KEY (id)
);
INSERT INTO "event_log" VALUES(1,'2026-02-09 05:56:36.230985','Incident Report','आगलागी incident reported at अदुकाली','अदुकाली','LEOC','Active','2026-02-09 05:56:36.230987','2026-02-09 05:56:36.230989',0);
INSERT INTO "event_log" VALUES(2,'2026-02-09 06:15:07.076749','Incident Report','आगलागी incident reported at पिखेत खौला ','पिखेत खौला ','LEOC','Active','2026-02-09 06:15:07.076750','2026-02-09 06:15:07.076752',0);
INSERT INTO "event_log" VALUES(3,'2026-02-09 06:20:43.034997','Incident Report','अन्य incident reported at पलाई ','पलाई ','LEOC','Active','2026-02-09 06:20:43.034999','2026-02-09 06:20:43.034999',0);
INSERT INTO "event_log" VALUES(4,'2026-02-09 06:27:24.707813','Incident Report','अन्य incident reported at डिक्ला ','डिक्ला ','LEOC','Active','2026-02-09 06:27:24.707815','2026-02-09 06:27:24.707815',0);
INSERT INTO "event_log" VALUES(5,'2026-03-23 09:10:51.217608','Incident Report','भूकम्प incident reported at वडाहरु','वडाहरु','LEOC','Active','2026-03-23 09:10:51.217610','2026-03-23 09:10:51.217611',0);
INSERT INTO "event_log" VALUES(6,'2026-04-17 06:50:18.311930','Incident Report','अन्य incident reported at पिखेत खौला ','पिखेत खौला ','LEOC','Active','2026-04-17 06:50:18.311932','2026-04-17 06:50:18.311932',0);
INSERT INTO "event_log" VALUES(7,'2026-05-08 05:09:46.225487','Incident Report','आँधी incident reported at आमबगर','आमबगर','LEOC','Active','2026-05-08 05:09:46.225489','2026-05-08 05:09:46.225491',0);
CREATE TABLE fund_transaction (
	id INTEGER NOT NULL, 
	transaction_type VARCHAR(50) NOT NULL, 
	amount FLOAT NOT NULL, 
	description VARCHAR(500) NOT NULL, 
	transaction_date DATE NOT NULL, 
	is_locked BOOLEAN, 
	is_system BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE inventory_item (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	item_code VARCHAR(50), 
	category VARCHAR(100) NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit VARCHAR(50) NOT NULL, 
	source VARCHAR(100), 
	status VARCHAR(50), 
	expiry_date DATE, 
	warehouse_location VARCHAR(200), 
	remarks TEXT, 
	image_filename VARCHAR(255), 
	is_locked BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "inventory_item" VALUES(1,'एम्बुलेन्स','AMB01','Vehicle',1,'pcs','थलारा गा.पा','Available',NULL,'गाउँपालिका कार्यालय','','inv_1770045634_ambulance.jpeg',1,'2026-02-02 15:20:34.447391','2026-02-02 15:20:34.447396');
INSERT INTO "inventory_item" VALUES(2,'ब्याकुलोडर','BKL01','Vehicle',1,'pcs','थलारा गा.पा','Available',NULL,'गाउँपालिका कार्यालय','','inv_1770045823_backhule.png',1,'2026-02-02 15:23:43.947312','2026-02-02 15:23:43.947316');
INSERT INTO "inventory_item" VALUES(3,'चार पाङ्ग्रे गाडि','JP01','Vehicle',2,'pcs','थलारा गा.पा','Available',NULL,'गाउँपालिका कार्यालय','','inv_1770046082_wheeler.png',1,'2026-02-02 15:28:02.697177','2026-02-02 15:28:02.697181');
INSERT INTO "inventory_item" VALUES(4,'Meghaphone','MP01','Search & Rescue',2,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770048418_meghaphone.jpeg',1,'2026-02-02 16:06:58.953561','2026-02-02 16:06:58.953563');
INSERT INTO "inventory_item" VALUES(5,'Rubber Boots','RB01','Search & Rescue',12,'pair','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770048535_boots.jpeg',1,'2026-02-02 16:08:55.575853','2026-02-03 15:21:03.271770');
INSERT INTO "inventory_item" VALUES(6,'Safety Helmet','SH01','Search & Rescue',12,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770048618_safetyhelmet.jpeg',1,'2026-02-02 16:10:18.616716','2026-02-02 16:10:18.616722');
INSERT INTO "inventory_item" VALUES(7,'Rescue Gloves','RG01','Search & Rescue',12,'pair','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770048701_rescuegloves.jpeg',1,'2026-02-02 16:11:41.390136','2026-02-02 16:11:41.390139');
INSERT INTO "inventory_item" VALUES(8,'Reflective Jacket','RJ01','Search & Rescue',12,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770048851_orange-reflective-jacket.jpg',1,'2026-02-02 16:14:11.677739','2026-02-02 16:14:11.677742');
INSERT INTO "inventory_item" VALUES(9,'Anti Dust Eye Glass','ADEG01','Search & Rescue',12,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770048929_antidustglass.png',1,'2026-02-02 16:15:29.750903','2026-02-02 16:15:29.750906');
INSERT INTO "inventory_item" VALUES(10,'Torch Light','TL01','Search & Rescue',6,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770048984_tourchlight.jpg',1,'2026-02-02 16:16:24.447529','2026-02-02 16:16:24.447532');
INSERT INTO "inventory_item" VALUES(11,'Head Search Light','HDL01','Search & Rescue',12,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','with rechargable battery','inv_1770049080_headtorchlight.jpeg',1,'2026-02-02 16:18:00.446793','2026-02-02 16:18:00.446798');
INSERT INTO "inventory_item" VALUES(12,'Knee Pad','KP01','Search & Rescue',12,'pair','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049142_kneepad.jpg',1,'2026-02-02 16:19:02.815852','2026-02-02 16:19:02.815855');
INSERT INTO "inventory_item" VALUES(13,'Whistle','WL01','Search & Rescue',12,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049192_whistle.jpeg',1,'2026-02-02 16:19:52.192895','2026-02-02 16:19:52.192899');
INSERT INTO "inventory_item" VALUES(14,'Stretcher','ST01','Search & Rescue',2,'pcs','Pratibaddha-III project','Low Stock',NULL,'LEOC','','inv_1770049240_stretcher.jpeg',1,'2026-02-02 16:20:40.423311','2026-02-02 16:20:40.423315');
INSERT INTO "inventory_item" VALUES(15,'Tarpaulin','TPL01','Relief Material',3,'pcs','Pratibaddha-III project','Low Stock',NULL,'LEOC','','inv_1770049344_traupalin.jpeg',1,'2026-02-02 16:22:24.135452','2026-02-02 16:22:24.135457');
INSERT INTO "inventory_item" VALUES(16,'Hand Wood Cutter Machine','HWCM01','Search & Rescue',1,'pcs','Pratibaddha-III project','Low Stock',NULL,'LEOC','Petrol Saw','inv_1770049441_dieselwoodcutter.jpg',1,'2026-02-02 16:24:01.454729','2026-02-02 16:24:01.454736');
INSERT INTO "inventory_item" VALUES(17,'Bold IronCutter','BIC01','Search & Rescue',1,'pcs','Pratibaddha-III project','Low Stock',NULL,'LEOC','','inv_1770049554_bold_iron_cutter.jpeg',1,'2026-02-02 16:25:54.657145','2026-02-02 16:25:54.657149');
INSERT INTO "inventory_item" VALUES(18,'Dynamic Rope','DR01','Search & Rescue',1,'pcs','Pratibaddha-III project','Low Stock',NULL,'LEOC','','inv_1770049608_dynamicrope.png',1,'2026-02-02 16:26:48.115362','2026-02-02 16:26:48.115366');
INSERT INTO "inventory_item" VALUES(19,'Carabiner','CB01','Search & Rescue',4,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049655_carabiner.jpeg',1,'2026-02-02 16:27:35.228210','2026-02-02 16:27:35.228213');
INSERT INTO "inventory_item" VALUES(20,'Hand Operating Siren','HOS01','Search & Rescue',1,'pcs','Pratibaddha-III project','Low Stock',NULL,'LEOC','','inv_1770049708_hand_siren.jpeg',1,'2026-02-02 16:28:28.523515','2026-02-02 16:28:28.523519');
INSERT INTO "inventory_item" VALUES(21,'Throw Bag','TB01','Search & Rescue',4,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049753_throw_bag.jpeg',1,'2026-02-02 16:29:13.777012','2026-02-02 16:29:13.777017');
INSERT INTO "inventory_item" VALUES(22,'Sledge Hammer','SLH01','Search & Rescue',2,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049824_sledgehammer.jpeg',1,'2026-02-02 16:30:24.600850','2026-02-02 16:30:24.600854');
INSERT INTO "inventory_item" VALUES(23,'Shovel','SVL01','Search & Rescue',4,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049876_shovel.jpg',1,'2026-02-02 16:31:16.272253','2026-02-02 16:31:16.272257');
INSERT INTO "inventory_item" VALUES(24,'Crowbar','CBR01','Search & Rescue',4,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049918_crowbar.jpg',1,'2026-02-02 16:31:58.123060','2026-02-02 16:31:58.123064');
INSERT INTO "inventory_item" VALUES(25,'Pick-Axe','PA01','Search & Rescue',4,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770049986_pick-axe.jpg',1,'2026-02-02 16:33:06.431987','2026-02-02 16:33:06.431989');
INSERT INTO "inventory_item" VALUES(26,'Axe','AX01','Search & Rescue',4,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','wooden handle','inv_1770050037_axe.png',1,'2026-02-02 16:33:57.782196','2026-02-02 16:33:57.782200');
INSERT INTO "inventory_item" VALUES(27,'Bucket','BK01','Search & Rescue',6,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770050089_bucket.jpeg',1,'2026-02-02 16:34:49.443317','2026-02-02 16:34:49.443321');
INSERT INTO "inventory_item" VALUES(28,'Fire Extinguisher','FEX01','Search & Rescue',2,'pcs','Pratibaddha-III project','Expired',NULL,'LEOC','','inv_1770050148_fire_extinguisher.jpeg',1,'2026-02-02 16:35:48.674263','2026-02-02 16:35:48.674267');
INSERT INTO "inventory_item" VALUES(29,'Hydraulic Jack','HJ01','Search & Rescue',1,'pcs','Pratibaddha-III project','Low Stock',NULL,'LEOC','','inv_1770050197_hydraulic_jack.jpeg',1,'2026-02-02 16:36:37.957560','2026-02-02 16:36:37.957565');
INSERT INTO "inventory_item" VALUES(30,'First Aid Kit','FAK01','Medical',4,'set','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770050271_First-Aid-Kit.jpeg',1,'2026-02-02 16:37:51.991461','2026-02-02 16:37:51.991465');
INSERT INTO "inventory_item" VALUES(31,'Fire Safety Back Pack Spray','FSBP01','Search & Rescue',2,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','Forest Fire Sprayer','inv_1770050349_fire_safety_back_pack.jpeg',1,'2026-02-02 16:39:09.014647','2026-02-02 16:39:09.014652');
INSERT INTO "inventory_item" VALUES(32,'Metal Storage Box','MSB01','Logistics',1,'pcs','Pratibaddha-III project','Available',NULL,'LEOC','','inv_1770050478_tin-storage-box-876.jpg',1,'2026-02-02 16:41:18.350302','2026-02-03 15:19:29.800273');
CREATE TABLE public_information (
	id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	content TEXT NOT NULL, 
	info_type VARCHAR(50), 
	priority VARCHAR(20), 
	is_active BOOLEAN, 
	valid_from DATETIME, 
	valid_until DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, 
	is_locked BOOLEAN, 
	PRIMARY KEY (id)
);
INSERT INTO "public_information" VALUES(1,'विपत सम्बन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । 
सम्पर्क व्यक्ति : ९८६५६५४६६५,     ९८४८९७८८००','General','Low',1,'2026-02-03 04:53:03.367272',NULL,'2026-02-03 04:53:03.367275','2026-02-03 04:53:03.367276',1);
INSERT INTO "public_information" VALUES(2,'आगामी २४ घण्टाको पूर्वानुमान','देशका हिमाली भू‍-भागमा साधारणतया बादल लाग्नेछ र गण्डकी, कर्णाली, लुम्बिनी र सुदूरपश्चिम प्रदेश लगायत बाँकी प्रदेशको पहाडी भू-भागमा आंशिक बादल लाग्नेछ र बाँकी तराईका भू-भागमा मौसम मुख्यतया सफा रहेको छ । देशका उच्च पहाडी तथा हिमाली भू‍-भागका थोरै स्थानहरूमा मध्यम हिमपात/वर्षाको सम्भावना रहेको छ ।','General','Low',1,'2026-02-03 05:31:48.635316',NULL,'2026-02-03 05:31:48.635320','2026-02-03 05:31:48.635320',1);
INSERT INTO "public_information" VALUES(3,'विपत सम्बन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००
 दैनिक विपद् डाटा प्रविष्टि विवरण','Emergency Contact','Low',1,'2026-02-04 08:56:39.029130',NULL,'2026-02-04 08:56:39.029133','2026-02-04 08:56:39.029134',1);
INSERT INTO "public_information" VALUES(4,'विपत सम्वन्धि जानकारी','विपत सम्बन्धि जानकारी:
विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८०० दैनिक विपद् डाटा प्रविष्टि विवरण','General','Low',1,'2026-02-05 09:47:12.068484',NULL,'2026-02-05 09:47:12.068487','2026-02-05 09:47:12.068488',1);
INSERT INTO "public_information" VALUES(5,'विपत सम्वन्धि जानकारी','विपत सम्बन्धि जानकारी: विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८०० दैनिक विपद् डाटा प्रविष्टि विवरण','General','Low',1,'2026-02-06 06:23:41.722730',NULL,'2026-02-06 06:23:41.722736','2026-02-06 06:23:41.722743',1);
INSERT INTO "public_information" VALUES(6,'विपत सम्वन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००

आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','General','Low',1,'2026-02-06 06:28:33.040306',NULL,'2026-02-06 06:28:33.040309','2026-02-06 06:28:33.040310',1);
INSERT INTO "public_information" VALUES(7,'विपत सम्वन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००  आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','General','Low',1,'2026-02-06 06:30:36.199336',NULL,'2026-02-06 06:30:36.199338','2026-02-06 06:30:36.199339',1);
INSERT INTO "public_information" VALUES(8,'विपत सम्बन्धि जानकारी','आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','General','Low',1,'2026-02-06 08:17:00.040639',NULL,'2026-02-06 08:17:00.040643','2026-02-06 08:17:00.040649',1);
INSERT INTO "public_information" VALUES(9,'विपत सम्बन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००','General','Low',1,'2026-02-09 08:26:24.422836',NULL,'2026-02-09 08:26:24.422840','2026-02-09 08:26:24.422841',1);
INSERT INTO "public_information" VALUES(10,'विपत सम्बन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC) सम्पर्क नं. ९७४३५३७२१५
सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००','General','Low',1,'2026-02-12 07:32:57.207231',NULL,'2026-02-12 07:32:57.207235','2026-02-12 07:32:57.207236',1);
INSERT INTO "public_information" VALUES(11,'विपत सम्बन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC) सम्पर्क नं. ९७४३५३७२१५ सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००','General','Low',1,'2026-02-16 07:14:05.152573',NULL,'2026-02-16 07:14:05.152578','2026-02-16 07:14:05.152585',1);
INSERT INTO "public_information" VALUES(12,'विपत सम्वन्धि जानकारी','आज राती
तराई भू-भागका थोरै स्थानहरूमा तुँवालो रहनेछ । कर्णाली र सुदूरपश्चिम प्रदेश लगायत गण्डकी प्रदेशको पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र  बाँकी भू-भागमा मौसम मुख्यतया सफा रहनेछ ।','General','Low',1,'2026-02-17 05:14:01.779693',NULL,'2026-02-17 05:14:01.779696','2026-02-17 05:14:01.779698',1);
INSERT INTO "public_information" VALUES(13,'विपत सम्वन्धि जानकारी','तराई भू-भागका थोरै स्थानहरूमा तुँवालो रहनेछ। कोशी प्रदेश लगायत बागमती र गण्डकी प्रदेशको हिमाली भू-भागमा आंशिक बादल लाग्नेछ तथा बाँकी भू-भागमा मौसम मुख्यतया सफा रहनेछ।','General','Low',1,'2026-02-20 04:48:30.277127',NULL,'2026-02-20 04:48:30.277130','2026-02-20 04:48:30.277131',1);
INSERT INTO "public_information" VALUES(14,'विपत सम्वन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC) सम्पर्क नं. ९७४३५३७२१५ सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००','General','Low',1,'2026-02-22 06:09:03.740862',NULL,'2026-02-22 06:09:03.740863','2026-02-22 06:09:03.740864',1);
INSERT INTO "public_information" VALUES(15,'विपत सम्वन्धि जानकारी','साप्ताहिक मौसम पूर्वानुमान वैधताको अवधि: २०८२ फागुन ०८ गते देखि १४ गते सम्म
उच्च पहाडी तथा हिमाली भू-भागः कोशी, बागमती र गण्डकी  प्रदेशमा साताको शुरुमा एक दुई स्थानमा तथा मध्य र अन्त्यमा थोरै स्थानहरुमा तथा लुम्बिनी, कर्णाली र सुदूरपश्चिम प्रदेशमा साताको शुरु र अन्त्यमा एक-दुई स्थानमा तथा मध्यमा थोरै स्थानहरुमा हल्का हिमपात/वर्षाको सम्भावना रहेको छ ।','General','Low',1,'2026-02-22 06:19:28.189344',NULL,'2026-02-22 06:19:28.189347','2026-02-22 06:19:28.189353',1);
INSERT INTO "public_information" VALUES(16,'विपत सम्वन्धि जानकारी','साप्ताहिक मौसम पूर्वानुमान अवधि: २०८२ फागुन ०८ गते देखि १४ गते सम्म उच्च पहाडी तथा हिमाली भू-भागः सुदूरपश्चिम प्रदेशमा साताको शुरु र अन्त्यमा एक-दुई स्थानमा तथा मध्यमा थोरै स्थानहरुमा हल्का हिमपात/वर्षाको सम्भावना रहेको छ ।','General','Low',1,'2026-02-22 06:22:12.951537',NULL,'2026-02-22 06:22:12.951541','2026-02-22 06:22:12.951542',1);
INSERT INTO "public_information" VALUES(17,'मौसम सम्वन्धि जानकारी:','साप्ताहिक मौसम पूर्वानुमान अवधि: २०८२ फागुन ०८ गते देखि १४ गते सम्म उच्च पहाडी तथा हिमाली भू-भागः सुदूरपश्चिम प्रदेशमा साताको शुरु र अन्त्यमा एक-दुई स्थानमा तथा मध्यमा थोरै स्थानहरुमा हल्का हिमपात/वर्षाको सम्भावना रहेको छ ।','General','Low',1,'2026-02-24 11:49:04.453412',NULL,'2026-02-24 11:49:04.453416','2026-02-24 11:49:04.453417',1);
INSERT INTO "public_information" VALUES(18,'विपत सम्वन्धि जानकारी','साप्ताहिक मौसम पूर्वानुमान अवधि: २०८२ फागुन ०८ गते देखि १४ गते सम्म उच्च पहाडी तथा हिमाली भू-भागः सुदूरपश्चिम प्रदेशमा साताको शुरु र अन्त्यमा एक-दुई स्थानमा तथा मध्यमा थोरै स्थानहरुमा हल्का हिमपात/वर्षाको सम्भावना रहेको छ ।','General','Low',1,'2026-02-25 09:15:56.385911',NULL,'2026-02-25 09:15:56.385915','2026-02-25 09:15:56.385916',1);
INSERT INTO "public_information" VALUES(19,'विपत सम्वन्धि जानकारी','साप्ताहिक मौसम पूर्वानुमान अवधि: २०८२ फागुन ०८ गते देखि १४ गते सम्म उच्च पहाडी तथा हिमाली भू-भागः सुदूरपश्चिम प्रदेशमा साताको शुरु र अन्त्यमा एक-दुई स्थानमा तथा मध्यमा थोरै स्थानहरुमा हल्का हिमपात/वर्षाको सम्भावना रहेको छ ।','General','Low',1,'2026-02-26 05:02:21.133053',NULL,'2026-02-26 05:02:21.133056','2026-02-26 05:02:21.133057',1);
INSERT INTO "public_information" VALUES(20,'विपत सम्वन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC) सम्पर्क नं. ९७४३५३७२१५ सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००','General','Low',1,'2026-02-27 04:39:06.434102',NULL,'2026-02-27 04:39:06.434105','2026-02-27 04:39:06.434113',1);
INSERT INTO "public_information" VALUES(21,'विपत सम्वन्धि जानकारी','२०८२ फागुन २६ गते (मङ्गलबार)
दिउँसोः  देशभर साधारणतया बादल लाग्नेछ। कोशी, बागमती, गण्डकी र लुम्बिनी प्रदेशको पहाडी र हिमाली भू-भागका थोरै स्थानहरूमा, कर्णाली र सुदूरपश्चिम प्रदेशका पहाडी र हिमाली भू-भाग तथा देशको तराई भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','General','Low',1,'2026-03-09 05:00:21.116835',NULL,'2026-03-09 05:00:21.116838','2026-03-09 05:00:21.116839',1);
INSERT INTO "public_information" VALUES(22,'विपत सम्वन्धि जानकारी','सुदूरपश्चिम प्रदेशको भोली पहाडी र हिमाली भू-भाग एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','General','Low',1,'2026-03-11 04:41:35.357362',NULL,'2026-03-11 04:41:35.357364','2026-03-11 04:41:35.357366',1);
INSERT INTO "public_information" VALUES(23,'विपत सम्वन्धि जानकारी','विपत सम्बन्धि जानकारीका लागि यस कार्यालयको स्थानीय आपतकालिन कार्यसञ्चालन केन्द्रमा जानकारी दिन हुन अनुरोध छ । स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC) सम्पर्क नं. ९७४३५३७२१५ सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००','General','Low',1,'2026-03-12 09:34:39.900738',NULL,'2026-03-12 09:34:39.900740','2026-03-12 09:34:39.900742',1);
INSERT INTO "public_information" VALUES(24,'विपत सम्वन्धि जानकारी','भोली: सुदुरपश्चिम प्रदेशको पहाडी भू-भागका थोरै स्थानहरूमा एक-दुई स्थानहरूमा मेघगर्जन/चट्याङ्ग सहित हल्का  वर्षाको सम्भावना रहेको छ।','General','Low',1,'2026-03-15 04:18:10.440565',NULL,'2026-03-15 04:18:10.440568','2026-03-15 04:18:10.440569',1);
INSERT INTO "public_information" VALUES(25,'विपत सम्वन्धि जानकारी','भोली: सुदुरपश्चिम प्रदेशको पहाडी भू-भागका थोरै स्थानहरूमा एक-दुई स्थानहरूमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षाको सम्भावना रहेको छ।','General','Low',1,'2026-03-16 07:41:21.231239',NULL,'2026-03-16 07:41:21.231243','2026-03-16 07:41:21.231244',1);
INSERT INTO "public_information" VALUES(26,'विपत सम्वन्धि जानकारी','साताको शुरूमा एक-दुई स्थानमा, मध्य र अन्त्यमा थोरै स्थानहरूमा, हल्का देखि मध्यम हिमपात/ वर्षाको सम्भावना ।','General','Low',1,'2026-03-17 06:50:41.818272',NULL,'2026-03-17 06:50:41.818278','2026-03-17 06:50:41.818280',1);
INSERT INTO "public_information" VALUES(27,'विपत सम्वन्धि जानकारी','साताको शुरूमा एक-दुई स्थानमा, मध्य र अन्त्यमा थोरै स्थानहरूमा, हल्का देखि मध्यम हिमपात/ वर्षाको सम्भावना ।','General','Low',1,'2026-03-18 04:45:59.229826',NULL,'2026-03-18 04:45:59.229829','2026-03-18 04:45:59.229834',1);
INSERT INTO "public_information" VALUES(28,'विपत सम्वन्धि जानकारी','बझाङ्गको थलारा गा.पाको आसपासका क्षेत्रमा आज र भोली हल्का देखि एक दुई स्थानमा भारी वर्षा, हिमपात तथा तिव्र हावाहुरीको सम्भावना रहेको पूर्वानुमान छ','General','Low',1,'2026-03-20 07:00:38.882459',NULL,'2026-03-20 07:00:38.882462','2026-03-20 07:00:38.882463',1);
INSERT INTO "public_information" VALUES(29,'मौसम सम्बन्धि जानकारी','देशको पहाडी र हिमाली भु-भागमा साधारणतया बादल लाग्नेछ र तराई भू-भागमा आँशिक बादल लाग्नेछ। सुदूरपश्चिम  र कर्णाली प्रदेशको पहाडी र हिमाली भू-भागका केही स्थानहरूमा तथा बाँकी पहाडी र हिमाली भु-भागका थोरै स्थानहरूमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','Weather Advisory','Normal',1,'2026-03-23 07:42:35.161259',NULL,'2026-03-23 07:42:35.161260','2026-03-23 07:42:35.161261',1);
INSERT INTO "public_information" VALUES(30,'मौसम सम्बन्धि जानकारी','थलारा क्षेत्रमा आँशिक बादल लाग्ने','General','Low',1,'2026-03-24 09:08:21.666830',NULL,'2026-03-24 09:08:21.666833','2026-03-24 09:08:21.666835',1);
INSERT INTO "public_information" VALUES(31,'मौसम सम्बन्धि जानकारी','विभिन्न स्थानमा बदली रहि केहि स्थानमा हल्का बर्षा हुन सक्ने','General','Low',1,'2026-03-24 10:12:10.496909',NULL,'2026-03-24 10:12:10.496913','2026-03-24 10:12:10.496914',1);
INSERT INTO "public_information" VALUES(32,'मौसम सम्बन्धि जानकारी','देशको पहाडी र हिमाली भु-भागमा साधारणतया बादल लाग्नेछ र तराई भू-भागमा आँशिक बादल लाग्नेछ। सुदूरपश्चिम र कर्णाली प्रदेशको पहाडी र हिमाली भू-भागका केही स्थानहरूमा तथा बाँकी पहाडी र हिमाली भु-भागका थोरै स्थानहरूमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','General','Low',1,'2026-03-26 04:55:05.765967',NULL,'2026-03-26 04:55:05.765970','2026-03-26 04:55:05.765971',1);
INSERT INTO "public_information" VALUES(33,'विपत सम्बन्धि जानकारी','२०८२ चैत्र १९ गते (बिहिबार)
दिउँसोः हिमाली र  पहाडी भू-भागमा आंशिक बादल लाग्नेछ,  तराई भू-भागमा मौसम मुख्यतया सफा रहनेछ।  कोशी, बागमती, गण्डकी, कर्णाली र सुदूरपश्चिम प्रदेशको हिमाली भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','General','Low',1,'2026-04-01 03:33:39.341961',NULL,'2026-04-01 03:33:39.341966','2026-04-01 03:33:39.341967',1);
INSERT INTO "public_information" VALUES(34,'विपत सम्बन्धि जानकारी','चैत्र १९ र २० गते (बिहिबार)
दिउँसोः हिमाली र  पहाडी भू-भागमा आंशिक बादल लाग्नेछ,  तराई भू-भागमा मौसम मुख्यतया सफा रहनेछ।  कोशी, बागमती, गण्डकी, कर्णाली र सुदूरपश्चिम प्रदेशको हिमाली भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','General','Low',1,'2026-04-01 03:35:43.103195',NULL,'2026-04-01 03:35:43.103200','2026-04-01 03:35:43.103202',1);
INSERT INTO "public_information" VALUES(35,'मौसम सम्बन्धि जानकारी','दिउँसोः हिमाली र पहाडी भू-भागमा आंशिक बादल लाग्नेछ, तराई भू-भागमा मौसम मुख्यतया सफा रहनेछ। कोशी, बागमती, गण्डकी, कर्णाली र सुदूरपश्चिम प्रदेशको हिमाली भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','General','Low',1,'2026-04-02 10:30:42.248356',NULL,'2026-04-02 10:30:42.248360','2026-04-02 10:30:42.248361',1);
INSERT INTO "public_information" VALUES(36,'मौसम सम्बन्धि जानकारी','सबै प्रदेशको हिमाली भू-भाग लगायत  गण्डकी, लुम्बिनी, कर्णाली र सुदूरपश्चिम प्रदेशका पहाडी भू-भागमा साधारणतया बादल लाग्ने तथा बाँकी भू-भागमा आंशिक बादल लाग्नेछ।  सुदूरपश्चिम प्रदेशका पहाडी तथा हिमाली भू-भागका थोरै स्थानहरूमा मेघगर्जन/चट्याङ्ग सहित मध्यम वर्षा/हिमपात सम्भावना रहेको छ।','General','Low',1,'2026-04-03 06:04:23.185373',NULL,'2026-04-03 06:04:23.185377','2026-04-03 06:04:23.185378',1);
INSERT INTO "public_information" VALUES(37,'विपत सम्वन्धि जानकारी','हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै मध्यम हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-04-06 08:12:45.675155',NULL,'2026-04-06 08:12:45.675158','2026-04-06 08:12:45.675164',1);
INSERT INTO "public_information" VALUES(38,'मौसम सम्बन्धि जानकारी','साताको शुरू र मध्यमा थोरै स्थानहरूमा तथा अन्त्यमा  धेरै स्थानहरूमा  हल्का देखि मध्यम  वर्षाको सम्भावना । साताको अन्त्यमा एक-दुई स्थानमा भारी वर्षा/ हिमपातको सम्भावना ।','General','Low',1,'2026-04-07 05:36:03.561739',NULL,'2026-04-07 05:36:03.561742','2026-04-07 05:36:03.561744',1);
INSERT INTO "public_information" VALUES(39,'मौसम सम्बन्धि जानकारी','शुक्रवार र शनिवार हिमाली क्षेत्रमा आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन चट्याङ्ग सहित हल्का वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । 
पहाडी क्षेत्रमा आंंशिक बदली रहने छ ।','General','Low',1,'2026-04-09 05:45:30.508406',NULL,'2026-04-09 05:45:30.508409','2026-04-09 05:45:30.508410',1);
INSERT INTO "public_information" VALUES(40,'विपत सम्बन्धि जानकारी','भोली सनिवार सुदूरपश्चिम प्रदेशका पहाडी भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ। लुम्बिनी र सुदूरपश्चिम प्रदेशका तराईका थोरै स्थानहरूमा हावाहुरीको समेत सम्भावना रहेको छ ।','General','Low',1,'2026-04-10 13:54:27.575967',NULL,'2026-04-10 13:54:27.575971','2026-04-10 13:54:27.575972',1);
INSERT INTO "public_information" VALUES(41,'मौसम सम्बन्धि जानकारी','भोली १ गते हिमाली क्षेत्रमा साधारणतया बदली रहने छ ।
२ गते हिमाली क्षेत्रमा साधारणतया बदली रही एक-दुई स्थानमा मेघगर्जन चट्याङ्ग सहित हल्का वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-04-13 04:06:08.227885',NULL,'2026-04-13 04:06:08.227888','2026-04-13 04:06:08.227889',1);
INSERT INTO "public_information" VALUES(42,'विपत सम्बन्धि जानकारी','हिमाली क्षेत्रमा साधारणतया बदली रही एक-दुई स्थानमा मेघगर्जन चट्याङ्ग सहित हल्का वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।
पहाडी क्षेत्रमा आंंशिक बदली रहने छ ।
तराई क्षेत्रमा मुख्यतया सफा रहने छ ।','General','Low',1,'2026-04-15 01:16:59.622410',NULL,'2026-04-15 01:16:59.622413','2026-04-15 01:16:59.622418',1);
INSERT INTO "public_information" VALUES(43,'विपत सम्बन्धि जानकारी','भोली सुदुरपश्चिमको हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।  पहाडी क्षेत्रमा मुख्यतया सफा रहने छ । तराई क्षेत्रमा मुख्यतया सफा रही तातो लहरको सम्भावना रहेकाे छ ।','General','Low',1,'2026-04-21 02:00:25.681191',NULL,'2026-04-21 02:00:25.681194','2026-04-21 02:00:25.681195',1);
INSERT INTO "public_information" VALUES(44,'विपत सम्बन्धि जानकारी','हिमाली क्षेत्रमा साधारणतया बदली रहने छ ।
पहाडी क्षेत्रमा आंंशिक बदली रहने छ ।
तराई क्षेत्रमा मुख्यतया सफा रही तातो लहरको सम्भावना रहेकाे छ ।','General','Low',1,'2026-04-22 04:46:09.754008',NULL,'2026-04-22 04:46:09.754010','2026-04-22 04:46:09.754012',1);
INSERT INTO "public_information" VALUES(45,'मौसम सम्बन्धि जानकारी','१२ र १३ गते हिमाली क्षेत्रमा साधारणतया बदली रही केही स्थानहरुमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै मध्यम हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-04-24 06:05:54.260733',NULL,'2026-04-24 06:05:54.260736','2026-04-24 06:05:54.260737',1);
INSERT INTO "public_information" VALUES(46,'मौसम सम्बन्धि जानकारी','हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै मध्यम हिमपातको सम्भावना रहेकाे छ ।
पहाडी क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।
तराई क्षेत्रमा आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।','General','Low',1,'2026-04-27 09:07:59.837727',NULL,'2026-04-27 09:07:59.837729','2026-04-27 09:07:59.837730',1);
INSERT INTO "public_information" VALUES(47,'मौसम सम्बन्धि जानकारी','२०८३  वैशाख २२ गते (मंगलबार)
दिउँसोः देशभर साधारणतया बादल लाग्नेछ। कोशी, मधेश, बागमती, गण्डकी र  लुम्बिनी प्रदेशका केही स्थानहरूमा तथा बाँकी प्रदेशका थोरै स्थानहरूमा मेघगर्जन/चट्याङ्ग सहित मध्यम सम्मको वर्षा/हिमपातको सम्भावना रहेको छ।','General','Low',1,'2026-05-04 07:19:06.411579',NULL,'2026-05-04 07:19:06.411584','2026-05-04 07:19:06.411591',1);
INSERT INTO "public_information" VALUES(48,'मौसम सम्बन्धि जानकारी','२०८३ वैशाख २२ गते (मंगलबार) दिउँसोः देशभर साधारणतया बादल लाग्नेछ। हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-04 07:21:10.629570',NULL,'2026-05-04 07:21:10.629575','2026-05-04 07:21:10.629577',1);
INSERT INTO "public_information" VALUES(49,'मौसम सम्बन्धि जानकारी','भोली दिउँसो	
हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।
पहाडी क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।
तराई क्षेत्रमा आंंशिक बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-05 05:10:52.657543',NULL,'2026-05-05 05:10:52.657546','2026-05-05 05:10:52.657547',1);
INSERT INTO "public_information" VALUES(50,'मौसम सम्बन्धि जानकारी','भोली २६ गते हिमाली क्षेत्रमा साधारणतया बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।
पहाडी क्षेत्रमा साधारणतया बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।
तराई क्षेत्रमा आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन चट्याङ्ग सहित हल्का वर्षाको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-08 04:48:51.329471',NULL,'2026-05-08 04:48:51.329473','2026-05-08 04:48:51.329475',1);
INSERT INTO "public_information" VALUES(51,'मौसम सम्बन्धि जानकारी','भोली: हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।
पहाडी क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।
तराई क्षेत्रमा आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-11 04:06:29.680013',NULL,'2026-05-11 04:06:29.680018','2026-05-11 04:06:29.680020',1);
INSERT INTO "public_information" VALUES(52,'मौसम सम्बन्धि जानकारी','भोली सुदुरपश्चिमको हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-14 07:36:08.634471',NULL,'2026-05-14 07:36:08.634475','2026-05-14 07:36:08.634476',1);
INSERT INTO "public_information" VALUES(53,'मौसम सम्बन्धि जानकारी','सुदुरपश्चिमको हिमाली क्षेत्रमा
२ गते: आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । 
३ गते: हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।','General','Low',1,'2026-05-15 04:18:56.145944',NULL,'2026-05-15 04:18:56.145947','2026-05-15 04:18:56.145949',1);
INSERT INTO "public_information" VALUES(54,'मौसम सम्बन्धि जानकारी','सुदुरपश्चिमको हिमाली क्षेत्रमा २ गते:- आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन, चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ भने, ३ गते: हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।','General','Low',1,'2026-05-15 04:20:44.743587',NULL,'2026-05-15 04:20:44.743590','2026-05-15 04:20:44.743596',1);
INSERT INTO "public_information" VALUES(55,'मौसम सम्बन्धि जानकारी','भोली ५ गते हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।
पहाडी क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।
तराई क्षेत्रमा मुख्यतया सफा रही तातो दिनको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-18 08:04:20.139392',NULL,'2026-05-18 08:04:20.139394','2026-05-18 08:04:20.139396',1);
INSERT INTO "public_information" VALUES(56,'मौसम सम्बन्धि जानकारी','भोली ६ गते हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । पहाडी क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ । तराई क्षेत्रमा मुख्यतया सफा रही तातो दिनको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-19 03:56:41.616205',NULL,'2026-05-19 03:56:41.616208','2026-05-19 03:56:41.616210',1);
INSERT INTO "public_information" VALUES(57,'मौसम सम्बन्धि जानकारी','भोली दिउँसो	
हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।
पहाडी क्षेत्रमा आंंशिक बदली रही तातो दिनको सम्भावना रहेकाे छ ।
तराई क्षेत्रमा मुख्यतया सफा रही तातो दिनको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-21 08:19:25.578972',NULL,'2026-05-21 08:19:25.578974','2026-05-21 08:19:25.578976',1);
INSERT INTO "public_information" VALUES(58,'मौसम सम्बन्धि जानकारी','९ गते:- हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।
१० गते:- हिमाली क्षेत्रमा आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षाको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-22 08:50:29.325777',NULL,'2026-05-22 08:50:29.325780','2026-05-22 08:50:29.325785',1);
INSERT INTO "public_information" VALUES(59,'मौसम सम्बन्धि जानकारी','भोली दिउँसो:- हिमाली क्षेत्रमा आंंशिक बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।
राती:- हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-25 05:01:09.153151',NULL,'2026-05-25 05:01:09.153154','2026-05-25 05:01:09.153155',1);
INSERT INTO "public_information" VALUES(60,'मौसम सम्बन्धि जानकारी','१५ गते दिउँसो	
हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । राती	
हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-05-27 04:53:08.816200',NULL,'2026-05-27 04:53:08.816203','2026-05-27 04:53:08.816205',1);
INSERT INTO "public_information" VALUES(61,'विपत सम्वन्धि जानकारी','भोली दिउँसो हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । हिमाली क्षेत्रमा साधारणतया बदली रही एक-दुई स्थानमा मेघगर्जन चट्याङ्ग सहित हल्का वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।','General','Low',1,'2026-06-01 05:30:45.738507',NULL,'2026-06-01 05:30:45.738510','2026-06-01 05:30:45.738511',1);
INSERT INTO "public_information" VALUES(62,'विपत सम्वन्धि जानकारी','सुदूरपश्चिम प्रदेश	दिउँसो	
हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।
राती	
हिमाली क्षेत्रमा साधारणतया बदली रहने छ ।','General','Low',1,'2026-06-02 03:37:42.868245',NULL,'2026-06-02 03:37:42.868248','2026-06-02 03:37:42.868255',1);
INSERT INTO "public_information" VALUES(63,'विपत सम्वन्धि जानकारी','भोली सुदूरपश्चिम प्रदेशमा दिउँसो: हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । राती हिमाली क्षेत्रमा साधारणतया बदली रहने छ ।','General','Low',1,'2026-06-02 03:40:29.324602',NULL,'2026-06-02 03:40:29.324607','2026-06-02 03:40:29.324609',1);
INSERT INTO "public_information" VALUES(64,'विपत सम्वन्धि जानकारी','भोली सुदूरपश्चिम प्रदेशमा दिउँसो: हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ ।   राती: - हिमाली क्षेत्रमा साधारणतया बदली रहने छ ।','General','Low',1,'2026-06-03 06:20:01.297978',NULL,'2026-06-03 06:20:01.297981','2026-06-03 06:20:01.297982',1);
INSERT INTO "public_information" VALUES(65,'विपत सम्वन्धि जानकारी','भोली सुदूरपश्चिम प्रदेशमा दिउँसो: हिमाली क्षेत्रमा साधारणतया बदली रही थोरै स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । राती: - हिमाली क्षेत्रमा साधारणतया बदली रहने छ ।','General','Low',1,'2026-06-04 07:41:22.746674',NULL,'2026-06-04 07:41:22.746677','2026-06-04 07:41:22.746678',1);
INSERT INTO "public_information" VALUES(66,'विपत सम्वन्धि जानकारी','भोली:- सुदूरपश्चिम प्रदेशको हिमाली तथा पहाडी भू-भागका एक -दुई  स्थानमा मेघगर्जन/चट्याङ्ग सहित मध्यमसम्मको वर्षा/हिमपातको सम्भावना रहेको छ','General','Low',1,'2026-06-08 03:36:11.248996',NULL,'2026-06-08 03:36:11.249000','2026-06-08 03:36:11.249006',1);
INSERT INTO "public_information" VALUES(67,'विपत सम्बन्धि जानकारी','भोली:- सुदूरपश्चिम प्रदेशको हिमाली तथा पहाडी भू-भागका एक -दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित मध्यमसम्मको वर्षा/हिमपातको सम्भावना रहेको छ','General','Low',1,'2026-06-09 08:07:06.153510',NULL,'2026-06-09 08:07:06.153513','2026-06-09 08:07:06.153520',1);
INSERT INTO "public_information" VALUES(68,'विपत सम्वन्धि जानकारी','भोली:- सुदूरपश्चिम प्रदेशको हिमाली तथा पहाडी भू-भागका एक -दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित मध्यमसम्मको वर्षा/हिमपातको सम्भावना रहेको छ','General','Low',1,'2026-06-10 06:00:38.813876',NULL,'2026-06-10 06:00:38.813879','2026-06-10 06:00:38.813880',1);
INSERT INTO "public_information" VALUES(69,'विपत सम्वन्धि जानकारी','दिउँसो	
हिमाली क्षेत्रमा आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । राती	
हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।','General','Low',1,'2026-06-15 10:14:23.644003',NULL,'2026-06-15 10:14:23.644006','2026-06-15 10:14:23.644012',1);
INSERT INTO "public_information" VALUES(70,'विपत सम्बन्धि जानकारी','दिउँसो हिमाली क्षेत्रमा आंंशिक बदली रही एक-दुई स्थानमा मेघगर्जन , चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । राती हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।','General','Low',1,'2026-06-16 08:28:33.076928',NULL,'2026-06-16 08:28:33.076931','2026-06-16 08:28:33.076932',1);
INSERT INTO "public_information" VALUES(71,'विपत सम्वन्धि जानकारी','भोली दिउँसो	
हिमाली क्षेत्रमा साधारणतया बदली रही एक-दुई स्थानमा मेघगर्जन, चट्याङ्ग सहित मध्यम वर्षा साथै हल्का हिमपातको सम्भावना रहेकाे छ । राती	
हिमाली क्षेत्रमा आंंशिक बदली रहने छ ।','General','Low',1,'2026-06-22 04:05:21.929463',NULL,'2026-06-22 04:05:21.929468','2026-06-22 04:05:21.929470',1);
CREATE TABLE relief_distribution (
	id INTEGER NOT NULL, 
	beneficiary_name VARCHAR(200) NOT NULL, 
	beneficiary_id VARCHAR(100) NOT NULL, 
	father_name VARCHAR(200), 
	phone VARCHAR(20), 
	disaster_date VARCHAR(10), 
	disaster_type VARCHAR(100), 
	fiscal_year VARCHAR(20), 
	ward INTEGER, 
	tole VARCHAR(200), 
	location VARCHAR(200), 
	latitude FLOAT, 
	longitude FLOAT, 
	current_shelter_location VARCHAR(200), 
	family_members_json TEXT, 
	male_count INTEGER, 
	female_count INTEGER, 
	children_count INTEGER, 
	pregnant_mother_count INTEGER, 
	mother_under_2_baby INTEGER, 
	deaths_during_disaster INTEGER, 
	in_social_security_fund BOOLEAN, 
	ssf_type VARCHAR(100), 
	poverty_card_holder BOOLEAN, 
	harms_json TEXT, 
	bank_account_holder_name VARCHAR(200), 
	bank_account_number VARCHAR(50), 
	bank_name VARCHAR(200), 
	relief_items_json TEXT, 
	cash_received FLOAT, 
	distribution_date DATETIME, 
	status VARCHAR(50), 
	documents TEXT, 
	image_filename VARCHAR(255), 
	notes TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, is_locked BOOLEAN DEFAULT 0, fund_transaction_id INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (beneficiary_id)
);
INSERT INTO "relief_distribution" VALUES(1,'जनक नेपाली दमाई','001','जनक दमाई','0000000','2082-03-24','बाढी','2081/82',5,'कोटफेरा','कोटफेरा',29.466751,81.025281,'आफ्नै घरमा','[]',2,3,0,0,0,0,0,'',0,'[]','JANAK NEPALI DAMAI','1840110979600001','Kumari Bank Ltd','[]',5000.0,'2026-01-29 01:31:57.037451','Distributed',NULL,NULL,'१ रोपनी खेत बगाएको','2026-01-29 01:31:57.037456','2026-02-02 11:21:33.644917',1,NULL);
INSERT INTO "relief_distribution" VALUES(2,'बल बहादुर खत्री','६२१','प्रेम बहादुर खत्री','9768472141','2082-03-24','पहिरो','2081/82',7,'घोडादाउना','घोडादाउना',29.458083,81.063468,'अन्यन्त्र','[]',0,0,0,0,0,0,0,'',0,'[]','BALA BAHADUR KHATRI','1840342559900001','Kumari Bank Ltd','[]',6100.0,'2026-01-29 01:36:52.041886','Distributed',NULL,NULL,'घर भत्किएको र बस्न योग्य नभएको','2026-01-29 01:36:52.041890','2026-02-02 11:21:28.313217',1,NULL);
INSERT INTO "relief_distribution" VALUES(3,'केशवराज गिरी','७११०३८-३१५','इश्वरराज गिरी','9860665417','2082-03-19','पहिरो','2081/82',6,'सेरालागाउँ','सेरालागाउँ',29.467329,81.03256,'आफ्नै घरमा','[]',2,0,0,0,0,0,0,'',0,'[]','Keshab Raj Giri','1840133139500001','Kumari Bank Ltd','[]',9000.0,'2026-01-29 01:45:54.061819','Distributed',NULL,NULL,'१ रोपनी खेत बगाएको','2026-01-29 01:45:54.061824','2026-02-02 11:21:20.843919',1,NULL);
INSERT INTO "relief_distribution" VALUES(4,'देवकी देवी सिहँ','७१३०३६-१८१','जाबिर थापा','9869563012','2082-03-21','बाढी','2081/82',3,'कुच','कुच',29.472946,81.009695,'आफ्नै घरमा','[]',0,1,0,0,0,0,0,'',0,'[]','DEBAKI DEVI SINGH','07505080252881','Nepal Investment MegaBank','[]',5000.0,'2026-01-29 01:50:22.511445','Distributed',NULL,NULL,'दलहन बालीमा क्षित पुर्याएको र खेत भत्काएको','2026-01-29 01:50:22.511450','2026-02-02 11:21:15.828636',1,NULL);
INSERT INTO "relief_distribution" VALUES(5,'अनिसा कुमारी बिष्ट','७११०१६-१९६','कृपा बिष्ट','9767415398','2081-06-20','बाढी','2081/82',3,'कुच','कुच',29.472933,81.009888,'आफ्नै घरमा','[]',0,1,0,0,0,0,0,'',0,'[]','ANISHA KUMARI BIST','07505080252375','Nepal Investment MegaBank','[]',4000.0,'2026-01-29 01:54:43.708877','Distributed',NULL,NULL,'दलहन बालीमा क्षित पुर्याएको र खेत भत्काएको','2026-01-29 01:54:43.708879','2026-02-02 11:21:11.008283',1,NULL);
INSERT INTO "relief_distribution" VALUES(6,'गणेश बहादुर सिहँ','१२५','नरेन्द्र बहादुर सिहँ','9766935157','2081-06-20','बाढी','2081/82',3,'कुच','कुच',29.473244,81.010127,'आफ्नै घरमा','[]',2,0,0,0,0,0,0,'',0,'[]','GANESH BAHADUR SINGH','07505080266918','Nepal Investment MegaBank','[]',5000.0,'2026-01-29 01:58:30.964124','Distributed',NULL,NULL,'दलहन बालीमा क्षित पुर्याएको र खेत भत्काएको','2026-01-29 01:58:30.964128','2026-02-02 11:21:05.791813',1,NULL);
INSERT INTO "relief_distribution" VALUES(7,'इन्द्रा देवी थापा','७१३०३६-१२७','पदम बहादुर बिष्ट','9865751470','2081-06-20','बाढी','2081/82',3,'कुच','कुच',29.472819,81.009498,'आफ्नै घरमा','[]',2,0,0,0,0,0,0,'',0,'[]','INDRA DEVI THAPA','07505080255349','Nepal Investment MegaBank','[]',5000.0,'2026-01-29 02:07:15.610842','Distributed',NULL,NULL,'दलहन बालीमा क्षित पुर्याएको र खेत भत्काएको','2026-01-29 02:07:15.610846','2026-02-02 11:21:00.459198',1,NULL);
INSERT INTO "relief_distribution" VALUES(8,'महामति देवी थापा','७१३०३६-११४','गगन बहादुर भण्डारी','9866523257','2081-06-20','बाढी','2081/82',3,'कुच','कुच',29.472995,81.009588,'आफ्नै घरमा','[]',1,1,0,0,0,0,0,'',0,'[]','MAHAMATI DEVI THAPA','07505080255690','Nepal Investment MegaBank','[]',4000.0,'2026-01-29 02:11:18.481308','Distributed',NULL,NULL,'दलहन बालीमा क्षित पुर्याएको र खेत भत्काएको','2026-01-29 02:11:18.481313','2026-02-02 11:20:55.442891',1,NULL);
INSERT INTO "relief_distribution" VALUES(9,'उत्तरा चन्द सिहँ','७१-०१-७७-०३३७१','टेक बहादुर सिहँ','0000000','2081-06-20','बाढी','2081/82',3,'कुच','कुच',29.473529,81.010098,'आफ्नै घरमा','[]',1,1,0,0,0,0,0,'',0,'[]','MADHURI KUMARI SINGH','07505390250375','Nepal Investment MegaBank','[]',5000.0,'2026-01-29 02:16:17.597593','Distributed',NULL,NULL,'तरकारी र अन्य बालीमा क्षित पुर्याएको र खेत भत्काएको','2026-01-29 02:16:17.597597','2026-02-02 11:20:50.937454',1,NULL);
INSERT INTO "relief_distribution" VALUES(10,'भरत बहादुर चन्द','१००७','बिर बहादुर चन्द','9844818169','2081-06-20','बाढी','2081/82',3,'कुच','कुच',29.473519,81.009792,'आफ्नै घरमा','[]',1,1,0,0,0,0,0,'',0,'[]','NANDA DEVI CHAND','07505050270298','Nepal Investment MegaBank','[]',5000.0,'2026-01-29 02:19:23.328111','Distributed',NULL,NULL,'तरकारी र अन्य बालीमा क्षित पुर्याएको र खेत भत्काएको','2026-01-29 02:19:23.328115','2026-02-02 11:20:46.363326',1,NULL);
INSERT INTO "relief_distribution" VALUES(11,'सरस्वती कुमारी उपाध्या','002','सरस्वती कुमारी उपाध्या','9858491091','2082-04-04','बाढी','2081/82',9,'सिरेटा','सिरेटा',29.488184,81.091758,'आफ्नै घरमा','[]',1,1,0,0,0,0,0,'',0,'[]','SARSWOTI KUMARI UPADHAYAY JOSHI','1840104505800001','Kumari Bank Ltd','[]',5000.0,'2026-01-29 02:26:12.770342','Distributed',NULL,NULL,'२० नाली खेलमा क्षति गरेको','2026-01-29 02:26:12.770347','2026-02-02 11:20:41.821840',1,NULL);
INSERT INTO "relief_distribution" VALUES(12,'पौमले सार्की','८०४२','फगिरे सार्की','0000000','2082-03-24','पहिरो','2081/82',7,'भण्डारीगाउँ','भण्डारीगाउँ',29.456296,81.063749,'छानामा बसिरहेको','[]',1,1,0,0,0,0,0,'',0,'[]','PAUMALE SHARKI','1840144217200002','Kumari Bank Ltd','[]',5500.0,'2026-01-29 02:31:40.982222','Distributed',NULL,NULL,'घर पूर्ण रुपमा भत्किएको','2026-01-29 02:31:40.982225','2026-02-02 11:20:36.496732',1,NULL);
INSERT INTO "relief_distribution" VALUES(13,'जयभान सार्की','३३३९','फगिरे सार्की','0000000','2082-03-24','पहिरो','2081/82',7,'भण्डारीगाउँ','भण्डारीगाउँ',29.45635,81.063635,'छानामा बसिरहेको','[]',1,1,0,0,0,0,0,'',0,'[]','JAYABHAN SHARKI','1840297642600001','Kumari Bank Ltd','[]',5500.0,'2026-01-29 02:34:36.901332','Distributed',NULL,NULL,'घर पूर्ण रुपमा भत्किएको','2026-01-29 02:34:36.901337','2026-02-02 11:20:27.690689',1,NULL);
INSERT INTO "relief_distribution" VALUES(14,'देवीलाल पाध्या','२८२८४','धनराज पाध्या','0000000','2082-03-24','पहिरो','2081/82',7,'घोडादाउना','घोडादाउना',29.457949,81.063372,'टहरामा बसिरहेको','[]',1,1,0,0,0,0,0,'',0,'[]','DEBILAL PADHYA','1840101002600001','Kumari Bank Ltd','[]',5500.0,'2026-01-29 02:37:29.169115','Distributed',NULL,NULL,'घर बस्न योग्य नभएको र टिनको टहरामा बस्दै आएको','2026-01-29 02:37:29.169119','2026-02-02 11:20:15.920686',1,NULL);
INSERT INTO "relief_distribution" VALUES(15,'मन्जु देवी दमाई','७११०३८-१५३','मनविर दमाई','9868496476','2082-07-20','पहिरो','2082/83',5,'कोटफेरा','कोटफेरा',29.466668,81.025515,'छोराको घरमा बसिरहेको','[{"name": "\u092e\u0928\u094d\u091c\u0941 \u0926\u0947\u0935\u0940 \u0926\u092e\u093e\u0908", "relation": "Spouse", "age": 40, "gender": "F"}, {"name": "\u0930\u0928\u093f \u0926\u092e\u093e\u0908", "relation": "Spouse", "age": 42, "gender": "M"}, {"name": "\u0915\u093f\u0938\u094d\u0928\u0947 \u0926\u092e\u093e\u0908", "relation": "Father", "age": 68, "gender": "M"}, {"name": "\u0938\u093f\u0926\u094d\u0926\u0941 \u0926\u0947\u0935\u0940 \u0926\u092e\u093e\u0908", "relation": "Mother", "age": 60, "gender": ""}, {"name": "\u092a\u0941\u091c\u093e \u0915\u0941\u092e\u093e\u0930\u0940 \u0928\u0947\u092a\u093e\u0932\u0940", "relation": "Daughter", "age": 23, "gender": "F"}, {"name": "\u0938\u0928\u093f \u0928\u0947\u092a\u093e\u0932\u0940", "relation": "Son", "age": 14, "gender": "M"}, {"name": "\u092a\u0935\u0928 \u0928\u0947\u092a\u093e\u0932\u0940", "relation": "Son", "age": 16, "gender": "M"}]',2,3,2,0,0,0,0,'',0,'[]','MANJU DEVI DAMAI','1840106210100001','Kumari Bank Ltd','[]',18000.0,'2026-01-29 02:45:36.650554','Distributed','1769663922.246338____.pdf,1769666198.328379____.pdf',NULL,'बर्षाका कारण घर पूर्ण रुपमा क्षति भएको','2026-01-29 02:45:36.650558','2026-02-02 11:20:10.188560',1,NULL);
INSERT INTO "relief_distribution" VALUES(16,'खगेन्द्र राज जैशी ','३६०-७९४-६६१-५','हरिलाल जैशी','9867058575','2082-05-10','अन्य','2082/83',8,'गड्नाउली','थलारा ८ गड्नाउली',29.458721,81.053088,'नातेदारको घरमा वसेको ','[{"name": "\u092d\u0941\u0935\u0928 \u0930\u093e\u091c \u091c\u0948\u0936\u0940", "relation": "Father", "age": 15, "gender": "M"}, {"name": "\u092e\u0928\u094b\u091c \u092a\u094d\u0930\u0936\u093e\u0926 \u091c\u0948\u0936\u0940 ", "relation": "Father", "age": 5, "gender": "M"}, {"name": "\u0936\u093f\u0932\u093e \u0926\u0947\u0935\u0940 \u091c\u0948\u0936\u0940", "relation": "Spouse", "age": 30, "gender": "F"}, {"name": "\u0906\u0938\u093f\u0928\u093e \u091c\u0948\u0936\u0940", "relation": "Father", "age": 8, "gender": "F"}, {"name": "\u091c\u093e\u0928\u0915\u0940 \u0915\u0941 \u091c\u0948\u0936\u0940", "relation": "Father", "age": 10, "gender": "F"}]',3,5,2,0,0,0,0,'',0,'[]','Khagendra Raj Jaishi','1840107033500001','Kumari Bank Ltd','[]',16000.0,'2026-01-29 05:45:09.190038','Distributed','1769665509.183234____.pdf',NULL,'घर चर्केको कारणले पछि गएर घर भत्तेको ','2026-01-29 05:45:09.190041','2026-02-02 11:20:06.093179',1,NULL);
INSERT INTO "relief_distribution" VALUES(17,'तारा देवी बोगटी','३०७८०','खली खड्का','9868590536','2082-09-09','अन्य','2082/83',4,'पलाई','थलारा ४ पलाई',29.46109,80.962457,'नातेदारको घरमा बसिरहेको','[]',0,1,0,0,0,0,0,'',0,'[]','','','','[{"item": "\u0924\u094d\u0930\u093f\u092a\u093e\u0932", "quantity": 1, "unit": "\u0938\u0902\u0916\u094d\u092f\u093e"}, {"item": "\u092a\u093f-\u092b\u092e", "quantity": 1, "unit": "\u0938\u0902\u0916\u094d\u092f\u093e"}, {"item": "\u092c\u0947\u0921 \u0935\u093f\u0938\u094d\u0924\u0930\u093e \u0924\u0928\u094d\u0928\u093e \u0938\u093f\u0930\u093e\u0928\u0940", "quantity": 1, "unit": "\u0938\u0947\u091f"}, {"item": "\u091a\u093e\u092e\u0932", "quantity": 50, "unit": "\u0915\u0947.\u091c\u093f"}, {"item": "\u0915\u0941\u0915\u0930", "quantity": 1, "unit": "\u0938\u0902\u0916\u094d\u092f\u093e"}, {"item": "\u0915\u0930\u093e\u0908", "quantity": 4, "unit": "\u0938\u0902\u0916\u094d\u092f\u093e"}, {"item": "\u0925\u093e\u0932\u0940 \u092a\u093f\u0932\u0947\u091f", "quantity": 3, "unit": "\u0938\u0902\u0916\u094d\u092f\u093e"}, {"item": "\u0915\u091f\u094c\u0930\u093e/\u0932\u094b\u091f\u093e", "quantity": 1, "unit": "\u0938\u0902\u0916\u094d\u092f\u093e"}, {"item": "\u0928\u0941\u0928", "quantity": 2, "unit": "\u0915\u0947.\u091c\u093f"}, {"item": "\u0924\u0947\u0932", "quantity": 3, "unit": "\u0932\u093f"}, {"item": "\u0938\u093e\u092c\u0941\u0928", "quantity": 3, "unit": "\u0938\u0902\u0916\u094d\u092f\u093e"}, {"item": "\u092e\u0938\u0932\u093e", "quantity": 4, "unit": "\u092a\u093e\u0915\u0947\u091f"}]',0.0,'2026-01-29 06:19:38.049825','Distributed','1769667578.046727___compressed.pdf',NULL,'भुकम्पको कारण घर चर्केपछि घर भत्केको','2026-01-29 06:19:38.049827','2026-02-02 11:20:01.174954',1,NULL);
INSERT INTO "relief_distribution" VALUES(18,'भजन दमाई ','711038','नर बहादुर दमाई ','9743500640','2082-07-20','भूकम्प','2082/83',5,'कोटफेरा','थलारा ५ कोटफेरा ',29.466679,81.025463,'नातेदारको घरमा वसेको ','[{"name": "\u091a\u0928\u094d\u0926\u094d\u0930\u093e \u0926\u092e\u093e\u0908 ", "relation": "Spouse", "age": 38, "gender": "F"}, {"name": "\u092a\u094d\u0930\u0935\u093f\u0928 \u0926\u092e\u093e\u0908 ", "relation": "Son", "age": 18, "gender": "M"}, {"name": "\u0932\u0915\u094d\u0937\u094d\u092e\u0940 \u0926\u092e\u093e\u0908 ", "relation": "Other", "age": 18, "gender": "F"}, {"name": "\u0928\u0935\u093f\u0928 \u0926\u092e\u093e\u0908", "relation": "Son", "age": 18, "gender": "M"}, {"name": "\u092d\u091c\u0928 \u0926\u092e\u093e\u0908", "relation": "Other", "age": 39, "gender": "M"}]',3,2,0,0,0,0,0,'',0,'[]','Bhajan  Damai','1840142241500001','कुमारी बैंक लिमिटेड','[]',12000.0,'2026-01-29 06:28:03.319977','Distributed','1769668083.315874____.pdf',NULL,'','2026-01-29 06:28:03.319981','2026-02-02 11:19:56.743912',1,NULL);
INSERT INTO "relief_distribution" VALUES(19,'धर्म राज जैशी','७११-७९१-४५४','शिलाधर जोशी','9848406763','2082-05-10','अन्य','2082/83',8,'गड्नाउली','थलारा ८ गड्नाउली',29.452809,81.053508,'नातेदारको घरमा वसेको ','[{"name": "\u091c\u092f \u0932\u093e\u0932 \u091c\u0948\u0936\u0940 ", "relation": "Brother", "age": 40, "gender": "M"}, {"name": "\u092e\u0939\u0947\u0936 \u0930\u093e\u091c \u091c\u0948\u0936\u0940", "relation": "Father", "age": 18, "gender": "M"}, {"name": "\u0935\u093f\u0938\u094d\u0928\u093e \u0926\u0947\u0935\u0940 \u091c\u0948\u0936\u0940", "relation": "Spouse", "age": 39, "gender": "F"}, {"name": "\u092e\u0928\u093e \u0926\u0947\u0935\u0940 \u091c\u0948\u0936\u0940", "relation": "Daughter", "age": 55, "gender": "F"}, {"name": "\u0932\u0915\u094d\u0937\u094d\u092e\u0940 \u0926\u0947\u0935\u0940 \u091c\u0948\u0936\u0940", "relation": "Brother", "age": 55, "gender": "F"}]',3,3,0,0,0,0,0,'',0,'[]','Dharm Raj Jaishi','184012949481100001','','[]',16000.0,'2026-01-29 07:04:59.966883','Distributed','1769670299.960344____.pdf',NULL,'भूकम्पले घर चर्केको र पछि भत्तेको ','2026-01-29 07:04:59.966888','2026-02-02 11:19:52.467753',1,NULL);
INSERT INTO "relief_distribution" VALUES(20,'रम्भा देवी नेपाली ','१०३०३६/३२६','हरिभक्त दौडे','0000000000','2082-10-12','अन्य','2082/83',4,'डिक्ला ','थलारा ४ डिक्ला ',29.449709,80.98737,'नातेदारको घरमा वसेको ','[{"name": "\u092e\u094b\u0939\u0928 \u0928\u0947\u092a\u093e\u0932\u0940 ", "relation": "Spouse", "age": 50, "gender": "M"}, {"name": "\u092a\u094d\u0930\u0915\u093e\u0936 \u0928\u0947\u092a\u093e\u0932\u0940", "relation": "Son", "age": null, "gender": "M"}, {"name": "\u0930\u0924\u094d\u0928\u093e \u0928\u0947\u092a\u093e\u0932\u0940", "relation": "Other", "age": null, "gender": "F"}, {"name": "\u0909\u092e\u093e \u0928\u0947\u092a\u093e\u0932\u0940", "relation": "Daughter", "age": 10, "gender": "F"}]',6,2,3,0,0,0,0,'',0,'[]','','','','[{"item": "\u0924\u094d\u0930\u093f\u092a\u093e\u0932", "quantity": 1, "unit": " \u092a\u093f\u0938"}, {"item": "\u092a\u093f-\u092b\u092e", "quantity": 1, "unit": "\u092a\u093f\u0938"}, {"item": "\u092c\u0947\u0921 \u0935\u093f\u0938\u094d\u0924\u0930\u093e \u0924\u0928\u094d\u0928\u093e \u0938\u093f\u0930\u093e\u0928\u0940", "quantity": 1, "unit": "\u0938\u0947\u091f"}, {"item": "\u091a\u093e\u092e\u0932", "quantity": 50, "unit": "kg"}, {"item": "\u0915\u0941\u0915\u0930", "quantity": 1, "unit": "\u0935\u091f\u093e "}, {"item": "\u0915\u091f\u094c\u0930\u093e/\u0932\u094b\u091f\u093e", "quantity": 3, "unit": " \u0935\u091f\u093e "}, {"item": "\u0925\u093e\u0932\u0940 \u092a\u093f\u0932\u0947\u091f", "quantity": 4, "unit": "\u0935\u091f\u093e "}, {"item": "\u0935\u093e\u0932\u094d\u091f\u0940\u0928", "quantity": 1, "unit": "\u0935\u091f\u093e "}, {"item": "\u0915\u0930\u093e\u0908", "quantity": 1, "unit": "\u0935\u091f\u093e "}, {"item": "\u091c\u0917", "quantity": 2, "unit": "\u0935\u091f\u093e "}, {"item": "\u0928\u0941\u0928", "quantity": 3, "unit": "kg"}, {"item": "\u0938\u093e\u092c\u0941\u0928", "quantity": 3, "unit": "kg"}, {"item": "\u092e\u0938\u0932\u093e", "quantity": 4, "unit": "\u092a\u093e\u0915\u0947\u091f"}]',0.0,'2026-01-29 07:16:21.828053','Distributed','1769671380.821147____.pdf',NULL,'भूकम्पले घर भत्केको र पछि गएर घर भत्तेको','2026-01-29 07:16:21.828057','2026-02-02 11:19:47.859321',1,NULL);
INSERT INTO "relief_distribution" VALUES(21,'चन्द्र बहादुर रोकाया','१३२','धन बहादुर रोकाया','0000000000','2082-06-30','आगलागी','2082/83',6,'पिखेत','थलारा ६ पिखेत',29.471614,81.029659,'टहरामा बसिरहेको','[]',1,0,0,0,0,0,0,'',0,'[]','','','','[{"item": "\u092a\u093f-\u092b\u092e", "quantity": 4, "unit": "\u0935\u091f\u093e"}, {"item": "\u0915\u0941\u0915\u0930", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u0935\u093e\u0932\u094d\u091f\u0940\u0928", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u091a\u093e\u092e\u0932", "quantity": 2, "unit": "\u0915\u091f\u094d\u091f\u093e"}, {"item": "\u0917\u094d\u092f\u093e\u0901\u0938 \u091a\u0941\u0932\u094b", "quantity": 1, "unit": "\u0938\u0947\u091f"}, {"item": "\u0925\u093e\u0932\u0940 \u092a\u093f\u0932\u0947\u091f", "quantity": 4, "unit": "\u0925\u093e\u0928"}, {"item": "\u0915\u091f\u094c\u0930\u093e/\u0932\u094b\u091f\u093e", "quantity": 5, "unit": "\u0935\u091f\u093e"}, {"item": "\u0924\u094d\u0930\u093f\u092a\u093e\u0932", "quantity": 2, "unit": "\u0925\u093e\u0928"}, {"item": "\u0915\u0930\u093e\u0908", "quantity": 1, "unit": "\u0925\u093e\u0928"}, {"item": "\u092c\u0947\u0921 \u0935\u093f\u0938\u094d\u0924\u0930\u093e \u0924\u0928\u094d\u0928\u093e \u0938\u093f\u0930\u093e\u0928\u0940", "quantity": 2, "unit": "\u0925\u093e\u0928"}, {"item": "\u0932\u093e\u0907\u091f\u0930", "quantity": 1, "unit": "\u092a\u093f\u0938"}, {"item": "\u091a\u0915\u094d\u0915\u0941", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u0921\u0947\u0915", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u0921\u093e\u0921\u0941/\u092a\u0928\u094d\u092f\u0941", "quantity": 1, "unit": "\u0938\u0947\u091f"}, {"item": "\u092c\u0947\u0932\u0928\u093e \u091a\u094b\u0915", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u0924\u0947\u0932", "quantity": 5, "unit": "\u092a\u094b\u0915\u093e"}, {"item": "\u0928\u0941\u0928", "quantity": 2, "unit": "\u0915\u0947.\u091c\u093f"}, {"item": "\u091a\u093f\u0928\u0940", "quantity": 3, "unit": "\u0915\u0947.\u091c\u093f"}, {"item": "\u091a\u093f\u092f\u093e\u092a\u0924\u094d\u0924\u0940", "quantity": 2, "unit": "\u092a\u094d\u092f\u093e\u0915\u0947\u091f"}, {"item": "\u092c\u093f\u0932\u0947\u0919\u094d\u0915\u0947\u091f", "quantity": 2, "unit": "\u0925\u093e\u0928"}, {"item": "\u091a\u093e\u0930\u094d\u091c/\u0938\u0947\u0932 \u0932\u093e\u0907\u091f", "quantity": 1, "unit": "\u092a\u093f\u0938"}]',0.0,'2026-01-29 07:38:25.882702','Distributed','1769672305.875434__.pdf',NULL,'विद्युत सट भएर घरमा आगजनी भएको','2026-01-29 07:38:25.882707','2026-02-02 11:19:43.047818',1,NULL);
INSERT INTO "relief_distribution" VALUES(22,'प्रमानन्द्र पाध्याय','३०३७/३','नन्द्रलाल पाध्याय','9743551196','2082-09-20','आगलागी','2082/83',7,'अदुगालि','थलारा ७ अदुगाली',29.466917,81.058417,'छोराको घरमा बसिरहेको','[{"name": "\u092f\u091c\u094d\u091e\u0930\u093e\u091c \u092a\u093e\u0927\u094d\u092f\u093e\u092f", "relation": "Son", "age": 54, "gender": "M"}, {"name": "\u092e\u0928\u094d\u0926\u093f\u0930\u0947\u0940 \u0926\u0947\u0935\u0940 \u092a\u093e\u0927\u094d\u092f\u093e\u092f", "relation": "Spouse", "age": 24, "gender": "F"}, {"name": "\u0939\u0930\u093f\u0938 \u092a\u093e\u0927\u094d\u092f\u093e\u092f", "relation": "Son", "age": 53, "gender": "M"}, {"name": "\u091a\u0928\u094d\u0926\u094d\u0930 \u0926\u0947\u0935 \u092a\u093e\u0927\u094d\u092f\u093e\u092f", "relation": "Son", "age": 15, "gender": "M"}, {"name": "\u0930\u092e\u093e \u0915\u0941\u092e\u093e\u0930\u0940 \u092a\u093e\u0927\u094d\u092f\u093e\u092f", "relation": "Daughter", "age": 12, "gender": "F"}]',5,2,3,0,0,0,0,'',0,'[]','','','','[{"item": "\u0924\u094d\u0930\u093f\u092a\u093e\u0932", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u092a\u093f-\u092b\u092e", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u092c\u0947\u0921 \u0935\u093f\u0938\u094d\u0924\u0930\u093e \u0924\u0928\u094d\u0928\u093e \u0938\u093f\u0930\u093e\u0928\u0940", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u091a\u093e\u092e\u0932", "quantity": 50, "unit": "kg"}, {"item": "\u0926\u093e\u0932", "quantity": 5, "unit": "kg"}, {"item": "\u0915\u0941\u0915\u0930", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u0925\u093e\u0932\u0940 \u092a\u093f\u0932\u0947\u091f", "quantity": 5, "unit": "\u0935\u091f\u093e"}, {"item": "\u0935\u093e\u0932\u094d\u091f\u0940\u0928", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u091c\u0917", "quantity": 1, "unit": "\u0935\u091f\u093e"}, {"item": "\u0928\u0941\u0928", "quantity": 1, "unit": "\u092a\u094b\u0915\u093e"}, {"item": "\u0924\u0947\u0932", "quantity": 5, "unit": "\u092a\u094b\u0915\u093e"}, {"item": "\u0938\u093e\u092c\u0941\u0928", "quantity": 2, "unit": "\u0935\u091f\u093e"}, {"item": "\u092e\u0938\u0932\u093e", "quantity": 4, "unit": "pic"}]',0.0,'2026-01-29 07:42:01.198531','Distributed','1769672521.194636____.pdf',NULL,'','2026-01-29 07:42:01.198538','2026-02-04 09:32:56.259054',1,NULL);
CREATE TABLE situation_report (
	id INTEGER NOT NULL, 
	report_date DATE, 
	current_situation_summary TEXT, 
	weather_conditions TEXT, 
	detailed_report TEXT, 
	resources_deployed TEXT, 
	next_update_time VARCHAR(20), 
	created_at DATETIME, 
	updated_at DATETIME, 
	is_locked BOOLEAN, 
	PRIMARY KEY (id)
);
INSERT INTO "situation_report" VALUES(1,'2026-02-02','कुनै पनि घटना नरहेको','घाम लागिको','कुनै पनि स्थानमा घटना नघटेको','','२०८२/१०/२० गते विहान १०:०० बजे','2026-02-02 11:01:28.898465','2026-02-02 11:01:28.898468',1);
INSERT INTO "situation_report" VALUES(2,'2026-02-03','सामान्य','हल्का बादल लागेको','कुनै पनि स्थानमा घटना नघटेको','','मिति २०८२/१०/२१ विहान १० वजे','2026-02-03 04:45:41.286415','2026-02-03 04:45:41.286417',1);
INSERT INTO "situation_report" VALUES(3,'2026-02-03','कुनै पनि घटना नरहेको','आशिंक बादल लागेको ','देशका हिमाली भू‍-भागमा साधारणतया बादल लाग्नेछ र गण्डकी, कर्णाली, लुम्बिनी र सुदूरपश्चिम प्रदेश लगायत बाँकी प्रदेशको पहाडी भू-भागमा आंशिक बादल लाग्नेछ र बाँकी तराईका भू-भागमा मौसम मुख्यतया सफा रहेको छ । देशका उच्च पहाडी तथा हिमाली भू‍-भागका थोरै स्थानहरूमा मध्यम हिमपात/वर्षाको सम्भावना रहेको छ ।','','मिति २०८२/१०/२१ वेलुका ३ वजे','2026-02-03 07:22:16.765475','2026-02-03 07:22:16.765477',1);
INSERT INTO "situation_report" VALUES(4,'2026-02-04','कुनै पनि घटना नरहेको','मौसम मुख्यतया सफा रहेको','हाल पश्चिमी न्यूनचापीय प्रणालीको आंशिक प्रभाव रहेको छ ।','','मिति २०८२/१०/२२ दिउसो ५ वजे','2026-02-04 08:54:24.851882','2026-02-04 08:54:24.851884',1);
INSERT INTO "situation_report" VALUES(5,'2026-02-05','कुनै पनि घटना नरहेको',' आज मौसम सफा रहेको छ ।','हाल मौसम प्रणालीको प्रभाव रहेको छैन ।','','मिति २०८२/१०/२३ वेलुका ५ वजे','2026-02-05 09:40:02.779823','2026-02-05 09:40:02.779824',1);
INSERT INTO "situation_report" VALUES(6,'2026-02-06','कुनै पनि घटना नरहेको','आज मौसम सफा रहेको छ ।','आज राती
कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','','मिति २०८२/१०/२५ वेलुका ५ वजे','2026-02-06 06:22:27.421867','2026-02-06 06:22:27.421868',1);
INSERT INTO "situation_report" VALUES(7,'2026-02-06','कुनै पनि घटना नरहेको','सामान्य','आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','','मिति २०८२/१०/२५ वेलुका ५ वजे','2026-02-06 06:26:05.984786','2026-02-06 06:26:05.984789',1);
INSERT INTO "situation_report" VALUES(8,'2026-02-06','कुनै पनि घटना नरहेको','आज मौसम सफा रहेको','आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','','मिति २०८२/१०/२३ वेलुका ५ वजे','2026-02-06 06:27:13.154152','2026-02-06 06:27:13.154154',1);
INSERT INTO "situation_report" VALUES(9,'2026-02-06','कुनै पनि घटना नरहेको','आज मौसम सफा रहेको','आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','','मिति २०८२/१०/२५ दिउसो ५ वजे','2026-02-06 08:15:49.877813','2026-02-06 08:15:49.877815',1);
INSERT INTO "situation_report" VALUES(10,'2026-02-06','कुनै पनि घटना नरहेको','आज मौसम सफा रहेको',' आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','','मिति २०८२/१०/२५ वेलुका ५ वजे','2026-02-06 08:23:49.303071','2026-02-06 08:23:49.303079',1);
INSERT INTO "situation_report" VALUES(11,'2026-02-08','कुनै पनि घटना नरहेको','आज मौसम सफा रहेको','आज राती कर्णाली र सुदूरपश्चिम प्रदेश लगायत कोशी र गण्डकी प्रदेशको उच्च पहाडी र हिमाली भू-भागमा आंशिक बादल लाग्नेछ र बाँकी भू-भागको मौसम मुख्यतया सफा रहेने छ।','','मिति २०८२/१०/२६ वेलुका ५ वजे','2026-02-08 08:12:03.782214','2026-02-08 08:12:03.782215',1);
INSERT INTO "situation_report" VALUES(12,'2026-02-09','कुनै पनि घटना नरहेको','आंशिक बादल लागेको ','हाल पश्चिमी वायूको आंशिक प्रभाव रहको छ । ','','मिति २०८२/१०/२७ वेलुका ५ वजे','2026-02-09 08:25:29.227927','2026-02-09 08:25:29.227929',1);
INSERT INTO "situation_report" VALUES(13,'2026-02-10','कुनै पनि घटना नरहेको','आज आंशिक बादल लागेको','आज कुनै पनि घटना नघटेको','','मिति २०८२/१०/२८ वेलुका ५ वजे','2026-02-10 08:14:45.940362','2026-02-10 08:14:45.940364',1);
INSERT INTO "situation_report" VALUES(14,'2026-02-12','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको ','आज कुनै पनि घटना नघटेको','','मिति २०८२/११/०१ गते वेलुका ५ वजे','2026-02-12 07:27:17.642335','2026-02-12 07:27:17.642337',1);
INSERT INTO "situation_report" VALUES(15,'2026-02-16','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको','विपत सम्बन्धि जानकारीका लागि स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC) सम्पर्क नं. ९७४३५३७२१५   , सम्पर्क व्यक्ति : ९८६५६५४६६५,   ९८४८९७८८००','','','2026-02-16 07:12:31.978642','2026-02-16 07:12:31.978645',1);
INSERT INTO "situation_report" VALUES(16,'2026-02-17','आज कुनै पनि घटना नघटेको','आज मौसम सफा रहेको ','विपत सम्बन्धि जानकारीका लागि स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC) सम्पर्क नं. ९७४३५३७२१५ , सम्पर्क व्यक्ति : ९८६५६५४६६५, ९८४८९७८८००','','मिति २०८२/११/०८ वेलुका ५ वजे','2026-02-17 05:13:19.592938','2026-02-17 05:13:19.592945',1);
INSERT INTO "situation_report" VALUES(17,'2026-02-20','आज कुनै पनि घटना नघटेको','आज मौसम सफा मुख्यतया सफा रहेको छ । ','तराई भू-भागका थोरै स्थानहरूमा तुँवालो रहनेछ। कोशी प्रदेश लगायत बागमती र गण्डकी प्रदेशको हिमाली भू-भागमा आंशिक बादल लाग्नेछ तथा बाँकी भू-भागमा मौसम मुख्यतया सफा रहनेछ।
','','मिति २०८२/११/१० वेलुका ५ वजे','2026-02-20 04:47:56.599824','2026-02-20 04:47:56.599826',1);
INSERT INTO "situation_report" VALUES(18,'2026-02-22','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको ','थलारा गाँउपालिकाको दैनिक विपद् बुलेटन २०८२/११/१०
','','मिति २०८२/११/११ वेलुका ५ वजे','2026-02-22 06:08:37.775193','2026-02-22 06:08:37.775195',1);
INSERT INTO "situation_report" VALUES(19,'2026-02-24','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको','थलारा गाँउपालिकाको दैनिक विपद् बुलेटन २०८२/११/११','',' मिति २०८२/११/१२ वेलुका ५ वजे','2026-02-24 11:44:53.882724','2026-02-24 11:44:53.882727',1);
INSERT INTO "situation_report" VALUES(20,'2026-02-24','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको','थलारा गाँउपालिकाको दैनिक विपद् बुलेटन २०८२/११/११','','मिति २०८२/११/१३ वेलुका ५ वजे','2026-02-24 11:47:57.946145','2026-02-24 11:47:57.946147',1);
INSERT INTO "situation_report" VALUES(21,'2026-02-25','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको','थलारा गाँउपालिकाको दैनिक विपद् बुलेटन २०८२/११/११','','मिति २०८२/११/१४ वेलुका ५ वजे','2026-02-25 09:15:09.909492','2026-02-25 09:15:09.909492',1);
INSERT INTO "situation_report" VALUES(22,'2026-02-26','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको',' थलारा गाँउपालिकाको दैनिक विपद् बुलेटन २०८२/११/११','','मिति २०८२/११/१५ वेलुका ५ वजे','2026-02-26 05:01:41.791020','2026-02-26 05:01:41.791023',1);
INSERT INTO "situation_report" VALUES(23,'2026-02-27','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको','थलारा गाँउपालिकाको दैनिक विपद् बुलेटन २०८२/११/१५','','मिति २०८२/११/१७ वेलुका ५ वजे','2026-02-27 04:38:02.704114','2026-02-27 04:38:02.704116',1);
INSERT INTO "situation_report" VALUES(24,'2026-03-01','आज कुनै पनि घटना नघटेको','मौसम सफा रहेको','थलारा गाँउपालिकाको दैनिक विपद् बुलेटन','','मिति २०८२/११/२५ वेलुका ५ वजे','2026-03-01 04:45:57.063994','2026-03-01 04:45:57.063997',1);
INSERT INTO "situation_report" VALUES(25,'2026-03-09','आज कुनै पनि घटना नघटेको','आंशिक बादल लागेको ','२०८२ फागुन २६ गते (मङ्गलबार)
दिउँसोः  देशभर साधारणतया बादल लाग्नेछ। कोशी, बागमती, गण्डकी र लुम्बिनी प्रदेशको पहाडी र हिमाली भू-भागका थोरै स्थानहरूमा, कर्णाली र सुदूरपश्चिम प्रदेशका पहाडी र हिमाली भू-भाग तथा देशको तराई भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ। ','','मिति २०८२/११/२७ वेलुका ५ वजे','2026-03-09 04:59:39.168421','2026-03-09 04:59:39.168423',1);
INSERT INTO "situation_report" VALUES(26,'2026-03-09','आज कुनै पनि घटना नघटेको','आंशिक बादल लागेको','२०८२ फागुन २६ गते (मङ्गलबार)
दिउँसोः  देशभर साधारणतया बादल लाग्नेछ।  सुदूरपश्चिम प्रदेशका पहाडी र हिमाली भू-भाग तथा देशको
तराई भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ। ','','मिति २०८२/११/२७ वेलुका ५ वजे','2026-03-09 05:02:12.319178','2026-03-09 05:02:12.319180',1);
INSERT INTO "situation_report" VALUES(27,'2026-03-11','आज कुनै पनि घटना नघटेको','आंशिक बादल लागेको','२०८२ फागुन २६ गते (मङ्गलबार) दिउँसोः देशभर साधारणतया बादल लाग्नेछ। सुदूरपश्चिम प्रदेशका पहाडी र हिमाली भू-भाग तथा देशको तराई भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','','मिति २०८२/११/२८ वेलुका ५ वजे','2026-03-11 04:38:17.643636','2026-03-11 04:38:17.643637',1);
INSERT INTO "situation_report" VALUES(28,'2026-03-12','आज कुनै पनि घटना नघटेको','आंशिक बादल लागेको','विपद् सम्बन्धी जानकारीका लागि ','ञ','','2026-03-12 09:33:57.270612','2026-03-12 09:33:57.270614',1);
INSERT INTO "situation_report" VALUES(29,'2026-03-12','विपद् सम्बन्धी जानकारीका लागि','आंशिक बादल लागेको','विपद् सम्बन्धी जानकारीका लागि','','मिति २०८२/११/२९ वेलुका ५ वजे','2026-03-12 09:35:10.034766','2026-03-12 09:35:10.034766',1);
INSERT INTO "situation_report" VALUES(30,'2026-03-12',' कुनै पनि घटना रिर्पोट गरिएको छैन । ','सामान्य तुवालो लागेको ','विपद् सम्बन्धी जानकारीका लागि ','','','2026-03-12 09:38:10.416831','2026-03-12 09:38:10.416833',1);
INSERT INTO "situation_report" VALUES(31,'2026-03-12','कुनै पनि घटना रिर्पोट गरिएको छैन ।','सामान्य तुवालो लागेको','विपद् सम्बन्धी जानकारीका लागि','','मिति २०८२/११/२९ वेलुका ५ वजे','2026-03-12 09:38:42.624546','2026-03-12 09:38:42.624548',1);
INSERT INTO "situation_report" VALUES(32,'2026-03-15','कुनै पनि घटना रिर्पोट गरिएको छैन ।','बादल लागेको छ ।','विपद् सम्बन्धी जानकारीका लागि सम्पर्क न. 9743537215','','मिति २०८२/१२/०२ वेलुका ५ वजे','2026-03-15 04:16:42.841106','2026-03-15 04:16:42.841108',1);
INSERT INTO "situation_report" VALUES(33,'2026-03-16','कुनै पनि घटना रिर्पोट गरिएको छैन ।','आंशिक बादल लागेको',' विपद् सम्बन्धी जानकारीका लागि सम्पर्क न. 9743537215','','मिति २०८२/१२/०३ वेलुका ५ वजे','2026-03-16 07:40:55.892733','2026-03-16 07:40:55.892734',1);
INSERT INTO "situation_report" VALUES(34,'2026-03-17','कुनै पनि घटना रिर्पोट गरिएको छैन ।','आंशिक बादल लागेको','विपद् सम्बन्धी जानकारीका लागि सम्पर्क न. 9743537215','','मिति २०८२/१२/०४ वेलुका ५ वजे','2026-03-17 06:50:00.766037','2026-03-17 06:50:00.766040',1);
INSERT INTO "situation_report" VALUES(35,'2026-03-17','कुनै पनि घटना रिर्पोट गरिएको छैन ।','आंशिक देखि साधारणतया बादल','विपद् सम्बन्धी जानकारीका लागि सम्पर्क न. 9743537215','','मिति २०८२/१२/०४ वेलुका ५ वजे','2026-03-17 06:51:16.874832','2026-03-17 06:51:16.874834',1);
INSERT INTO "situation_report" VALUES(36,'2026-03-18','कुनै पनि घटना रिर्पोट गरिएको छैन ।','आंशिक देखि साधारणतया बादल','विपद् सम्बन्धी जानकारीका लागि सम्पर्क न. 9743537215','','मिति २०८२/१२/०५ वेलुका ५ वजे','2026-03-18 04:45:11.690875','2026-03-18 04:45:11.690877',1);
INSERT INTO "situation_report" VALUES(37,'2026-03-20','कुनै पनि घटना रिर्पोट गरिएको छैन ।','मध्यम लगातार वर्षा भइरहेको',' विपद् सम्बन्धी जानकारीका लागि सम्पर्क न. 9743537215','','','2026-03-20 06:51:18.011313','2026-03-20 06:51:18.011315',1);
INSERT INTO "situation_report" VALUES(38,'2026-03-20','कुनै पनि घटना रिर्पोट गरिएको छैन ।','लगातार मध्यम वर्षा भइरहेको छ । ','विपद् सम्बन्धी जानकारीका लागि सम्पर्क न. 9743537215','','मिति २०८२/१२/०८ वेलुका ५ वजे','2026-03-20 07:01:48.490611','2026-03-20 07:01:48.490612',1);
INSERT INTO "situation_report" VALUES(39,'2026-03-23','भुकम्प','हल्का बादल लागिरहेको','आज दिउसो १:१४ बजे भुकम्पको धक्का महसुस गरिएको','','','2026-03-23 07:50:23.362958','2026-03-23 07:50:23.362959',1);
INSERT INTO "situation_report" VALUES(40,'2026-03-23','आज दिउसो १:१४ बजे भुकम्पको धक्का महसुस गरिएको','हल्का बादल लागिरहेको','आज दिउसो १:१४ बजे भुकम्पको धक्का महसुस गरिएको','','','2026-03-23 07:51:42.692842','2026-03-23 07:51:42.692850',1);
INSERT INTO "situation_report" VALUES(41,'2026-03-24','आँशिक बादल','आँसिक बादल लागिरहेको','देशको पहाडी र हिमाली भु-भागमा आँशिक बादल लाग्नेछ र तराई भू-भागमा मौसम मुख्यतया सफा रहने छ','','','2026-03-24 09:11:36.492725','2026-03-24 09:11:36.492728',1);
INSERT INTO "situation_report" VALUES(42,'2026-03-24','कुनै पनि घटना रिर्पोट गरिएको छैन ।','देशको पहाडी र हिमाली भु-भागमा आँशिक बादल लाग्नेछ र तराई भू-भागमा मौसम मुख्यतया सफा रहने छ','कुनै पनि घटना रिर्पोट गरिएको छैन ।','','मिति २०८२/१२/११ वेलुका ५ वजे','2026-03-24 10:15:14.715495','2026-03-24 10:15:14.715496',1);
INSERT INTO "situation_report" VALUES(43,'2026-03-24','विभिन्न स्थानमा बदली रहि केहि स्थानमा हल्का बर्षा हुन सक्ने','विभिन्न स्थानमा बदली रहि केहि स्थानमा हल्का बर्षा हुन सक्ने','विभिन्न स्थानमा बदली रहि केहि स्थानमा हल्का बर्षा हुन सक्ने','','','2026-03-24 10:15:57.214656','2026-03-24 10:15:57.214658',1);
INSERT INTO "situation_report" VALUES(44,'2026-03-24','घटना नरहेको
','विभिन्न स्थानमा बदली रहि केहि स्थानमा हल्का बर्षा हुन सक्ने
','कुनै पनि घटना प्राप्त नभएको','','मिति २०८२/१२/११ वेलुका ५ वजे','2026-03-24 10:17:05.000254','2026-03-24 10:17:05.000256',1);
INSERT INTO "situation_report" VALUES(45,'2026-03-26','कुनै पनि घटना नरहेको','मौसम सफा रहेको ','कुनै पनि घटना प्राप्त नभएको','','मिति २०८२/१२/१५ वेलुका ५ वजे','2026-03-26 04:51:32.051410','2026-03-26 04:51:32.051412',1);
INSERT INTO "situation_report" VALUES(46,'2026-03-29','कुनै पनि घटना नरहेको','मौसम सफा रहेको','कुनै पनि घटना प्राप्त नभएको','','मिति २०८२/१२/१६ वेलुका ५ वजे','2026-03-29 07:20:34.276422','2026-03-29 07:20:34.276424',1);
INSERT INTO "situation_report" VALUES(47,'2026-03-30','कुनै पनि घटना नरहेको','मौसम सफा रहेको','आज कुनै पनि घटना नरहेको ','','मिति २०८२/१२/१७ वेलुका ५ वजे','2026-03-30 04:46:59.489601','2026-03-30 04:46:59.489603',1);
INSERT INTO "situation_report" VALUES(48,'2026-03-31','कुनै पनि घटना नरहेको','मौसम सफा रहेको','आज कुनै पनि घटना नरहेको','','मिति २०८२/१२/१८ वेलुका ५ वजे','2026-03-31 04:41:03.955191','2026-03-31 04:41:03.955193',1);
INSERT INTO "situation_report" VALUES(49,'2026-04-01','आज कुनै पनि घटना नरहेको','मौसम सफा रहेको','दिउँसोः हिमाली र  पहाडी भू-भागमा आंशिक बादल लाग्नेछ,  तराई भू-भागमा मौसम मुख्यतया सफा रहनेछ।  कोशी, बागमती, गण्डकी, कर्णाली र सुदूरपश्चिम प्रदेशको हिमाली भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','','मिति २०८२/१०/१९ वेलुका ५ वजे','2026-04-01 03:32:57.365272','2026-04-01 03:32:57.365273',1);
INSERT INTO "situation_report" VALUES(50,'2026-04-02','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मौसम मूख्यतया सफा रहेकोछ ','दिउँसोः हिमाली र पहाडी भू-भागमा आंशिक बादल लाग्नेछ, तराई भू-भागमा मौसम मुख्यतया सफा रहनेछ। कोशी, बागमती, गण्डकी, कर्णाली र सुदूरपश्चिम प्रदेशको हिमाली भू-भागका एक-दुई स्थानमा मेघगर्जन/चट्याङ्ग सहित हल्का वर्षा/हिमपातको सम्भावना रहेको छ।','','मिति २०८२/१२/२० वेलुका ५ वजे','2026-04-02 10:29:22.392385','2026-04-02 10:29:22.392387',1);
INSERT INTO "situation_report" VALUES(51,'2026-04-03','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन  ','साधारणतया बदली रहेको छ ','आज कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन  ','','मिति २०८२/१२/२० वेलुका ५ वजे','2026-04-03 06:00:10.197191','2026-04-03 06:00:10.197192',1);
INSERT INTO "situation_report" VALUES(52,'2026-04-06','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','पूर्ण रुपमा बादल लागेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन । ','','मिति २०८२/१२/२४ वेलुका ५ वजे','2026-04-06 08:11:30.016780','2026-04-06 08:11:30.016782',1);
INSERT INTO "situation_report" VALUES(53,'2026-04-07','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','आज मौसम सफा रहेको छ ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८२/१२/२५ वेलुका ५ वजे','2026-04-07 05:34:14.336499','2026-04-07 05:34:14.336500',1);
INSERT INTO "situation_report" VALUES(54,'2026-04-07','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','आज आशिंक बादल लागेको छ ।','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८२/१२/२५ वेलुका ५ वजे','2026-04-07 09:14:56.203345','2026-04-07 09:14:56.203346',1);
INSERT INTO "situation_report" VALUES(55,'2026-04-09','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','आजको मौसम मुख्यतया सफा रहेको छ ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८२/१२/२७ वेलुका ५ वजे','2026-04-09 05:43:58.322659','2026-04-09 05:43:58.322696',1);
INSERT INTO "situation_report" VALUES(56,'2026-04-10','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन',' आज मौसम सफा रहेको छ ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८२/१२/२९ वेलुका ५ वजे','2026-04-10 13:53:21.853051','2026-04-10 13:53:21.853053',1);
INSERT INTO "situation_report" VALUES(57,'2026-04-10','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन',' आज मौसम सफा रहेको छ ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८२/१२/२९ वेलुका ५ वजे','2026-04-10 13:53:21.864972','2026-04-10 13:53:21.864974',1);
INSERT INTO "situation_report" VALUES(58,'2026-04-13','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','आज मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/०२ वेलुका ५ वजे','2026-04-13 04:02:49.128948','2026-04-13 04:02:49.128951',1);
INSERT INTO "situation_report" VALUES(59,'2026-04-15','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','आज मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/०३ वेलुका ५ वजे','2026-04-15 01:13:56.730110','2026-04-15 01:13:56.730112',1);
INSERT INTO "situation_report" VALUES(60,'2026-04-15','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','आज मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/०३ वेलुका ५ वजे','2026-04-15 01:13:56.789876','2026-04-15 01:13:56.789878',1);
INSERT INTO "situation_report" VALUES(61,'2026-04-15','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','आज मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/०३ वेलुका ५ वजे','2026-04-15 01:13:56.795782','2026-04-15 01:13:56.795784',1);
INSERT INTO "situation_report" VALUES(62,'2026-04-16','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/०४ वेलुका ५ वजे','2026-04-16 04:04:18.493312','2026-04-16 04:04:18.493320',1);
INSERT INTO "situation_report" VALUES(63,'2026-04-17','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/०६ वेलुका ५ वजे','2026-04-17 05:29:20.076048','2026-04-17 05:29:20.076050',1);
INSERT INTO "situation_report" VALUES(64,'2026-04-21','कुनै पनि घटना रिपोर्ट प्राप्त भएको छैन','मौसम मुख्यतया सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/०९ वेलुका ५ वजे','2026-04-21 01:57:40.140788','2026-04-21 01:57:40.140791',1);
INSERT INTO "situation_report" VALUES(65,'2026-04-22','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मौसम मुख्यतया सफा रहेको छ',' थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/१० वेलुका ५ वजे','2026-04-22 04:44:20.460631','2026-04-22 04:44:20.460632',1);
INSERT INTO "situation_report" VALUES(66,'2026-04-22','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मौसम मुख्यतया सफा रहेको छ',' थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/१० वेलुका ५ वजे','2026-04-22 04:44:24.015405','2026-04-22 04:44:24.015408',1);
INSERT INTO "situation_report" VALUES(67,'2026-04-22','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मौसम मुख्यतया सफा रहेको छ',' थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/१० वेलुका ५ वजे','2026-04-22 04:44:24.266468','2026-04-22 04:44:24.266470',1);
INSERT INTO "situation_report" VALUES(68,'2026-04-24','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/१४ वेलुका ५ वजे','2026-04-24 06:03:24.136857','2026-04-24 06:03:24.136859',1);
INSERT INTO "situation_report" VALUES(69,'2026-04-27','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मौसम सफा रहेको छ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/१५ वेलुका ५ वजे','2026-04-27 09:07:24.694974','2026-04-27 09:07:24.694976',1);
INSERT INTO "situation_report" VALUES(70,'2026-05-04','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','लगातार वर्षा भइरहेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/२२ वेलुका ५ वजे','2026-05-04 07:17:58.986648','2026-05-04 07:17:58.986650',1);
INSERT INTO "situation_report" VALUES(71,'2026-05-05','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','आंशिक बादल लागेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/२३ वेलुका ५ वजे','2026-05-05 05:10:13.953120','2026-05-05 05:10:13.953122',1);
INSERT INTO "situation_report" VALUES(72,'2026-05-06','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','अधिकांश बदली','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/२४ वेलुका ५ वजे','2026-05-06 09:19:07.051699','2026-05-06 09:19:07.051701',1);
INSERT INTO "situation_report" VALUES(73,'2026-05-08','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मुख्य तया मौसम सफा रहेको छ ',' थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/२८वेलुका ५ वजे','2026-05-08 04:48:03.714452','2026-05-08 04:48:03.714454',1);
INSERT INTO "situation_report" VALUES(74,'2026-05-11','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','अंशिक बदली रहेको छ ।',' थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/२९ वेलुका ५ वजे','2026-05-11 04:05:29.238887','2026-05-11 04:05:29.238889',1);
INSERT INTO "situation_report" VALUES(75,'2026-05-12','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','अंशिक बदली',' थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/३० वेलुका ५ वजे','2026-05-12 06:34:24.892244','2026-05-12 06:34:24.892246',1);
INSERT INTO "situation_report" VALUES(76,'2026-05-13','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मुख्यतया सफा रहेको छ ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०१/३१ वेलुका ५ वजे','2026-05-13 07:32:11.357254','2026-05-13 07:32:11.357256',1);
INSERT INTO "situation_report" VALUES(77,'2026-05-14','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा मौसम ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०२/१ वेलुका ५ वजे','2026-05-14 07:34:18.166261','2026-05-14 07:34:18.166263',1);
INSERT INTO "situation_report" VALUES(78,'2026-05-15','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','आंशिक बदली ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०२/४ वेलुका ५ वजे','2026-05-15 04:14:29.401415','2026-05-15 04:14:29.401417',1);
INSERT INTO "situation_report" VALUES(79,'2026-05-18','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा मौसम ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०२/५ वेलुका ५ वजे','2026-05-18 08:03:33.576980','2026-05-18 08:03:33.576982',1);
INSERT INTO "situation_report" VALUES(80,'2026-05-19','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मुख्यतया सफा ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०२/६ वेलुका ५ वजे','2026-05-19 03:54:36.640356','2026-05-19 03:54:36.640358',1);
INSERT INTO "situation_report" VALUES(81,'2026-05-21','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा मौसम ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०२/८ वेलुका ५ वजे','2026-05-21 08:18:42.629923','2026-05-21 08:18:42.629924',1);
INSERT INTO "situation_report" VALUES(82,'2026-05-22','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मुख्यतया सफा रहेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ।','','मिति २०८३/०२/११ वेलुका ५ वजे','2026-05-22 08:34:50.497853','2026-05-22 08:34:50.497855',1);
INSERT INTO "situation_report" VALUES(83,'2026-05-25','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा रहेको','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन ','','मिति २०८३/०२/१२ वेलुका ५ वजे','2026-05-25 04:57:31.070879','2026-05-25 04:57:31.070881',1);
INSERT INTO "situation_report" VALUES(84,'2026-05-27','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा रहेको','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/१८ वेलुका ५ वजे','2026-05-27 04:51:21.941099','2026-05-27 04:51:21.941100',1);
INSERT INTO "situation_report" VALUES(85,'2026-06-01','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','आंशिक बादल लागेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/१९ वेलुका ५ वजे','2026-06-01 05:10:54.617832','2026-06-01 05:10:54.617834',1);
INSERT INTO "situation_report" VALUES(86,'2026-06-02','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','आंशिक बादल लागेको','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/२० वेलुका ५ वजे','2026-06-02 03:36:32.580982','2026-06-02 03:36:32.580991',1);
INSERT INTO "situation_report" VALUES(87,'2026-06-03','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मुख्यतया सफा रहेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/२१ वेलुका ५ वजे','2026-06-03 06:18:33.745010','2026-06-03 06:18:33.745012',1);
INSERT INTO "situation_report" VALUES(88,'2026-06-04','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','आंशिक बादल ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/२१ वेलुका ५ वजे','2026-06-04 07:40:13.332247','2026-06-04 07:40:13.332249',1);
INSERT INTO "situation_report" VALUES(89,'2026-06-08','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा रहेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/२६ गते वेलुका ५ बजे ','2026-06-08 03:34:50.322914','2026-06-08 03:34:50.322915',1);
INSERT INTO "situation_report" VALUES(90,'2026-06-09','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा रहेको','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/२६ वेलुका ५ वजे','2026-06-09 08:04:35.668261','2026-06-09 08:04:35.668262',1);
INSERT INTO "situation_report" VALUES(91,'2026-06-10','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मुख्यतया सफा ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०२/२८ गते वेलुका ५ बजे ','2026-06-10 05:58:50.327801','2026-06-10 05:58:50.327803',1);
INSERT INTO "situation_report" VALUES(92,'2026-06-15','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','मुख्यतया सफा',' थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०३/०२ गते वेलुका ५ बजे ','2026-06-15 10:13:58.654709','2026-06-15 10:13:58.654712',1);
INSERT INTO "situation_report" VALUES(93,'2026-06-16','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा रहेको ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०३/०३ वेलुका ५ वजे','2026-06-16 08:22:58.893162','2026-06-16 08:22:58.893163',1);
INSERT INTO "situation_report" VALUES(94,'2026-06-18','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा रहेको','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०३/०५ गते वेलुका ५ बजे ','2026-06-18 05:09:42.062916','2026-06-18 05:09:42.062918',1);
INSERT INTO "situation_report" VALUES(95,'2026-06-19','हालसम्म कुनै रिपोर्ट प्राप्त भएको छैन।','सफा ','थलारा गाँउपालिकामा कुनै पनि घटना रिर्पोट प्राप्त भएको छैन','','मिति २०८३/०३/०८ गते वेलुका ५ बजे ','2026-06-19 06:39:10.853637','2026-06-19 06:39:10.853640',1);
INSERT INTO "situation_report" VALUES(96,'2026-06-22','No reports have been received so far.','Clean','No incident reports have been received in Thalara Rural Municipality.','','मिति २०८३/०३/०९ गते वेलुका ५ बजे ','2026-06-22 03:57:18.728937','2026-06-22 03:57:18.728940',1);
CREATE TABLE social_security_beneficiary (
	id INTEGER NOT NULL, 
	beneficiary_name VARCHAR(200) NOT NULL, 
	beneficiary_id VARCHAR(100) NOT NULL, 
	ssf_type VARCHAR(100) NOT NULL, 
	age INTEGER, 
	gender VARCHAR(10), 
	ward INTEGER, 
	tole VARCHAR(200), 
	latitude FLOAT, 
	longitude FLOAT, 
	phone VARCHAR(20), 
	bank_account_holder_name VARCHAR(200), 
	bank_account_number VARCHAR(50), 
	bank_name VARCHAR(200), 
	notes TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, is_locked BOOLEAN DEFAULT 0, 
	PRIMARY KEY (id), 
	UNIQUE (beneficiary_id)
);
CREATE INDEX ix_relief_distribution_status ON relief_distribution (status);
CREATE INDEX ix_relief_distribution_tole ON relief_distribution (tole);
CREATE INDEX ix_relief_distribution_location ON relief_distribution (location);
CREATE INDEX ix_relief_distribution_in_social_security_fund ON relief_distribution (in_social_security_fund);
CREATE INDEX ix_relief_distribution_created_at ON relief_distribution (created_at);
CREATE INDEX ix_relief_distribution_disaster_date ON relief_distribution (disaster_date);
CREATE INDEX ix_relief_distribution_updated_at ON relief_distribution (updated_at);
CREATE INDEX ix_relief_distribution_fiscal_year ON relief_distribution (fiscal_year);
CREATE INDEX ix_relief_distribution_beneficiary_name ON relief_distribution (beneficiary_name);
CREATE INDEX ix_relief_distribution_poverty_card_holder ON relief_distribution (poverty_card_holder);
CREATE INDEX ix_relief_distribution_distribution_date ON relief_distribution (distribution_date);
CREATE INDEX ix_relief_distribution_ward ON relief_distribution (ward);
CREATE INDEX ix_relief_distribution_father_name ON relief_distribution (father_name);
CREATE INDEX ix_relief_distribution_current_shelter_location ON relief_distribution (current_shelter_location);
CREATE INDEX ix_relief_distribution_ssf_type ON relief_distribution (ssf_type);
CREATE INDEX ix_relief_distribution_disaster_type ON relief_distribution (disaster_type);
CREATE INDEX ix_disaster_disaster_date ON disaster (disaster_date);
CREATE INDEX ix_disaster_created_at ON disaster (created_at);
CREATE INDEX ix_disaster_fiscal_year ON disaster (fiscal_year);
CREATE INDEX ix_disaster_updated_at ON disaster (updated_at);
CREATE INDEX ix_disaster_disaster_type ON disaster (disaster_type);
CREATE INDEX ix_disaster_ward ON disaster (ward);
CREATE INDEX ix_disaster_tole ON disaster (tole);
CREATE INDEX ix_social_security_beneficiary_beneficiary_name ON social_security_beneficiary (beneficiary_name);
CREATE INDEX ix_social_security_beneficiary_gender ON social_security_beneficiary (gender);
CREATE INDEX ix_social_security_beneficiary_ward ON social_security_beneficiary (ward);
CREATE INDEX ix_social_security_beneficiary_tole ON social_security_beneficiary (tole);
CREATE INDEX ix_social_security_beneficiary_created_at ON social_security_beneficiary (created_at);
CREATE INDEX ix_social_security_beneficiary_ssf_type ON social_security_beneficiary (ssf_type);
CREATE INDEX ix_social_security_beneficiary_updated_at ON social_security_beneficiary (updated_at);
CREATE INDEX ix_event_log_location ON event_log (location);
CREATE INDEX ix_event_log_created_at ON event_log (created_at);
CREATE INDEX ix_event_log_event_type ON event_log (event_type);
CREATE INDEX ix_event_log_responsible_unit ON event_log (responsible_unit);
CREATE INDEX ix_event_log_status ON event_log (status);
CREATE INDEX ix_event_log_is_locked ON event_log (is_locked);
CREATE INDEX ix_event_log_timestamp ON event_log (timestamp);
CREATE INDEX ix_event_log_updated_at ON event_log (updated_at);
CREATE INDEX ix_situation_report_report_date ON situation_report (report_date);
CREATE INDEX ix_situation_report_updated_at ON situation_report (updated_at);
CREATE INDEX ix_situation_report_created_at ON situation_report (created_at);
CREATE INDEX ix_situation_report_is_locked ON situation_report (is_locked);
CREATE INDEX ix_public_information_updated_at ON public_information (updated_at);
CREATE INDEX ix_public_information_created_at ON public_information (created_at);
CREATE INDEX ix_public_information_priority ON public_information (priority);
CREATE INDEX ix_public_information_is_locked ON public_information (is_locked);
CREATE INDEX ix_public_information_is_active ON public_information (is_active);
CREATE INDEX ix_public_information_info_type ON public_information (info_type);
CREATE UNIQUE INDEX ix_daily_report_log_report_date_bs ON daily_report_log (report_date_bs);
CREATE INDEX ix_inventory_item_name ON inventory_item (name);
CREATE INDEX ix_inventory_item_category ON inventory_item (category);
CREATE INDEX ix_inventory_item_is_locked ON inventory_item (is_locked);
CREATE INDEX ix_inventory_item_updated_at ON inventory_item (updated_at);
CREATE INDEX ix_inventory_item_created_at ON inventory_item (created_at);
CREATE UNIQUE INDEX ix_inventory_item_item_code ON inventory_item (item_code);
CREATE INDEX ix_inventory_item_status ON inventory_item (status);
CREATE INDEX ix_fund_transaction_is_locked ON fund_transaction (is_locked);
CREATE INDEX ix_fund_transaction_transaction_type ON fund_transaction (transaction_type);
COMMIT;
