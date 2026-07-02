BEGIN TRANSACTION;
CREATE TABLE activity_log (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	username VARCHAR(100), 
	action VARCHAR(50) NOT NULL, 
	resource VARCHAR(100), 
	resource_id VARCHAR(50), 
	details TEXT, 
	ip_address VARCHAR(50), 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "activity_log" VALUES(1,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 15:46:32.756160');
INSERT INTO "activity_log" VALUES(2,1,'admin','create','/api/categories',NULL,'TestCat-Log','127.0.0.1','2026-06-18 15:46:32.933997');
INSERT INTO "activity_log" VALUES(3,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 15:47:09.194948');
INSERT INTO "activity_log" VALUES(4,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 15:47:09.214070');
INSERT INTO "activity_log" VALUES(5,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 15:47:09.729533');
INSERT INTO "activity_log" VALUES(6,1,'admin','create','/api/categories',NULL,'TestLogCat','127.0.0.1','2026-06-18 15:47:10.754477');
INSERT INTO "activity_log" VALUES(7,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-18 15:47:11.267168');
INSERT INTO "activity_log" VALUES(8,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-18 15:50:17.747509');
INSERT INTO "activity_log" VALUES(9,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-18 15:50:51.704376');
INSERT INTO "activity_log" VALUES(10,1,'admin','view','/api/users',NULL,NULL,'127.0.0.1','2026-06-18 15:50:57.509421');
INSERT INTO "activity_log" VALUES(11,3,'viewer','login','auth',NULL,'User viewer logged in','127.0.0.1','2026-06-18 15:58:08.179333');
INSERT INTO "activity_log" VALUES(12,3,'viewer','logout','auth',NULL,'User viewer logged out','127.0.0.1','2026-06-18 15:58:08.246935');
INSERT INTO "activity_log" VALUES(13,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 15:58:08.423889');
INSERT INTO "activity_log" VALUES(14,1,'admin','view','/api/users',NULL,NULL,'127.0.0.1','2026-06-18 16:00:18.141145');
INSERT INTO "activity_log" VALUES(15,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:03:36.795242');
INSERT INTO "activity_log" VALUES(16,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-18 16:03:40.887730');
INSERT INTO "activity_log" VALUES(17,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-18 16:03:42.808222');
INSERT INTO "activity_log" VALUES(18,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:03:44.682495');
INSERT INTO "activity_log" VALUES(19,1,'admin','delete','/api/items/65',NULL,NULL,'127.0.0.1','2026-06-18 16:03:53.487656');
INSERT INTO "activity_log" VALUES(20,1,'admin','delete','/api/items/68',NULL,NULL,'127.0.0.1','2026-06-18 16:03:57.439990');
INSERT INTO "activity_log" VALUES(21,1,'admin','view','/api/suppliers',NULL,NULL,'127.0.0.1','2026-06-18 16:04:09.303814');
INSERT INTO "activity_log" VALUES(22,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-18 16:04:09.305314');
INSERT INTO "activity_log" VALUES(23,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-18 16:04:14.395556');
INSERT INTO "activity_log" VALUES(24,1,'admin','create','/api/warehouses',NULL,'LEOC Godam','127.0.0.1','2026-06-18 16:04:56.336851');
INSERT INTO "activity_log" VALUES(25,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-18 16:04:56.360368');
INSERT INTO "activity_log" VALUES(26,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-18 16:04:59.668217');
INSERT INTO "activity_log" VALUES(27,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:05:03.410654');
INSERT INTO "activity_log" VALUES(28,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-18 16:05:24.783114');
INSERT INTO "activity_log" VALUES(29,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:05:28.629394');
INSERT INTO "activity_log" VALUES(30,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:05:28.638643');
INSERT INTO "activity_log" VALUES(31,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:07:55.765891');
INSERT INTO "activity_log" VALUES(32,1,'admin','create','/api/incidents',NULL,'Fire by Electric shot','127.0.0.1','2026-06-18 16:11:53.142970');
INSERT INTO "activity_log" VALUES(33,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:11:53.171699');
INSERT INTO "activity_log" VALUES(34,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:12:33.409007');
INSERT INTO "activity_log" VALUES(35,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:12:33.413227');
INSERT INTO "activity_log" VALUES(36,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:12:37.403972');
INSERT INTO "activity_log" VALUES(37,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:12:44.482895');
INSERT INTO "activity_log" VALUES(38,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:14:33.834129');
INSERT INTO "activity_log" VALUES(39,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:15:02.284616');
INSERT INTO "activity_log" VALUES(40,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:15:32.213787');
INSERT INTO "activity_log" VALUES(41,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:15:59.703054');
INSERT INTO "activity_log" VALUES(42,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:16:06.590930');
INSERT INTO "activity_log" VALUES(43,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:16:06.592616');
INSERT INTO "activity_log" VALUES(44,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:16:08.899246');
INSERT INTO "activity_log" VALUES(45,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:16:10.189442');
INSERT INTO "activity_log" VALUES(46,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:16:12.260833');
INSERT INTO "activity_log" VALUES(47,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:17:37.168032');
INSERT INTO "activity_log" VALUES(48,1,'admin','create','/api/beneficiaries',NULL,'प्रकाश भण्डारी','127.0.0.1','2026-06-18 16:19:42.979085');
INSERT INTO "activity_log" VALUES(49,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:19:43.009836');
INSERT INTO "activity_log" VALUES(50,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:19:55.516586');
INSERT INTO "activity_log" VALUES(51,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 16:22:19.573797');
INSERT INTO "activity_log" VALUES(52,1,'admin','create','/api/incidents',NULL,'Test Flood - Ward 1 - 2083-03-04','127.0.0.1','2026-06-18 16:22:19.586450');
INSERT INTO "activity_log" VALUES(53,1,'admin','create','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:22:19.635886');
INSERT INTO "activity_log" VALUES(54,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:30:51.531771');
INSERT INTO "activity_log" VALUES(55,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:31:09.139844');
INSERT INTO "activity_log" VALUES(56,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:31:09.145372');
INSERT INTO "activity_log" VALUES(57,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:31:15.987124');
INSERT INTO "activity_log" VALUES(58,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:31:41.737441');
INSERT INTO "activity_log" VALUES(59,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:31:41.759959');
INSERT INTO "activity_log" VALUES(60,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:31:49.316163');
INSERT INTO "activity_log" VALUES(61,1,'admin','update','/api/items/36',NULL,'Prusik Loop','127.0.0.1','2026-06-18 16:32:02.814049');
INSERT INTO "activity_log" VALUES(62,1,'admin','create','/api/items',NULL,'Rice Bag','127.0.0.1','2026-06-18 16:33:53.430962');
INSERT INTO "activity_log" VALUES(63,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:33:53.489493');
INSERT INTO "activity_log" VALUES(64,1,'admin','create','/api/items',NULL,'Bed Set','127.0.0.1','2026-06-18 16:34:54.193896');
INSERT INTO "activity_log" VALUES(65,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:34:54.285105');
INSERT INTO "activity_log" VALUES(66,1,'admin','create','/api/items',NULL,'Blanket','127.0.0.1','2026-06-18 16:35:39.574675');
INSERT INTO "activity_log" VALUES(67,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:35:39.644962');
INSERT INTO "activity_log" VALUES(68,1,'admin','create','/api/items',NULL,'Induction Stove','127.0.0.1','2026-06-18 16:36:39.649120');
INSERT INTO "activity_log" VALUES(69,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:36:39.733464');
INSERT INTO "activity_log" VALUES(70,1,'admin','view','/api/suppliers',NULL,NULL,'127.0.0.1','2026-06-18 16:36:41.347322');
INSERT INTO "activity_log" VALUES(71,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-18 16:36:41.350167');
INSERT INTO "activity_log" VALUES(72,1,'admin','create','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-18 16:40:01.044433');
INSERT INTO "activity_log" VALUES(73,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-18 16:40:01.060972');
INSERT INTO "activity_log" VALUES(74,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:40:20.006081');
INSERT INTO "activity_log" VALUES(75,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:40:30.665787');
INSERT INTO "activity_log" VALUES(76,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:40:30.673632');
INSERT INTO "activity_log" VALUES(77,1,'admin','update','/api/relief-requests/1',NULL,NULL,'127.0.0.1','2026-06-18 16:41:28.012980');
INSERT INTO "activity_log" VALUES(78,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:41:28.030832');
INSERT INTO "activity_log" VALUES(79,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:41:30.792979');
INSERT INTO "activity_log" VALUES(80,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:41:41.666923');
INSERT INTO "activity_log" VALUES(81,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:41:43.562945');
INSERT INTO "activity_log" VALUES(82,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:45:45.710487');
INSERT INTO "activity_log" VALUES(83,1,'admin','create','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:46:18.266847');
INSERT INTO "activity_log" VALUES(84,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:46:18.286423');
INSERT INTO "activity_log" VALUES(85,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:46:25.663931');
INSERT INTO "activity_log" VALUES(86,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:46:32.119669');
INSERT INTO "activity_log" VALUES(87,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:46:32.120994');
INSERT INTO "activity_log" VALUES(88,1,'admin','create','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:47:12.255744');
INSERT INTO "activity_log" VALUES(89,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:47:12.283849');
INSERT INTO "activity_log" VALUES(90,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:47:18.538579');
INSERT INTO "activity_log" VALUES(91,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:47:36.955983');
INSERT INTO "activity_log" VALUES(92,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:47:44.773261');
INSERT INTO "activity_log" VALUES(93,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:47:44.779198');
INSERT INTO "activity_log" VALUES(94,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:49:31.312953');
INSERT INTO "activity_log" VALUES(95,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:50:22.323427');
INSERT INTO "activity_log" VALUES(96,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:50:22.330479');
INSERT INTO "activity_log" VALUES(97,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:51:18.378463');
INSERT INTO "activity_log" VALUES(98,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:51:35.582986');
INSERT INTO "activity_log" VALUES(99,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:51:35.593836');
INSERT INTO "activity_log" VALUES(100,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 16:53:56.376902');
INSERT INTO "activity_log" VALUES(101,1,'admin','create','/api/incidents',NULL,'Test','127.0.0.1','2026-06-18 16:53:56.389176');
INSERT INTO "activity_log" VALUES(102,1,'admin','create','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:53:56.429070');
INSERT INTO "activity_log" VALUES(103,1,'admin','update','/api/relief-requests/2',NULL,NULL,'127.0.0.1','2026-06-18 16:53:56.439557');
INSERT INTO "activity_log" VALUES(104,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 16:54:06.474515');
INSERT INTO "activity_log" VALUES(105,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:54:06.487991');
INSERT INTO "activity_log" VALUES(106,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-18 16:54:06.495466');
INSERT INTO "activity_log" VALUES(107,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 16:54:18.204968');
INSERT INTO "activity_log" VALUES(108,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-18 16:54:18.212209');
INSERT INTO "activity_log" VALUES(109,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:54:18.233399');
INSERT INTO "activity_log" VALUES(110,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 16:54:22.494254');
INSERT INTO "activity_log" VALUES(111,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-18 16:54:22.508525');
INSERT INTO "activity_log" VALUES(112,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 16:54:27.727092');
INSERT INTO "activity_log" VALUES(113,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:54:27.765333');
INSERT INTO "activity_log" VALUES(114,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:54:45.937860');
INSERT INTO "activity_log" VALUES(115,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:54:45.946980');
INSERT INTO "activity_log" VALUES(116,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:55:16.876424');
INSERT INTO "activity_log" VALUES(117,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:55:16.884086');
INSERT INTO "activity_log" VALUES(118,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:55:20.813093');
INSERT INTO "activity_log" VALUES(119,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:55:28.042607');
INSERT INTO "activity_log" VALUES(120,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 16:55:45.331555');
INSERT INTO "activity_log" VALUES(121,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-18 16:55:49.156014');
INSERT INTO "activity_log" VALUES(122,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-18 16:55:49.161960');
INSERT INTO "activity_log" VALUES(123,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-18 16:55:54.573597');
INSERT INTO "activity_log" VALUES(124,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-18 16:56:00.229793');
INSERT INTO "activity_log" VALUES(125,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:01:23.174509');
INSERT INTO "activity_log" VALUES(126,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:28:30.767423');
INSERT INTO "activity_log" VALUES(127,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:30:39.023140');
INSERT INTO "activity_log" VALUES(128,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:30:58.566970');
INSERT INTO "activity_log" VALUES(129,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:41:33.519967');
INSERT INTO "activity_log" VALUES(130,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-18 17:43:19.587246');
INSERT INTO "activity_log" VALUES(131,1,'admin','update','/api/wards/1',NULL,'1','127.0.0.1','2026-06-18 17:43:28.227238');
INSERT INTO "activity_log" VALUES(132,1,'admin','update','/api/wards/2',NULL,'2','127.0.0.1','2026-06-18 17:43:31.613695');
INSERT INTO "activity_log" VALUES(133,1,'admin','update','/api/wards/3',NULL,'3','127.0.0.1','2026-06-18 17:43:35.093231');
INSERT INTO "activity_log" VALUES(134,1,'admin','update','/api/wards/4',NULL,'4','127.0.0.1','2026-06-18 17:43:38.588905');
INSERT INTO "activity_log" VALUES(135,1,'admin','update','/api/wards/5',NULL,'5','127.0.0.1','2026-06-18 17:43:40.593074');
INSERT INTO "activity_log" VALUES(136,1,'admin','update','/api/wards/6',NULL,'6','127.0.0.1','2026-06-18 17:43:42.573943');
INSERT INTO "activity_log" VALUES(137,1,'admin','update','/api/wards/7',NULL,'7','127.0.0.1','2026-06-18 17:43:44.452707');
INSERT INTO "activity_log" VALUES(138,1,'admin','update','/api/wards/8',NULL,'8','127.0.0.1','2026-06-18 17:43:46.702188');
INSERT INTO "activity_log" VALUES(139,1,'admin','update','/api/wards/9',NULL,'9','127.0.0.1','2026-06-18 17:43:49.021550');
INSERT INTO "activity_log" VALUES(140,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:47:24.925625');
INSERT INTO "activity_log" VALUES(141,1,'admin','create','/api/daily-bulletins',NULL,NULL,'127.0.0.1','2026-06-18 17:49:08.205928');
INSERT INTO "activity_log" VALUES(142,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-18 17:50:37.347249');
INSERT INTO "activity_log" VALUES(143,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:50:41.496523');
INSERT INTO "activity_log" VALUES(144,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:51:05.353415');
INSERT INTO "activity_log" VALUES(145,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:54:38.526181');
INSERT INTO "activity_log" VALUES(146,1,'admin','update','/api/incidents/2',NULL,'Test Flood - Ward 1 - 2083-03-04','127.0.0.1','2026-06-18 17:54:53.037728');
INSERT INTO "activity_log" VALUES(147,1,'admin','update','/api/incidents/3',NULL,'Test','127.0.0.1','2026-06-18 17:55:05.711029');
INSERT INTO "activity_log" VALUES(148,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-18 17:55:11.139700');
INSERT INTO "activity_log" VALUES(149,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-19 00:03:40.802685');
INSERT INTO "activity_log" VALUES(150,1,'admin','view','/api/users',NULL,NULL,'127.0.0.1','2026-06-19 00:03:46.048696');
INSERT INTO "activity_log" VALUES(151,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:04:47.638782');
INSERT INTO "activity_log" VALUES(152,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:05:41.009057');
INSERT INTO "activity_log" VALUES(153,1,'admin','delete','/api/incidents/3',NULL,NULL,'127.0.0.1','2026-06-19 00:05:48.868349');
INSERT INTO "activity_log" VALUES(154,1,'admin','create','/api/incidents',NULL,'Earthquake','127.0.0.1','2026-06-19 00:09:29.130947');
INSERT INTO "activity_log" VALUES(155,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:09:29.160055');
INSERT INTO "activity_log" VALUES(156,1,'admin','create','/api/daily-bulletins',NULL,NULL,'127.0.0.1','2026-06-19 00:12:33.245013');
INSERT INTO "activity_log" VALUES(157,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:20:05.381216');
INSERT INTO "activity_log" VALUES(158,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:21:23.213731');
INSERT INTO "activity_log" VALUES(159,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:31:05.429877');
INSERT INTO "activity_log" VALUES(160,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:48:25.236238');
INSERT INTO "activity_log" VALUES(161,1,'admin','update','/api/incidents/3',NULL,'Earthquake','127.0.0.1','2026-06-19 00:48:55.126599');
INSERT INTO "activity_log" VALUES(162,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 00:49:01.527629');
INSERT INTO "activity_log" VALUES(163,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-19 00:54:50.680758');
INSERT INTO "activity_log" VALUES(164,1,'admin','create','/api/settings/office_name',NULL,NULL,'127.0.0.1','2026-06-19 00:55:02.660082');
INSERT INTO "activity_log" VALUES(165,1,'admin','create','/api/settings/phone',NULL,NULL,'127.0.0.1','2026-06-19 00:55:02.674716');
INSERT INTO "activity_log" VALUES(166,1,'admin','create','/api/settings/email',NULL,NULL,'127.0.0.1','2026-06-19 00:55:02.690912');
INSERT INTO "activity_log" VALUES(167,1,'admin','create','/api/settings/address',NULL,NULL,'127.0.0.1','2026-06-19 00:55:02.704527');
INSERT INTO "activity_log" VALUES(168,1,'admin','create','/api/settings/default_language',NULL,NULL,'127.0.0.1','2026-06-19 00:55:02.722581');
INSERT INTO "activity_log" VALUES(169,1,'admin','create','/api/settings/report_header',NULL,NULL,'127.0.0.1','2026-06-19 00:55:02.741360');
INSERT INTO "activity_log" VALUES(170,1,'admin','create','/api/settings/report_footer',NULL,NULL,'127.0.0.1','2026-06-19 00:55:02.759021');
INSERT INTO "activity_log" VALUES(171,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:00:08.926751');
INSERT INTO "activity_log" VALUES(172,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:03:36.649365');
INSERT INTO "activity_log" VALUES(173,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:04:10.284997');
INSERT INTO "activity_log" VALUES(174,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:06:59.875393');
INSERT INTO "activity_log" VALUES(175,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:14:37.579254');
INSERT INTO "activity_log" VALUES(176,1,'admin','create','/api/daily-bulletins',NULL,NULL,'127.0.0.1','2026-06-19 01:16:53.527360');
INSERT INTO "activity_log" VALUES(177,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:19:37.876981');
INSERT INTO "activity_log" VALUES(178,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:21:02.194353');
INSERT INTO "activity_log" VALUES(179,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:28:37.888488');
INSERT INTO "activity_log" VALUES(180,1,'admin','update','/api/daily-bulletins/1',NULL,NULL,'127.0.0.1','2026-06-19 01:29:15.699286');
INSERT INTO "activity_log" VALUES(181,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:34:17.553224');
INSERT INTO "activity_log" VALUES(182,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:35:43.886542');
INSERT INTO "activity_log" VALUES(183,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:37:09.972031');
INSERT INTO "activity_log" VALUES(184,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:42:16.731005');
INSERT INTO "activity_log" VALUES(185,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 01:51:54.715005');
INSERT INTO "activity_log" VALUES(186,1,'admin','create','/api/daily-bulletins',NULL,NULL,'127.0.0.1','2026-06-19 01:52:45.315858');
INSERT INTO "activity_log" VALUES(187,1,'admin','delete','/api/daily-bulletins/2',NULL,NULL,'127.0.0.1','2026-06-19 01:57:38.420666');
INSERT INTO "activity_log" VALUES(188,1,'admin','delete','/api/daily-bulletins/1',NULL,NULL,'127.0.0.1','2026-06-19 01:57:42.204910');
INSERT INTO "activity_log" VALUES(189,1,'admin','create','/api/daily-bulletins',NULL,NULL,'127.0.0.1','2026-06-19 02:00:42.838794');
INSERT INTO "activity_log" VALUES(190,1,'admin','update','/api/daily-bulletins/1',NULL,NULL,'127.0.0.1','2026-06-19 02:00:48.388365');
INSERT INTO "activity_log" VALUES(191,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 02:04:44.107275');
INSERT INTO "activity_log" VALUES(192,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 02:13:34.639145');
INSERT INTO "activity_log" VALUES(193,1,'admin','delete','/api/daily-bulletins/1',NULL,NULL,'127.0.0.1','2026-06-19 02:14:29.888770');
INSERT INTO "activity_log" VALUES(194,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 02:15:08.522032');
INSERT INTO "activity_log" VALUES(195,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 02:15:42.622357');
INSERT INTO "activity_log" VALUES(196,1,'admin','create','/api/daily-bulletins',NULL,NULL,'127.0.0.1','2026-06-19 02:16:49.800393');
INSERT INTO "activity_log" VALUES(197,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 02:16:49.914357');
INSERT INTO "activity_log" VALUES(198,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 02:20:27.390465');
INSERT INTO "activity_log" VALUES(199,1,'admin','delete','/api/daily-bulletins/1',NULL,NULL,'127.0.0.1','2026-06-19 02:20:38.445264');
INSERT INTO "activity_log" VALUES(200,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-19 02:20:53.066253');
CREATE TABLE app_settings (
	id INTEGER NOT NULL, 
	setting_key VARCHAR(100) NOT NULL, 
	setting_value TEXT NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (setting_key)
);
INSERT INTO "app_settings" VALUES(1,'relief_items','["खाद्य सामाग्री (Food Packages)", "पानीको बोतल (Water Bottles)", "औषधि सामाग्री (Medical Supplies)", "कम्बल (Blankets)", "लुगा सामाग्री (Clothing)", "स्वास्थ्य सामाग्री (Hygiene Kits)", "घर बनाउने सामाग्री (Shelter Materials)", "बच्चाको हेरचाह (Baby Care)", "अन्य (Other)"]','2026-06-18 14:48:34.043417','2026-06-18 14:48:34.043421');
INSERT INTO "app_settings" VALUES(2,'fiscal_years','["2080/81", "2081/82", "2082/83", "2083/84", "2084/85"]','2026-06-18 14:48:34.046164','2026-06-18 14:48:34.046167');
INSERT INTO "app_settings" VALUES(3,'active_fiscal_year','2081/82','2026-06-18 14:48:34.048629','2026-06-18 14:48:34.048630');
INSERT INTO "app_settings" VALUES(4,'ssf_types','["OAS (बर्षा पेन्सन)", "विधवा (Widow)", "अपाङ्गता (Disabled)", "कोही नभएको (Endangered)", "बाल भत्ता (Child Grant)", "अन्य (Other)"]','2026-06-18 14:48:34.050964','2026-06-18 14:48:34.050965');
INSERT INTO "app_settings" VALUES(5,'disaster_types','["भूकम्प (Earthquake)", "बाढी (Flood)", "पहिरो (Landslide)", "आँधी (Storm)", "आगलागी (Fire)", "अन्य (Other)"]','2026-06-18 14:48:34.053706','2026-06-18 14:48:34.053711');
INSERT INTO "app_settings" VALUES(6,'organization_name','थलारा गाउँपालिका','2026-06-18 14:48:34.056330','2026-06-18 14:48:34.056332');
INSERT INTO "app_settings" VALUES(7,'organization_address','खोली, बझाङ','2026-06-18 14:48:34.058635','2026-06-18 14:48:34.058637');
INSERT INTO "app_settings" VALUES(8,'organization_phone','XXX-XXXXXXX','2026-06-18 14:48:34.061341','2026-06-18 14:48:34.061345');
INSERT INTO "app_settings" VALUES(9,'organization_email','leoc@thalara.gov.np','2026-06-18 14:48:34.063932','2026-06-18 14:48:34.063934');
INSERT INTO "app_settings" VALUES(10,'currency','NPR','2026-06-18 14:48:34.066556','2026-06-18 14:48:34.066558');
INSERT INTO "app_settings" VALUES(11,'language','ne','2026-06-18 14:48:34.069130','2026-06-18 14:48:34.069133');
INSERT INTO "app_settings" VALUES(12,'default_warehouse','','2026-06-18 14:48:34.071717','2026-06-18 14:48:34.071719');
INSERT INTO "app_settings" VALUES(13,'office_name','"थलारा गाउँपालिका बझाङ"','2026-06-18 15:17:12.433857','2026-06-19 00:55:02.656240');
INSERT INTO "app_settings" VALUES(14,'default_language','"Nepali"','2026-06-18 15:17:12.437739','2026-06-18 15:40:35.046190');
INSERT INTO "app_settings" VALUES(15,'phone','""','2026-06-18 15:40:34.985271','2026-06-18 15:40:34.985296');
INSERT INTO "app_settings" VALUES(16,'email','"rosyprakash786@gmail.com"','2026-06-18 15:40:35.006187','2026-06-18 15:40:35.006198');
INSERT INTO "app_settings" VALUES(17,'address','""','2026-06-18 15:40:35.024054','2026-06-18 15:40:35.024068');
INSERT INTO "app_settings" VALUES(18,'report_header','""','2026-06-18 15:40:35.066733','2026-06-18 15:40:35.066746');
INSERT INTO "app_settings" VALUES(19,'report_footer','""','2026-06-18 15:40:35.084512','2026-06-18 15:40:35.084526');
CREATE TABLE beneficiary (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	national_id VARCHAR(100), 
	father_name VARCHAR(200), 
	phone VARCHAR(50), 
	address VARCHAR(300), 
	ward INTEGER, 
	tole VARCHAR(200), 
	current_shelter_location VARCHAR(300), 
	coordinates VARCHAR(100), 
	family_members INTEGER, 
	family_members_json TEXT, 
	in_social_security_fund BOOLEAN, 
	ssf_type VARCHAR(100), 
	poverty_card_holder BOOLEAN, 
	bank_account_holder_name VARCHAR(200), 
	bank_account VARCHAR(100), 
	bank_name VARCHAR(200), 
	mobile_wallet VARCHAR(100), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "beneficiary" VALUES(1,'प्रकाश भण्डारी','166036','मान ब भणडारी','9865654665','थलारा ३',3,'सिमल्लेख','आफ्नै घर','',2,'[{"name": "मान ब भण्डारी", "id": "75", "relation": "Father", "age": 52, "gender": "Male", "is_pregnant": false, "is_disabled": false}, {"name": "श्रेयंस भण्डारी", "id": "1023", "relation": "Son", "age": 3, "gender": "Male", "is_pregnant": false, "is_disabled": false}]',1,'बाल भत्ता (Child Grant)',0,'','','','','',1,'2026-06-18 16:19:42.965488','2026-06-18 16:19:42.965499');
CREATE TABLE bulletin_incidents (
	bulletin_id INTEGER NOT NULL, 
	incident_id INTEGER NOT NULL, 
	PRIMARY KEY (bulletin_id, incident_id), 
	FOREIGN KEY(bulletin_id) REFERENCES daily_bulletin (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id)
);
CREATE TABLE cash_distribution (
	id INTEGER NOT NULL, 
	distribution_no VARCHAR(50) NOT NULL, 
	distribution_date DATE NOT NULL, 
	fund_id INTEGER NOT NULL, 
	incident_id INTEGER NOT NULL, 
	cash_request_id INTEGER, 
	relief_request_id INTEGER, 
	distribution_type VARCHAR(20), 
	total_amount FLOAT NOT NULL, 
	fiscal_year VARCHAR(20), 
	officer VARCHAR(200), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fund_id) REFERENCES cash_fund (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id), 
	FOREIGN KEY(cash_request_id) REFERENCES cash_request (id), 
	FOREIGN KEY(relief_request_id) REFERENCES relief_request (id)
);
CREATE TABLE cash_distribution_beneficiary (
	id INTEGER NOT NULL, 
	distribution_id INTEGER NOT NULL, 
	beneficiary_id INTEGER, 
	name VARCHAR(200) NOT NULL, 
	national_id VARCHAR(100), 
	address VARCHAR(300), 
	phone VARCHAR(50), 
	amount FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(distribution_id) REFERENCES cash_distribution (id), 
	FOREIGN KEY(beneficiary_id) REFERENCES beneficiary (id)
);
CREATE TABLE cash_fund (
	id INTEGER NOT NULL, 
	fund_no VARCHAR(50) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	fiscal_year VARCHAR(20), 
	funding_source VARCHAR(200), 
	allocated_amount FLOAT, 
	current_balance FLOAT, 
	description TEXT, 
	status VARCHAR(20), 
	created_by INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE cash_receipt (
	id INTEGER NOT NULL, 
	receipt_no VARCHAR(50) NOT NULL, 
	receipt_date DATE NOT NULL, 
	fund_id INTEGER NOT NULL, 
	funding_source VARCHAR(200), 
	reference_number VARCHAR(100), 
	voucher_number VARCHAR(100), 
	bank_transaction_no VARCHAR(100), 
	amount_received FLOAT NOT NULL, 
	received_by VARCHAR(200), 
	remarks TEXT, 
	document_file VARCHAR(500), 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fund_id) REFERENCES cash_fund (id)
);
CREATE TABLE cash_request (
	id INTEGER NOT NULL, 
	request_number VARCHAR(50) NOT NULL, 
	request_date DATE NOT NULL, 
	incident_id INTEGER NOT NULL, 
	requesting_office VARCHAR(200), 
	requester_name VARCHAR(200), 
	phone VARCHAR(50), 
	priority VARCHAR(20), 
	requested_amount FLOAT NOT NULL, 
	purpose VARCHAR(100), 
	remarks TEXT, 
	status VARCHAR(20), 
	created_by INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id)
);
CREATE TABLE category (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "category" VALUES(1,'Food',NULL,'2026-06-18 14:48:34.025127');
INSERT INTO "category" VALUES(2,'Shelter',NULL,'2026-06-18 14:48:34.025131');
INSERT INTO "category" VALUES(3,'Relief Supplies',NULL,'2026-06-18 14:48:34.025132');
INSERT INTO "category" VALUES(4,'WASH (Water/Sanitation)',NULL,'2026-06-18 14:48:34.025132');
INSERT INTO "category" VALUES(5,'Education Materials',NULL,'2026-06-18 14:48:34.025133');
INSERT INTO "category" VALUES(6,'Protection Gear',NULL,'2026-06-18 14:48:34.025133');
INSERT INTO "category" VALUES(7,'Fuel & Lubricants',NULL,'2026-06-18 14:48:34.025133');
INSERT INTO "category" VALUES(8,'Construction Materials',NULL,'2026-06-18 14:48:34.025134');
INSERT INTO "category" VALUES(9,'Livestock Supplies',NULL,'2026-06-18 14:48:34.025134');
INSERT INTO "category" VALUES(10,'Clothing & Textiles',NULL,'2026-06-18 14:48:34.025134');
INSERT INTO "category" VALUES(11,'Kitchen & Cooking',NULL,'2026-06-18 14:48:34.025135');
INSERT INTO "category" VALUES(12,'Baby & Child Care',NULL,'2026-06-18 14:48:34.025135');
INSERT INTO "category" VALUES(13,'Other',NULL,'2026-06-18 14:48:34.025135');
INSERT INTO "category" VALUES(14,'Rescue - Search & Rescue Tools',NULL,'2026-06-18 14:48:34.025136');
INSERT INTO "category" VALUES(15,'Rescue - Ropes & Rigging',NULL,'2026-06-18 14:48:34.025136');
INSERT INTO "category" VALUES(16,'Rescue - Cutting & Breaking',NULL,'2026-06-18 14:48:34.025136');
INSERT INTO "category" VALUES(17,'Rescue - Lighting & Signal',NULL,'2026-06-18 14:48:34.025137');
INSERT INTO "category" VALUES(18,'Rescue - Water Rescue',NULL,'2026-06-18 14:48:34.025137');
INSERT INTO "category" VALUES(19,'Rescue - Confined Space',NULL,'2026-06-18 14:48:34.025137');
INSERT INTO "category" VALUES(20,'Medical - Consumables',NULL,'2026-06-18 14:48:34.025137');
INSERT INTO "category" VALUES(21,'Medical - Equipment',NULL,'2026-06-18 14:48:34.025138');
INSERT INTO "category" VALUES(22,'Medical - First Aid',NULL,'2026-06-18 14:48:34.025138');
INSERT INTO "category" VALUES(23,'Medical - Diagnostic',NULL,'2026-06-18 14:48:34.025138');
INSERT INTO "category" VALUES(24,'Medical - Mobility & Transport',NULL,'2026-06-18 14:48:34.025139');
INSERT INTO "category" VALUES(25,'Vehicles - Light',NULL,'2026-06-18 14:48:34.025139');
INSERT INTO "category" VALUES(26,'Vehicles - Heavy',NULL,'2026-06-18 14:48:34.025139');
INSERT INTO "category" VALUES(27,'Vehicles - Water & Air',NULL,'2026-06-18 14:48:34.025140');
INSERT INTO "category" VALUES(28,'Vehicle Parts & Tools',NULL,'2026-06-18 14:48:34.025140');
INSERT INTO "category" VALUES(29,'Preparedness - Communication',NULL,'2026-06-18 14:48:34.025140');
INSERT INTO "category" VALUES(30,'Preparedness - Power & Lighting',NULL,'2026-06-18 14:48:34.025141');
INSERT INTO "category" VALUES(31,'Preparedness - Shelter & Camp',NULL,'2026-06-18 14:48:34.025141');
INSERT INTO "category" VALUES(32,'Preparedness - Water & Sanitation',NULL,'2026-06-18 14:48:34.025141');
INSERT INTO "category" VALUES(33,'Preparedness - Fire Safety',NULL,'2026-06-18 14:48:34.025141');
INSERT INTO "category" VALUES(34,'TestCat-Log',NULL,'2026-06-18 15:46:32.927537');
INSERT INTO "category" VALUES(35,'TestLogCat',NULL,'2026-06-18 15:47:10.744453');
CREATE TABLE daily_bulletin (
	id INTEGER NOT NULL, 
	notice_title VARCHAR(300) NOT NULL, 
	notice_description TEXT, 
	priority VARCHAR(20), 
	report_status VARCHAR(20), 
	valid_from VARCHAR(10) NOT NULL, 
	valid_to VARCHAR(10), 
	weather_status VARCHAR(50), 
	incident_reporting_status VARCHAR(50), 
	next_update_date VARCHAR(10), 
	next_update_time VARCHAR(10), 
	situation_summary TEXT, 
	resources_deployed TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE daily_report_log (
	id INTEGER NOT NULL, 
	report_date_bs VARCHAR(10) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "daily_report_log" VALUES(1,'2083-03-04','2026-06-18 17:31:03.891357');
INSERT INTO "daily_report_log" VALUES(2,'2083-03-05','2026-06-18 17:46:17.147000');
INSERT INTO "daily_report_log" VALUES(3,'2083-03-01','2026-06-18 17:46:32.508434');
CREATE TABLE disaster_assessment (
	id INTEGER NOT NULL, 
	incident_id INTEGER NOT NULL, 
	disaster_type VARCHAR(100) NOT NULL, 
	fiscal_year VARCHAR(20), 
	disaster_date_bs VARCHAR(10), 
	tole VARCHAR(200), 
	deaths INTEGER, 
	missing_persons INTEGER, 
	injured INTEGER, 
	affected_households INTEGER, 
	affected_people INTEGER, 
	affected_people_male INTEGER, 
	affected_people_female INTEGER, 
	house_destroyed INTEGER, 
	house_damaged INTEGER, 
	public_building_destroyed INTEGER, 
	public_building_damaged INTEGER, 
	estimated_loss FLOAT, 
	agriculture_crop_damage TEXT, 
	road_blocked BOOLEAN, 
	electricity_blocked BOOLEAN, 
	communication_blocked BOOLEAN, 
	drinking_water_disrupted BOOLEAN, 
	cattle_lost INTEGER, 
	cattle_injured INTEGER, 
	poultry_lost INTEGER, 
	poultry_injured INTEGER, 
	goats_sheep_lost INTEGER, 
	goats_sheep_injured INTEGER, 
	other_livestock_lost INTEGER, 
	other_livestock_injured INTEGER, 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id)
);
CREATE TABLE dispatch (
	id INTEGER NOT NULL, 
	dispatch_number VARCHAR(50) NOT NULL, 
	date DATE NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	incident_id INTEGER NOT NULL, 
	relief_request_id INTEGER, 
	destination VARCHAR(300), 
	receiver VARCHAR(200), 
	phone VARCHAR(50), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouse (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id), 
	FOREIGN KEY(relief_request_id) REFERENCES relief_request (id)
);
INSERT INTO "dispatch" VALUES(1,'DSP-5753','2026-06-18',1,2,1,'','','','',1,'2026-06-18 16:46:18.243284');
CREATE TABLE dispatch_item (
	id INTEGER NOT NULL, 
	dispatch_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit VARCHAR(50), 
	batch_no VARCHAR(100), 
	expiry_date DATE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(dispatch_id) REFERENCES dispatch (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
);
INSERT INTO "dispatch_item" VALUES(1,1,130,10,'Kg','','2026-06-18');
INSERT INTO "dispatch_item" VALUES(2,1,131,1,'Set','','2026-06-18');
INSERT INTO "dispatch_item" VALUES(3,1,132,2,'Set','','2026-06-18');
INSERT INTO "dispatch_item" VALUES(4,1,133,1,'Piece','','2026-06-18');
CREATE TABLE distribution (
	id INTEGER NOT NULL, 
	distribution_no VARCHAR(50) NOT NULL, 
	dispatch_id INTEGER NOT NULL, 
	incident_id INTEGER NOT NULL, 
	location VARCHAR(300), 
	latitude FLOAT, 
	longitude FLOAT, 
	fiscal_year VARCHAR(20), 
	distribution_date DATE NOT NULL, 
	officer VARCHAR(200), 
	status VARCHAR(20), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(dispatch_id) REFERENCES dispatch (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id)
);
INSERT INTO "distribution" VALUES(1,'DIST-2152',1,2,'',NULL,NULL,'2081/82','2026-06-18','Prakash Bhandari','Completed','',1,'2026-06-18 16:47:12.238268');
CREATE TABLE distribution_beneficiary (
	id INTEGER NOT NULL, 
	distribution_id INTEGER NOT NULL, 
	beneficiary_id INTEGER, 
	family_name VARCHAR(200) NOT NULL, 
	id_number VARCHAR(100), 
	members INTEGER, 
	item VARCHAR(200), 
	quantity INTEGER NOT NULL, 
	status VARCHAR(20), 
	photo VARCHAR(255), 
	document VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(distribution_id) REFERENCES distribution (id), 
	FOREIGN KEY(beneficiary_id) REFERENCES beneficiary (id)
);
INSERT INTO "distribution_beneficiary" VALUES(1,1,NULL,'John','',1,'Rice Bag',10,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(2,1,NULL,'John','',1,'Bed Set',1,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(3,1,NULL,'John','',1,'Blanket',2,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(4,1,NULL,'John','',1,'Induction Stove',1,'Received',NULL,NULL);
CREATE TABLE incident (
	id INTEGER NOT NULL, 
	incident_name VARCHAR(200) NOT NULL, 
	incident_type VARCHAR(100) NOT NULL, 
	ward INTEGER, 
	start_date DATE NOT NULL, 
	status VARCHAR(50), 
	fiscal_year VARCHAR(20), 
	description TEXT, 
	disaster_date_bs VARCHAR(10), 
	incident_time VARCHAR(10), 
	coordinates VARCHAR(100), 
	tole VARCHAR(200), 
	severity VARCHAR(20), 
	affected_people INTEGER, 
	injured INTEGER, 
	deaths INTEGER, 
	missing_persons INTEGER, 
	affected_people_male INTEGER, 
	affected_people_female INTEGER, 
	affected_households INTEGER, 
	house_damaged INTEGER, 
	house_destroyed INTEGER, 
	public_building_damaged INTEGER, 
	public_building_destroyed INTEGER, 
	estimated_loss FLOAT, 
	agriculture_crop_damage TEXT, 
	road_blocked BOOLEAN, 
	electricity_blocked BOOLEAN, 
	communication_blocked BOOLEAN, 
	drinking_water_disrupted BOOLEAN, 
	cattle_lost INTEGER, 
	cattle_injured INTEGER, 
	poultry_lost INTEGER, 
	poultry_injured INTEGER, 
	goats_sheep_lost INTEGER, 
	goats_sheep_injured INTEGER, 
	other_livestock_lost INTEGER, 
	other_livestock_injured INTEGER, 
	rescue_operations TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, weather_status VARCHAR(100), injured_male INTEGER DEFAULT 0, injured_female INTEGER DEFAULT 0, death_male INTEGER DEFAULT 0, death_female INTEGER DEFAULT 0, missing_male INTEGER DEFAULT 0, missing_female INTEGER DEFAULT 0, 
	PRIMARY KEY (id)
);
INSERT INTO "incident" VALUES(1,'Fire by Electric shot','आगलागी (Fire)',6,'2026-06-18','Active','2081/82','','','','','','medium',0,0,0,0,0,0,0,0,0,0,0,0.0,'',0,0,0,0,0,0,0,0,0,0,0,0,'','2026-06-18 16:11:53.128002','2026-06-18 16:11:53.128011',NULL,0,0,0,0,0,0);
INSERT INTO "incident" VALUES(2,'Test Flood - Ward 1 - 2083-03-04','बाढी (Flood)',1,'1969-10-04','Active','2081/82','','2083-03-04','','','','high',0,0,0,0,0,0,0,0,0,0,0,0.0,'',0,0,0,0,0,0,0,0,0,0,0,0,'','2026-06-18 16:22:19.581688','2026-06-18 17:54:53.029010',NULL,0,0,0,0,0,0);
INSERT INTO "incident" VALUES(3,'Earthquake','भूकम्प (Earthquake)',7,'1969-10-05','Active','2081/82','','2083-03-05','06:45','','Anarkholi','high',78,15,3,2,29,36,20,18,4,3,2,980000.0,'Crop damaged',1,1,0,1,10,30,50,29,15,54,5,2,'','2026-06-19 00:09:29.118138','2026-06-19 00:48:55.113870',NULL,15,18,3,4,2,1);
CREATE TABLE inventory (
	id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	reserved_quantity INTEGER, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(item_id) REFERENCES item (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouse (id)
);
INSERT INTO "inventory" VALUES(1,130,1,490,0,'2026-06-18 16:46:18.248944');
INSERT INTO "inventory" VALUES(2,131,1,19,0,'2026-06-18 16:46:18.251497');
INSERT INTO "inventory" VALUES(3,132,1,18,0,'2026-06-18 16:46:18.252827');
INSERT INTO "inventory" VALUES(4,133,1,4,0,'2026-06-18 16:46:18.254104');
CREATE TABLE item (
	id INTEGER NOT NULL, 
	uuid VARCHAR(36), 
	item_code VARCHAR(50), 
	barcode VARCHAR(100), 
	qr_code TEXT, 
	category_id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	local_name VARCHAR(200), 
	description TEXT, 
	unit VARCHAR(50) NOT NULL, 
	minimum_stock INTEGER, 
	max_stock INTEGER, 
	storage_life_days INTEGER, 
	expiry_tracking BOOLEAN, 
	batch_tracking BOOLEAN, 
	serial_tracking BOOLEAN, 
	is_consumable BOOLEAN, 
	is_distributable BOOLEAN, 
	storage_requirement VARCHAR(50), 
	photo VARCHAR(500), 
	status VARCHAR(20), 
	created_by INTEGER, 
	updated_by INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
);
INSERT INTO "item" VALUES(1,'9af79875-b2a2-44b8-ba4f-cea41eb819bf',NULL,NULL,NULL,15,'Cat-1 Rope (Static)',NULL,NULL,'Meter',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036648','2026-06-18 14:48:34.036651');
INSERT INTO "item" VALUES(2,'2020864c-4f42-40c7-90e8-a0b7ce2add46',NULL,NULL,NULL,15,'Cat-2 Rope (Dynamic)',NULL,NULL,'Meter',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036652','2026-06-18 14:48:34.036653');
INSERT INTO "item" VALUES(3,'fe993c6e-3073-4231-8f6a-38b00c9e0246',NULL,NULL,NULL,15,'Webbing Sling (60cm)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036653','2026-06-18 14:48:34.036654');
INSERT INTO "item" VALUES(4,'40df81a6-7152-4526-a016-e8130b3f2d34',NULL,NULL,NULL,15,'Webbing Sling (120cm)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036654','2026-06-18 14:48:34.036655');
INSERT INTO "item" VALUES(5,'81b40681-d92b-4574-84ed-6ed4f3904c1f',NULL,NULL,NULL,15,'Carabiner (Screw Lock)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036655','2026-06-18 14:48:34.036656');
INSERT INTO "item" VALUES(6,'68395200-39c1-4570-811a-9049b194d1ae',NULL,NULL,NULL,15,'Carabiner (Auto Lock)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036656','2026-06-18 14:48:34.036657');
INSERT INTO "item" VALUES(7,'5e692582-99c4-4c95-9fb7-32b95c2d18df',NULL,NULL,NULL,15,'Descender (Figure 8)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036657','2026-06-18 14:48:34.036658');
INSERT INTO "item" VALUES(8,'98306a87-c665-4dcd-b6c4-14a044c5c375',NULL,NULL,NULL,15,'Pulley (Single)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036658','2026-06-18 14:48:34.036658');
INSERT INTO "item" VALUES(9,'e310d14d-8c16-40cf-a567-70dc5c158daa',NULL,NULL,NULL,15,'Pulley (Double)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036659','2026-06-18 14:48:34.036659');
INSERT INTO "item" VALUES(10,'bb589c09-c667-40c0-93f9-692aed9931a3',NULL,NULL,NULL,15,'Harness (Full Body)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036660','2026-06-18 14:48:34.036660');
INSERT INTO "item" VALUES(11,'2332dcf4-66fd-4b58-95ca-b5614ef64211',NULL,NULL,NULL,15,'Harness (Chest)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036661','2026-06-18 14:48:34.036661');
INSERT INTO "item" VALUES(12,'ac49b7ea-4432-4cf3-a9c0-70ef1367570e',NULL,NULL,NULL,14,'Helmet (Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036662','2026-06-18 14:48:34.036662');
INSERT INTO "item" VALUES(13,'a7df81c5-ae3b-4026-a722-878361b42e2e',NULL,NULL,NULL,17,'Headlamp (Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036663','2026-06-18 14:48:34.036663');
INSERT INTO "item" VALUES(14,'7e89827c-d965-402d-8e2e-29a7a79cfc9b',NULL,NULL,NULL,17,'Rescue Flashlight',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036664','2026-06-18 14:48:34.036664');
INSERT INTO "item" VALUES(15,'59d68d3e-ebf9-41c9-b709-5cdcbb131844',NULL,NULL,NULL,17,'Signal Whistle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036665','2026-06-18 14:48:34.036665');
INSERT INTO "item" VALUES(16,'e41cdb00-4807-49b9-9b86-de72f246e67f',NULL,NULL,NULL,14,'Safety Glasses',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036666','2026-06-18 14:48:34.036666');
INSERT INTO "item" VALUES(17,'4a9619a0-8e41-43da-86f8-f671e2983387',NULL,NULL,NULL,14,'Work Gloves (Leather)',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036667','2026-06-18 14:48:34.036667');
INSERT INTO "item" VALUES(18,'4e3d9ccb-1197-42f4-88e9-ef0d26e10e84',NULL,NULL,NULL,14,'Knee Pads',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036668','2026-06-18 14:48:34.036668');
INSERT INTO "item" VALUES(19,'6bbdd945-5e01-4c9d-b214-0fb3bb0da234',NULL,NULL,NULL,16,'Cutting Tool (Bolt Cutter)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036668','2026-06-18 14:48:34.036669');
INSERT INTO "item" VALUES(20,'c98c2e52-56d5-40f5-aa74-eb0d34bbe4ab',NULL,NULL,NULL,16,'Crowbar',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036669','2026-06-18 14:48:34.036670');
INSERT INTO "item" VALUES(21,'786b17ba-df93-4b5a-9a0d-d51381fbb1e4',NULL,NULL,NULL,16,'Sledge Hammer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036670','2026-06-18 14:48:34.036671');
INSERT INTO "item" VALUES(22,'d8fddf42-6ca4-458b-aa24-a2ffc71ee2a5',NULL,NULL,NULL,16,'Hacksaw',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036671','2026-06-18 14:48:34.036672');
INSERT INTO "item" VALUES(23,'11d67845-73d2-4060-867a-7b3e89ce6efc',NULL,NULL,NULL,14,'Shovel (Folding)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036672','2026-06-18 14:48:34.036673');
INSERT INTO "item" VALUES(24,'db7e8ffa-fcf9-4c90-a5d1-7a8eb4e4e8aa',NULL,NULL,NULL,14,'Stretcher (Basket)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036673','2026-06-18 14:48:34.036673');
INSERT INTO "item" VALUES(25,'061c5868-b306-48b6-901c-a778c93db9e7',NULL,NULL,NULL,14,'Stretcher (Foldable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036674','2026-06-18 14:48:34.036674');
INSERT INTO "item" VALUES(26,'cc1a235f-3a47-475f-8ba3-74677e38e030',NULL,NULL,NULL,14,'Spine Board',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036675','2026-06-18 14:48:34.036675');
INSERT INTO "item" VALUES(27,'92e1dbca-1575-4d6d-83c4-c922615759d4',NULL,NULL,NULL,14,'Cervical Collar (Set)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036676','2026-06-18 14:48:34.036677');
INSERT INTO "item" VALUES(28,'6252abc5-aa1e-4270-b0fe-822b424f1a8e',NULL,NULL,NULL,18,'Life Jacket',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036677','2026-06-18 14:48:34.036677');
INSERT INTO "item" VALUES(29,'4982d92d-b216-4f61-804f-afa747873b27',NULL,NULL,NULL,18,'Throw Bag (Water Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036678','2026-06-18 14:48:34.036678');
INSERT INTO "item" VALUES(30,'59de41f5-a0ed-426d-b719-f8af5fc972d6',NULL,NULL,NULL,18,'Rescue Tube',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036679','2026-06-18 14:48:34.036679');
INSERT INTO "item" VALUES(31,'d30cf002-801e-4e6c-b671-850d2d86843e',NULL,NULL,NULL,19,'Gas Detector (Multi)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036680','2026-06-18 14:48:34.036681');
INSERT INTO "item" VALUES(32,'a60f758a-3d81-458d-bdd9-78cff1fcedaf',NULL,NULL,NULL,19,'Tripod Rescue System',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036682','2026-06-18 14:48:34.036682');
INSERT INTO "item" VALUES(33,'26cdd5de-5d55-4bf8-9b37-9415acb4b69d',NULL,NULL,NULL,14,'Come-Along Winch',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036683','2026-06-18 14:48:34.036683');
INSERT INTO "item" VALUES(34,'52e0d1da-063b-483b-9f4e-cdc2e489e8c5',NULL,NULL,NULL,15,'Rope Grab (ASAP)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036684','2026-06-18 14:48:34.036684');
INSERT INTO "item" VALUES(35,'c543ddff-a2c9-4d75-9046-ec754af3b36a',NULL,NULL,NULL,15,'Edge Roller',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036685','2026-06-18 14:48:34.036685');
INSERT INTO "item" VALUES(36,'1cf40c8c-08b4-4bf4-aafb-287ab725af75','','','',15,'Prusik Loop','','','Piece',0,0,0,0,0,0,0,1,'Dry Storage','','Active',NULL,1,'2026-06-18 14:48:34.036686','2026-06-18 16:32:02.785410');
INSERT INTO "item" VALUES(37,'6d151844-0afe-4716-b088-54953366016e',NULL,NULL,NULL,15,'Daisy Chain',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036687','2026-06-18 14:48:34.036687');
INSERT INTO "item" VALUES(38,'924743f0-82b4-4be9-b644-80137c4ff76e',NULL,NULL,NULL,14,'Ratchet Strap (Heavy)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036688','2026-06-18 14:48:34.036688');
INSERT INTO "item" VALUES(39,'c523ae1f-9898-40da-993e-79f78dee908f',NULL,NULL,NULL,14,'Tarp (Waterproof)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036688','2026-06-18 14:48:34.036689');
INSERT INTO "item" VALUES(40,'bd06b68a-dfa3-4b16-a683-f06e935a5e27',NULL,NULL,NULL,21,'Oxygen Cylinder (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036689','2026-06-18 14:48:34.036690');
INSERT INTO "item" VALUES(41,'e1e2d827-44b4-46e0-b94f-cfbeef989e87',NULL,NULL,NULL,21,'Oxygen Regulator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036690','2026-06-18 14:48:34.036691');
INSERT INTO "item" VALUES(42,'d4ba5e65-ebc6-4b8e-9f41-b0064300c380',NULL,NULL,NULL,23,'Pulse Oximeter',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036691','2026-06-18 14:48:34.036692');
INSERT INTO "item" VALUES(43,'9f5f27ff-b2d4-4a46-aba8-51698eb5208b',NULL,NULL,NULL,23,'BP Monitor (Digital)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036692','2026-06-18 14:48:34.036692');
INSERT INTO "item" VALUES(44,'a696aab1-72a5-46b1-ab27-e71e6d786368',NULL,NULL,NULL,23,'Thermometer (Infrared)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036693','2026-06-18 14:48:34.036693');
INSERT INTO "item" VALUES(45,'b537893e-d4e4-4f63-a87b-af1a0fd01c0f',NULL,NULL,NULL,23,'Stethoscope',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036694','2026-06-18 14:48:34.036694');
INSERT INTO "item" VALUES(46,'928792de-666c-41be-86f4-ac5d2fd6ffed',NULL,NULL,NULL,23,'Glucometer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036695','2026-06-18 14:48:34.036695');
INSERT INTO "item" VALUES(47,'6c31c747-1acb-4b80-a551-344b18124c12',NULL,NULL,NULL,21,'Suction Machine',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036696','2026-06-18 14:48:34.036696');
INSERT INTO "item" VALUES(48,'312e5590-b97a-4d55-8075-203505620920',NULL,NULL,NULL,21,'Bag Valve Mask (Adult)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036697','2026-06-18 14:48:34.036697');
INSERT INTO "item" VALUES(49,'3cf65052-bca2-4ff5-bee0-14255c84f258',NULL,NULL,NULL,21,'Bag Valve Mask (Pediatric)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036698','2026-06-18 14:48:34.036698');
INSERT INTO "item" VALUES(50,'7e5ffb0f-b224-46d2-b830-0c9d0b3d2349',NULL,NULL,NULL,21,'Laryngoscope Set',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036699','2026-06-18 14:48:34.036699');
INSERT INTO "item" VALUES(51,'0de28b58-2582-4ac7-ad24-df7b86cb9e56',NULL,NULL,NULL,24,'Stretcher (Ambulance)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036700','2026-06-18 14:48:34.036700');
INSERT INTO "item" VALUES(52,'4c6458ab-4c8d-41c6-a42b-9ae944313c63',NULL,NULL,NULL,24,'Wheelchair',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036700','2026-06-18 14:48:34.036701');
INSERT INTO "item" VALUES(53,'41d8623a-c95f-4e4a-a314-8ce50c4edd3c',NULL,NULL,NULL,24,'Crutches (Pair)',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036701','2026-06-18 14:48:34.036702');
INSERT INTO "item" VALUES(54,'569d6614-f4b1-4908-9679-7a77be6e6716',NULL,NULL,NULL,24,'Walking Frame',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036702','2026-06-18 14:48:34.036703');
INSERT INTO "item" VALUES(55,'df4eb967-6f0d-40b7-a4fa-d39720a1acc0',NULL,NULL,NULL,21,'IV Stand',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036703','2026-06-18 14:48:34.036703');
INSERT INTO "item" VALUES(56,'00d3473d-9b85-42fd-803c-002e9f9f87b6',NULL,NULL,NULL,22,'First Aid Cabinet (Empty)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036704','2026-06-18 14:48:34.036704');
INSERT INTO "item" VALUES(57,'490a31bc-d76b-4827-926b-c6a91493f7b7',NULL,NULL,NULL,22,'Splint Set (SAM)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036705','2026-06-18 14:48:34.036705');
INSERT INTO "item" VALUES(58,'b525a393-0055-4303-9968-45f3465d2b76',NULL,NULL,NULL,22,'Tourniquet (CAT)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036706','2026-06-18 14:48:34.036706');
INSERT INTO "item" VALUES(59,'fbcb41ee-73e9-4a07-89da-dea8585aa1dc',NULL,NULL,NULL,22,'Trauma Shears',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036707','2026-06-18 14:48:34.036707');
INSERT INTO "item" VALUES(60,'c8284d06-20fa-41fe-b47b-178938cb0efb',NULL,NULL,NULL,22,'Medical Backpack (Empty)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036708','2026-06-18 14:48:34.036708');
INSERT INTO "item" VALUES(61,'d0bf3b16-cdf2-4fba-adc0-632efe1dea61',NULL,NULL,NULL,21,'CPR Pocket Mask',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036709','2026-06-18 14:48:34.036709');
INSERT INTO "item" VALUES(62,'7701447b-e717-4725-b60e-e104be6d6fae',NULL,NULL,NULL,21,'Portable Ventilator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036710','2026-06-18 14:48:34.036710');
INSERT INTO "item" VALUES(63,'7012214d-5846-43fa-8d1e-f5525115c892',NULL,NULL,NULL,21,'Defibrillator (AED)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036711','2026-06-18 14:48:34.036711');
INSERT INTO "item" VALUES(64,'0f5beb12-2b30-41bd-b552-528bfee47c9b',NULL,NULL,NULL,21,'Oxygen Tank (Large)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036711','2026-06-18 14:48:34.036712');
INSERT INTO "item" VALUES(66,'9c44726e-812d-4aa7-aea8-dc1075c12a69',NULL,NULL,NULL,25,'SUV (4x4)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036713','2026-06-18 14:48:34.036714');
INSERT INTO "item" VALUES(67,'40d2fafc-efa6-48a3-bd52-d44714de3415',NULL,NULL,NULL,25,'Motorcycle (Dirt)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036714','2026-06-18 14:48:34.036714');
INSERT INTO "item" VALUES(69,'fd716053-4f21-4252-89f4-9251f41aaa10',NULL,NULL,NULL,26,'Cargo Truck (6-Ton)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036716','2026-06-18 14:48:34.036716');
INSERT INTO "item" VALUES(70,'48463f12-e172-40e5-a1ea-343ffa88573c',NULL,NULL,NULL,26,'Cargo Truck (10-Ton)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036717','2026-06-18 14:48:34.036717');
INSERT INTO "item" VALUES(71,'ba4dc5a6-72d7-4cf0-87a4-94609fe0a458',NULL,NULL,NULL,26,'Dump Truck',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036718','2026-06-18 14:48:34.036718');
INSERT INTO "item" VALUES(72,'21e27294-8fb3-4215-8908-39286b325af6',NULL,NULL,NULL,26,'Water Tanker Truck',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036719','2026-06-18 14:48:34.036719');
INSERT INTO "item" VALUES(73,'085bef4a-4e6a-408f-bb31-2d5a92b18aa9',NULL,NULL,NULL,26,'Fuel Tanker',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036720','2026-06-18 14:48:34.036720');
INSERT INTO "item" VALUES(74,'d2584f06-1dc4-4aef-9ae2-0084701e1a24',NULL,NULL,NULL,26,'Bulldozer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036722','2026-06-18 14:48:34.036722');
INSERT INTO "item" VALUES(75,'977bda2e-bb50-4da7-9975-f97dbc9b456c',NULL,NULL,NULL,26,'Excavator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036723','2026-06-18 14:48:34.036723');
INSERT INTO "item" VALUES(76,'d757daf4-f5e7-4901-a366-4b2115889db1',NULL,NULL,NULL,26,'Forklift',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036723','2026-06-18 14:48:34.036724');
INSERT INTO "item" VALUES(77,'45ba64aa-6971-42fa-9290-76739acb56ac',NULL,NULL,NULL,26,'Backhoe Loader',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036724','2026-06-18 14:48:34.036725');
INSERT INTO "item" VALUES(78,'9d962d19-5ff7-4c5a-b564-26a06633c4e8',NULL,NULL,NULL,27,'Outboard Motor (Boat)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036725','2026-06-18 14:48:34.036726');
INSERT INTO "item" VALUES(79,'c21e2d5d-4219-4cbc-a3fd-c12aa92fc7e3',NULL,NULL,NULL,27,'Rescue Boat (Inflatable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036726','2026-06-18 14:48:34.036727');
INSERT INTO "item" VALUES(80,'08f5efe1-7c08-4499-a6f9-2b3f6970ad6a',NULL,NULL,NULL,27,'Drone (Search)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036727','2026-06-18 14:48:34.036727');
INSERT INTO "item" VALUES(81,'4abac88c-bbc3-490f-ad0a-94452fa930c3',NULL,NULL,NULL,28,'Tire (Vehicle)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036728','2026-06-18 14:48:34.036728');
INSERT INTO "item" VALUES(82,'b3c638a7-48cd-4dc3-b6f3-65cd909ff73e',NULL,NULL,NULL,28,'Jump Starter Pack',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036729','2026-06-18 14:48:34.036729');
INSERT INTO "item" VALUES(83,'5d499e05-ad22-48f0-8ace-b8d1c7fd2853',NULL,NULL,NULL,28,'Tow Cable',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036730','2026-06-18 14:48:34.036730');
INSERT INTO "item" VALUES(84,'dd73caca-89e6-4c82-93a4-a968e803ba97',NULL,NULL,NULL,28,'Hydraulic Jack',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036731','2026-06-18 14:48:34.036731');
INSERT INTO "item" VALUES(85,'6c6386a1-e240-4496-9f59-75f9428c600d',NULL,NULL,NULL,28,'Tool Kit (Vehicle)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036732','2026-06-18 14:48:34.036732');
INSERT INTO "item" VALUES(86,'9ce144b1-3f3c-4d6f-bd81-6b871fca7992',NULL,NULL,NULL,28,'Fire Extinguisher (Vehicle)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036733','2026-06-18 14:48:34.036733');
INSERT INTO "item" VALUES(87,'ec98ef11-d7cd-4813-9b8d-7f47353d72a4',NULL,NULL,NULL,25,'Fuel Can (20L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Hazardous',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036733','2026-06-18 14:48:34.036734');
INSERT INTO "item" VALUES(88,'03c6c390-9067-4aa8-bddf-e9ee9b60a262',NULL,NULL,NULL,28,'Warning Triangle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036734','2026-06-18 14:48:34.036735');
INSERT INTO "item" VALUES(89,'bafa7a41-fbfd-482b-b2b6-438b9044ecfa',NULL,NULL,NULL,28,'Safety Vest (Reflective)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036735','2026-06-18 14:48:34.036736');
INSERT INTO "item" VALUES(90,'83e3fd1b-4784-484c-9121-cce4f498a0c3',NULL,NULL,NULL,29,'Satellite Phone',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036736','2026-06-18 14:48:34.036736');
INSERT INTO "item" VALUES(91,'3f416968-d6af-421d-a98d-7174804815e0',NULL,NULL,NULL,29,'Handheld Radio (VHF)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036737','2026-06-18 14:48:34.036737');
INSERT INTO "item" VALUES(92,'72e474b9-068b-41ae-b8ea-d091e8c72261',NULL,NULL,NULL,29,'Handheld Radio (UHF)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036738','2026-06-18 14:48:34.036738');
INSERT INTO "item" VALUES(93,'76f6b523-1b9e-4d18-84e3-05e207671fa2',NULL,NULL,NULL,29,'Base Station Radio',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036739','2026-06-18 14:48:34.036739');
INSERT INTO "item" VALUES(94,'2608c981-11fc-4268-978f-d09ffaf5a9bf',NULL,NULL,NULL,29,'Megaphone (Battery)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036740','2026-06-18 14:48:34.036740');
INSERT INTO "item" VALUES(95,'19f1b98b-d063-48fb-8326-eb67f3c9ce4a',NULL,NULL,NULL,30,'Generator (2kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036741','2026-06-18 14:48:34.036741');
INSERT INTO "item" VALUES(96,'87bd6ff2-3e37-4292-beff-855df2d41bc7',NULL,NULL,NULL,30,'Generator (5kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036742','2026-06-18 14:48:34.036742');
INSERT INTO "item" VALUES(97,'015f60e6-4f8e-458e-af01-271b49734f32',NULL,NULL,NULL,30,'Generator (10kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036743','2026-06-18 14:48:34.036743');
INSERT INTO "item" VALUES(98,'dd13a5f5-39ff-4f4d-bf0a-c8996f1f6d3a',NULL,NULL,NULL,30,'Solar Panel (Portable 100W)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036743','2026-06-18 14:48:34.036744');
INSERT INTO "item" VALUES(99,'c983843c-d551-4e17-bdd6-058211077538',NULL,NULL,NULL,30,'Solar Panel (Portable 300W)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036744','2026-06-18 14:48:34.036745');
INSERT INTO "item" VALUES(100,'4ff8e33d-80e6-4a37-8359-bef4327e22cc',NULL,NULL,NULL,30,'Power Station (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036745','2026-06-18 14:48:34.036745');
INSERT INTO "item" VALUES(101,'b099b9c3-b3b8-4141-80e9-6db00a3e79cc',NULL,NULL,NULL,30,'LED Flood Light',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036746','2026-06-18 14:48:34.036746');
INSERT INTO "item" VALUES(102,'ca538c29-dea9-4c71-9fe8-eb7e66e0bb77',NULL,NULL,NULL,30,'Extension Cable (50m)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036747','2026-06-18 14:48:34.036747');
INSERT INTO "item" VALUES(103,'950b0989-a055-4cc3-bb5c-1f708ac05514',NULL,NULL,NULL,30,'Power Distribution Box',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036748','2026-06-18 14:48:34.036748');
INSERT INTO "item" VALUES(104,'d6710365-fd99-4afc-9024-e0f3778c2201',NULL,NULL,NULL,31,'Camp Tent (10 Person)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036749','2026-06-18 14:48:34.036749');
INSERT INTO "item" VALUES(105,'8bdf9dd4-088c-458e-9e0d-c42c03d93307',NULL,NULL,NULL,31,'Camp Tent (20 Person)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036750','2026-06-18 14:48:34.036750');
INSERT INTO "item" VALUES(106,'41d0e27d-1585-425e-a4ce-6da184d0ee81',NULL,NULL,NULL,31,'Cot (Folding)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036750','2026-06-18 14:48:34.036751');
INSERT INTO "item" VALUES(107,'f943503e-41d6-4d61-9912-181aeae50328',NULL,NULL,NULL,31,'Sleeping Bag',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036751','2026-06-18 14:48:34.036752');
INSERT INTO "item" VALUES(108,'4ff892ae-8c63-4067-bc3c-746741fd1c2f',NULL,NULL,NULL,31,'Camp Table',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036752','2026-06-18 14:48:34.036752');
INSERT INTO "item" VALUES(109,'cf922196-6fbe-425d-88d1-24ecddafdd48',NULL,NULL,NULL,31,'Camp Chair',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036753','2026-06-18 14:48:34.036753');
INSERT INTO "item" VALUES(110,'f88fce93-a2c0-45f4-a534-34c88283a963',NULL,NULL,NULL,32,'Water Bladder (1000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036754','2026-06-18 14:48:34.036754');
INSERT INTO "item" VALUES(111,'abef2207-67ed-4fa1-bb43-8f96affd3404',NULL,NULL,NULL,32,'Water Bladder (2000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036755','2026-06-18 14:48:34.036755');
INSERT INTO "item" VALUES(112,'916136ea-beab-445f-bd11-a5b80d4f5601',NULL,NULL,NULL,32,'Water Treatment Unit (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036756','2026-06-18 14:48:34.036756');
INSERT INTO "item" VALUES(113,'78128ec8-14ac-4f51-b78d-9732a758d494',NULL,NULL,NULL,32,'Water Pump (Submersible)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036757','2026-06-18 14:48:34.036757');
INSERT INTO "item" VALUES(114,'fed220cd-9469-4859-80e6-1be02cb2a1ff',NULL,NULL,NULL,32,'Water Tank (Plastic 500L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036758','2026-06-18 14:48:34.036758');
INSERT INTO "item" VALUES(115,'9912c542-3925-466d-84e9-543150ce8bda',NULL,NULL,NULL,32,'Water Tank (Plastic 1000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036758','2026-06-18 14:48:34.036759');
INSERT INTO "item" VALUES(116,'1d7d2f8c-3bc5-4418-bc03-897485ffecd4',NULL,NULL,NULL,32,'Collapsible Jerry Can (10L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036759','2026-06-18 14:48:34.036760');
INSERT INTO "item" VALUES(117,'fae26343-c228-4d61-a6ae-808980e6f4e0',NULL,NULL,NULL,32,'Portable Toilet',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036762','2026-06-18 14:48:34.036762');
INSERT INTO "item" VALUES(118,'8d01145d-adce-4bcb-904b-28945ca32404',NULL,NULL,NULL,32,'Shower Unit (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036763','2026-06-18 14:48:34.036763');
INSERT INTO "item" VALUES(119,'fdb40968-b474-4a27-adb7-6af8f8be880f',NULL,NULL,NULL,33,'Fire Extinguisher (ABC 6kg)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036764','2026-06-18 14:48:34.036764');
INSERT INTO "item" VALUES(120,'ce9d3978-800d-4d9c-b44c-6db895372ae8',NULL,NULL,NULL,33,'Fire Extinguisher (CO2)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036765','2026-06-18 14:48:34.036765');
INSERT INTO "item" VALUES(121,'6076b296-7c90-4cd6-8517-56974c88a56a',NULL,NULL,NULL,33,'Fire Hose (15m)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036766','2026-06-18 14:48:34.036766');
INSERT INTO "item" VALUES(122,'591ab021-1d28-414e-a08b-15c3f045fab8',NULL,NULL,NULL,33,'Fire Nozzle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036767','2026-06-18 14:48:34.036767');
INSERT INTO "item" VALUES(123,'5ae1e8d9-627e-4a59-9eef-4d1c8eff9859',NULL,NULL,NULL,33,'Fire Blanket',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036767','2026-06-18 14:48:34.036768');
INSERT INTO "item" VALUES(124,'83664279-2fc3-4878-aa3b-35b74aa10b34',NULL,NULL,NULL,33,'Smoke Detector',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036768','2026-06-18 14:48:34.036769');
INSERT INTO "item" VALUES(125,'63fb8bfc-64ae-4e9f-a4ba-f55fac9fbfe0',NULL,NULL,NULL,31,'First Aid Kit (Workplace)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036769','2026-06-18 14:48:34.036770');
INSERT INTO "item" VALUES(126,'820e6c19-9256-47bb-b44d-62e58f26e9b6',NULL,NULL,NULL,31,'Emergency Whistle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036770','2026-06-18 14:48:34.036771');
INSERT INTO "item" VALUES(127,'d4cf76ec-296f-45a1-966a-8eb2c5a0ef5e',NULL,NULL,NULL,31,'Dust Mask (N95)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036771','2026-06-18 14:48:34.036771');
INSERT INTO "item" VALUES(128,'530aa4b8-c86b-480a-a987-7f60de4e9242',NULL,NULL,NULL,31,'Safety Goggles',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036772','2026-06-18 14:48:34.036772');
INSERT INTO "item" VALUES(129,'a691beda-9965-46fe-afde-f593fde32c43',NULL,NULL,NULL,31,'Rain Poncho',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036773','2026-06-18 14:48:34.036773');
INSERT INTO "item" VALUES(130,'683d84fd-3007-4463-bbbb-63316723f510','ITM-0130','111','',1,'Rice Bag','चामल','','Kg',0,0,365,1,0,0,0,1,'Cold Storage','','Active',1,NULL,'2026-06-18 16:33:53.423948','2026-06-18 16:33:53.423955');
INSERT INTO "item" VALUES(131,'fc7a6885-2b5e-4b2a-ae5e-596542ca9133','ITM-0131','','',10,'Bed Set','बिस्तरा','','Set',0,0,0,0,0,0,0,1,'','','Active',1,NULL,'2026-06-18 16:34:54.185869','2026-06-18 16:34:54.185878');
INSERT INTO "item" VALUES(132,'2b34b38a-3200-432f-abe7-6846013e1c93','ITM-0132','','',10,'Blanket','बिलेङ्केट','','Set',0,0,0,0,0,0,0,1,'','','Active',1,NULL,'2026-06-18 16:35:39.566560','2026-06-18 16:35:39.566569');
INSERT INTO "item" VALUES(133,'6fe449b9-2e2b-4a60-878a-931da6cdccbe','ITM-0133','','',11,'Induction Stove','इन्डक्सन चुलो','','Piece',0,0,0,0,0,0,0,1,'Normal','','Active',1,NULL,'2026-06-18 16:36:39.641387','2026-06-18 16:36:39.641398');
CREATE TABLE manual_adjustment (
	id INTEGER NOT NULL, 
	adjustment_no VARCHAR(50) NOT NULL, 
	date DATE NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	adjustment_type VARCHAR(20) NOT NULL, 
	reason VARCHAR(100), 
	current_quantity INTEGER, 
	adjusted_quantity INTEGER NOT NULL, 
	remarks TEXT, 
	approval_user VARCHAR(200), 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouse (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
);
CREATE TABLE relief_request (
	id INTEGER NOT NULL, 
	request_number VARCHAR(50) NOT NULL, 
	request_date DATE NOT NULL, 
	incident_id INTEGER NOT NULL, 
	organization VARCHAR(200), 
	requester_name VARCHAR(200), 
	phone VARCHAR(50), 
	priority VARCHAR(20), 
	requested_cash_amount FLOAT, 
	distributed_cash_amount FLOAT, 
	cash_purpose VARCHAR(100), 
	remarks TEXT, 
	status VARCHAR(20), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id)
);
INSERT INTO "relief_request" VALUES(1,'REQ-0001','1969-10-04',2,'Test Org','John','','High',0.0,0.0,'','','Completed','2026-06-18 16:22:19.626552');
INSERT INTO "relief_request" VALUES(2,'REQ-0002','1969-10-04',1,'Org','John',NULL,'High',0.0,0.0,NULL,NULL,'Completed','2026-06-18 16:53:56.395390');
CREATE TABLE relief_request_item (
	id INTEGER NOT NULL, 
	request_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	quantity_requested INTEGER NOT NULL, 
	quantity_dispatched INTEGER, 
	unit VARCHAR(50), 
	PRIMARY KEY (id), 
	FOREIGN KEY(request_id) REFERENCES relief_request (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
);
INSERT INTO "relief_request_item" VALUES(1,1,130,10,10,'Kg');
INSERT INTO "relief_request_item" VALUES(2,1,131,1,1,'Set');
INSERT INTO "relief_request_item" VALUES(3,1,132,2,2,'Set');
INSERT INTO "relief_request_item" VALUES(4,1,133,1,1,'Piece');
INSERT INTO "relief_request_item" VALUES(5,2,1,10,0,NULL);
CREATE TABLE stock_receipt (
	id INTEGER NOT NULL, 
	receipt_no VARCHAR(50) NOT NULL, 
	date DATE NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	supplier_id INTEGER, 
	source_type VARCHAR(50) NOT NULL, 
	source_name VARCHAR(200), 
	source_contact VARCHAR(200), 
	phone VARCHAR(50), 
	email VARCHAR(100), 
	address TEXT, 
	ref_number VARCHAR(100), 
	invoice_no VARCHAR(100), 
	invoice_date DATE, 
	delivery_note VARCHAR(100), 
	vehicle_no VARCHAR(50), 
	received_by INTEGER, 
	verified_by VARCHAR(200), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouse (id), 
	FOREIGN KEY(supplier_id) REFERENCES supplier (id)
);
INSERT INTO "stock_receipt" VALUES(1,'RCPT-604096','2026-06-18',1,NULL,'Local Government','Thalara Rural Municipality','Bharat Rokaya','','','Kholi','125','120','2026-06-15','','',NULL,'Madhav Joshi','',1,'2026-06-18 16:40:01.023963');
CREATE TABLE stock_receipt_attachment (
	id INTEGER NOT NULL, 
	receipt_id INTEGER NOT NULL, 
	filename VARCHAR(500) NOT NULL, 
	original_name VARCHAR(500), 
	file_type VARCHAR(50), 
	file_size INTEGER, 
	uploaded_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(receipt_id) REFERENCES stock_receipt (id)
);
CREATE TABLE stock_receipt_item (
	id INTEGER NOT NULL, 
	receipt_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit VARCHAR(50), 
	batch_no VARCHAR(100), 
	serial_no VARCHAR(100), 
	mfg_date DATE, 
	expiry_date DATE, 
	unit_cost FLOAT, 
	total_cost FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(receipt_id) REFERENCES stock_receipt (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
);
INSERT INTO "stock_receipt_item" VALUES(1,1,130,500,'Kg','555','11223','2026-06-18','2027-06-17',40.0,20000.0);
INSERT INTO "stock_receipt_item" VALUES(2,1,131,20,'Set','210','22365','2026-06-18','2026-06-18',6000.0,120000.0);
INSERT INTO "stock_receipt_item" VALUES(3,1,132,20,'Set','156','45662','2026-06-18','2026-06-18',5000.0,100000.0);
INSERT INTO "stock_receipt_item" VALUES(4,1,133,5,'Piece','25','61221','2026-06-18','2026-06-18',4500.0,22500.0);
CREATE TABLE stock_transfer (
	id INTEGER NOT NULL, 
	transfer_no VARCHAR(50) NOT NULL, 
	from_warehouse_id INTEGER NOT NULL, 
	to_warehouse_id INTEGER NOT NULL, 
	transfer_date DATE NOT NULL, 
	reason VARCHAR(300), 
	remarks TEXT, 
	approved_by VARCHAR(200), 
	status VARCHAR(20), 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(from_warehouse_id) REFERENCES warehouse (id), 
	FOREIGN KEY(to_warehouse_id) REFERENCES warehouse (id)
);
CREATE TABLE stock_transfer_item (
	id INTEGER NOT NULL, 
	transfer_id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit VARCHAR(20), 
	batch_no VARCHAR(100), 
	PRIMARY KEY (id), 
	FOREIGN KEY(transfer_id) REFERENCES stock_transfer (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
);
CREATE TABLE supplier (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	contact_person VARCHAR(200), 
	phone VARCHAR(50), 
	email VARCHAR(100), 
	address VARCHAR(300), 
	supplier_type VARCHAR(50), 
	status VARCHAR(20), 
	remarks TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE "user" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                full_name VARCHAR(200),
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            );
INSERT INTO "user" VALUES(1,'admin','scrypt:32768:8:1$k2COQgO3yfRx8BQg$8a5c1bac376ee6f0072ceb442c1d4977ac1015cea64f807bb6ba764af6ab64a7aebe69823e9c39dc4be493da3bd2d08267805abb7ed629316c9c5b2de8953e0a','admin','System Administrator',1,'2026-06-18 14:48:34','2026-06-19 00:03:40.797148+00:00');
INSERT INTO "user" VALUES(2,'editor','scrypt:32768:8:1$hynLA0mcsu8D5kPk$712ddee14ef8818957809fb38f30fdb10c12cd99a06880a09289aacdb8ebcfd3bcfa949874072395ea01105427ff56588f798711767fac3e963b29f5535f938e','editor','Data Editor',1,'2026-06-18 14:48:34',NULL);
INSERT INTO "user" VALUES(3,'viewer','scrypt:32768:8:1$7hQSQyYmbn9YKOFI$37499c3b9d25af0379fa361416c879e5f00ff363d23cd5a6fc041debc2b3f9f509bb5bbb7c8f8e2072c4b16e4d70439966e17ee19bf5fa3c3d22263e28017d47','viewer','Read Only User',1,'2026-06-18 14:48:34','2026-06-18 15:58:08.173404+00:00');
INSERT INTO "user" VALUES(4,'operator','scrypt:32768:8:1$RyqQpHSR3rk8tthg$225d5e6230b42e979ab46a67a9326b1009de4befe51ddd6f8d059ab0f92f2bc3f6d48da6bb73417af67872d9bc000b97b6b4cb617e5664d46d25de8fa105f71a','operator','Operations Officer',1,'2026-06-18 14:48:34',NULL);
INSERT INTO "user" VALUES(5,'finance','scrypt:32768:8:1$jGVYGN6ZWYtvvElG$e96bc8a4b2adf810e6c33ff36eff00333eecedf6d0c68b0fc1d33796129a2225de6889f9a93c8ae01b9ea8905b6ecbc4c2e0d612ba9c90c1577592de8debd04b','finance','Finance Officer',1,'2026-06-18 14:48:34',NULL);
CREATE TABLE ward (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	sort_order INTEGER, 
	PRIMARY KEY (id)
);
INSERT INTO "ward" VALUES(1,'1',1);
INSERT INTO "ward" VALUES(2,'2',2);
INSERT INTO "ward" VALUES(3,'3',3);
INSERT INTO "ward" VALUES(4,'4',4);
INSERT INTO "ward" VALUES(5,'5',5);
INSERT INTO "ward" VALUES(6,'6',6);
INSERT INTO "ward" VALUES(7,'7',7);
INSERT INTO "ward" VALUES(8,'8',8);
INSERT INTO "ward" VALUES(9,'9',9);
CREATE TABLE warehouse (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	address VARCHAR(300), 
	contact_person VARCHAR(200), 
	phone VARCHAR(50), 
	capacity FLOAT, 
	remarks TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "warehouse" VALUES(1,'LEOC Godam','TRM-WH1','Kholi','Bharat Rokaya','',1000.0,'','2026-06-18 16:04:56.327339','2026-06-18 16:04:56.327347');
CREATE TABLE warehouse_zone (
	id INTEGER NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	code VARCHAR(50), 
	capacity FLOAT, 
	description TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouse (id)
);
CREATE UNIQUE INDEX ix_warehouse_code ON warehouse (code);
CREATE INDEX ix_supplier_name ON supplier (name);
CREATE UNIQUE INDEX ix_category_name ON category (name);
CREATE INDEX ix_incident_fiscal_year ON incident (fiscal_year);
CREATE INDEX ix_incident_incident_type ON incident (incident_type);
CREATE INDEX ix_incident_status ON incident (status);
CREATE UNIQUE INDEX ix_daily_report_log_report_date_bs ON daily_report_log (report_date_bs);
CREATE UNIQUE INDEX ix_cash_fund_fund_no ON cash_fund (fund_no);
CREATE INDEX ix_beneficiary_name ON beneficiary (name);
CREATE INDEX ix_warehouse_zone_warehouse_id ON warehouse_zone (warehouse_id);
CREATE INDEX ix_item_category_id ON item (category_id);
CREATE INDEX ix_item_name ON item (name);
CREATE UNIQUE INDEX ix_item_item_code ON item (item_code);
CREATE UNIQUE INDEX ix_item_uuid ON item (uuid);
CREATE UNIQUE INDEX ix_stock_receipt_receipt_no ON stock_receipt (receipt_no);
CREATE INDEX ix_stock_receipt_supplier_id ON stock_receipt (supplier_id);
CREATE INDEX ix_stock_receipt_warehouse_id ON stock_receipt (warehouse_id);
CREATE INDEX ix_relief_request_status ON relief_request (status);
CREATE UNIQUE INDEX ix_relief_request_request_number ON relief_request (request_number);
CREATE INDEX ix_relief_request_priority ON relief_request (priority);
CREATE INDEX ix_relief_request_incident_id ON relief_request (incident_id);
CREATE INDEX ix_disaster_assessment_incident_id ON disaster_assessment (incident_id);
CREATE INDEX ix_disaster_assessment_fiscal_year ON disaster_assessment (fiscal_year);
CREATE INDEX ix_disaster_assessment_disaster_type ON disaster_assessment (disaster_type);
CREATE INDEX ix_disaster_assessment_disaster_date_bs ON disaster_assessment (disaster_date_bs);
CREATE UNIQUE INDEX ix_stock_transfer_transfer_no ON stock_transfer (transfer_no);
CREATE INDEX ix_stock_transfer_from_warehouse_id ON stock_transfer (from_warehouse_id);
CREATE INDEX ix_stock_transfer_to_warehouse_id ON stock_transfer (to_warehouse_id);
CREATE UNIQUE INDEX ix_cash_receipt_receipt_no ON cash_receipt (receipt_no);
CREATE INDEX ix_cash_receipt_fund_id ON cash_receipt (fund_id);
CREATE UNIQUE INDEX ix_cash_request_request_number ON cash_request (request_number);
CREATE INDEX ix_cash_request_incident_id ON cash_request (incident_id);
CREATE INDEX ix_stock_receipt_item_receipt_id ON stock_receipt_item (receipt_id);
CREATE INDEX ix_stock_receipt_attachment_receipt_id ON stock_receipt_attachment (receipt_id);
CREATE INDEX ix_manual_adjustment_warehouse_id ON manual_adjustment (warehouse_id);
CREATE UNIQUE INDEX ix_manual_adjustment_adjustment_no ON manual_adjustment (adjustment_no);
CREATE INDEX ix_inventory_item_id ON inventory (item_id);
CREATE INDEX ix_inventory_warehouse_id ON inventory (warehouse_id);
CREATE INDEX ix_relief_request_item_request_id ON relief_request_item (request_id);
CREATE INDEX ix_dispatch_incident_id ON dispatch (incident_id);
CREATE INDEX ix_dispatch_warehouse_id ON dispatch (warehouse_id);
CREATE UNIQUE INDEX ix_dispatch_dispatch_number ON dispatch (dispatch_number);
CREATE INDEX ix_dispatch_relief_request_id ON dispatch (relief_request_id);
CREATE INDEX ix_stock_transfer_item_transfer_id ON stock_transfer_item (transfer_id);
CREATE INDEX ix_cash_distribution_incident_id ON cash_distribution (incident_id);
CREATE INDEX ix_cash_distribution_fund_id ON cash_distribution (fund_id);
CREATE INDEX ix_cash_distribution_fiscal_year ON cash_distribution (fiscal_year);
CREATE INDEX ix_cash_distribution_relief_request_id ON cash_distribution (relief_request_id);
CREATE INDEX ix_cash_distribution_cash_request_id ON cash_distribution (cash_request_id);
CREATE UNIQUE INDEX ix_cash_distribution_distribution_no ON cash_distribution (distribution_no);
CREATE INDEX ix_dispatch_item_dispatch_id ON dispatch_item (dispatch_id);
CREATE INDEX ix_distribution_fiscal_year ON distribution (fiscal_year);
CREATE INDEX ix_distribution_incident_id ON distribution (incident_id);
CREATE UNIQUE INDEX ix_distribution_distribution_no ON distribution (distribution_no);
CREATE INDEX ix_distribution_dispatch_id ON distribution (dispatch_id);
CREATE INDEX ix_cash_distribution_beneficiary_distribution_id ON cash_distribution_beneficiary (distribution_id);
CREATE INDEX ix_cash_distribution_beneficiary_beneficiary_id ON cash_distribution_beneficiary (beneficiary_id);
CREATE INDEX ix_distribution_beneficiary_beneficiary_id ON distribution_beneficiary (beneficiary_id);
CREATE INDEX ix_distribution_beneficiary_distribution_id ON distribution_beneficiary (distribution_id);
CREATE INDEX ix_activity_log_user_id ON activity_log (user_id);
CREATE INDEX ix_activity_log_action ON activity_log (action);
CREATE INDEX ix_activity_log_resource ON activity_log (resource);
CREATE INDEX ix_activity_log_created_at ON activity_log (created_at);
CREATE INDEX ix_activity_log_username ON activity_log (username);
CREATE INDEX ix_daily_bulletin_valid_from ON daily_bulletin (valid_from);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('user',5);
COMMIT;
