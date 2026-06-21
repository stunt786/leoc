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
INSERT INTO "activity_log" VALUES(1,1,'admin','create','/api/reset-db',NULL,NULL,'127.0.0.1','2026-06-19 02:53:20.774555');
INSERT INTO "activity_log" VALUES(2,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-19 05:10:48.200653');
INSERT INTO "activity_log" VALUES(3,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-19 06:03:48.409033');
INSERT INTO "activity_log" VALUES(4,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 09:47:13.596499');
INSERT INTO "activity_log" VALUES(5,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 09:47:13.608789');
INSERT INTO "activity_log" VALUES(6,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-19 09:48:40.691445');
INSERT INTO "activity_log" VALUES(7,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-19 09:48:48.563790');
INSERT INTO "activity_log" VALUES(8,1,'admin','view','/api/users',NULL,NULL,'127.0.0.1','2026-06-19 09:49:16.213604');
INSERT INTO "activity_log" VALUES(9,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 09:49:25.184361');
INSERT INTO "activity_log" VALUES(10,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 09:54:28.103389');
INSERT INTO "activity_log" VALUES(11,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 09:57:16.700731');
INSERT INTO "activity_log" VALUES(12,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 09:58:17.162540');
INSERT INTO "activity_log" VALUES(13,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:03:22.302645');
INSERT INTO "activity_log" VALUES(14,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-19 10:09:54.190314');
INSERT INTO "activity_log" VALUES(15,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:10:28.593847');
INSERT INTO "activity_log" VALUES(16,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:18:57.566422');
INSERT INTO "activity_log" VALUES(17,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:45:48.518258');
INSERT INTO "activity_log" VALUES(18,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-19 10:46:03.266294');
INSERT INTO "activity_log" VALUES(19,1,'admin','update','/api/wards/1',NULL,'1','127.0.0.1','2026-06-19 10:46:08.568879');
INSERT INTO "activity_log" VALUES(20,1,'admin','update','/api/wards/2',NULL,'2','127.0.0.1','2026-06-19 10:46:10.058718');
INSERT INTO "activity_log" VALUES(21,1,'admin','update','/api/wards/3',NULL,'3','127.0.0.1','2026-06-19 10:46:11.691930');
INSERT INTO "activity_log" VALUES(22,1,'admin','update','/api/wards/4',NULL,'4','127.0.0.1','2026-06-19 10:46:13.020852');
INSERT INTO "activity_log" VALUES(23,1,'admin','update','/api/wards/5',NULL,'5','127.0.0.1','2026-06-19 10:46:14.462892');
INSERT INTO "activity_log" VALUES(24,1,'admin','update','/api/wards/6',NULL,'6','127.0.0.1','2026-06-19 10:46:16.642069');
INSERT INTO "activity_log" VALUES(25,1,'admin','update','/api/wards/7',NULL,'7','127.0.0.1','2026-06-19 10:46:18.196187');
INSERT INTO "activity_log" VALUES(26,1,'admin','update','/api/wards/8',NULL,'8','127.0.0.1','2026-06-19 10:46:20.769389');
INSERT INTO "activity_log" VALUES(27,1,'admin','update','/api/wards/9',NULL,'9','127.0.0.1','2026-06-19 10:46:22.093074');
INSERT INTO "activity_log" VALUES(28,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:46:24.487456');
INSERT INTO "activity_log" VALUES(29,1,'admin','create','/api/incidents',NULL,'Test Fire','127.0.0.1','2026-06-19 10:48:05.070108');
INSERT INTO "activity_log" VALUES(30,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:48:05.091529');
INSERT INTO "activity_log" VALUES(31,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:49:41.217980');
INSERT INTO "activity_log" VALUES(32,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:50:27.267019');
INSERT INTO "activity_log" VALUES(33,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 10:59:42.017002');
INSERT INTO "activity_log" VALUES(34,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:01:02.075966');
INSERT INTO "activity_log" VALUES(35,1,'admin','delete','/api/incidents/1',NULL,NULL,'127.0.0.1','2026-06-19 11:01:16.935030');
INSERT INTO "activity_log" VALUES(36,1,'admin','create','/api/incidents',NULL,'Test Flood ','127.0.0.1','2026-06-19 11:02:47.874579');
INSERT INTO "activity_log" VALUES(37,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:02:47.887119');
INSERT INTO "activity_log" VALUES(38,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:04:37.098202');
INSERT INTO "activity_log" VALUES(39,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-19 11:07:54.087086');
INSERT INTO "activity_log" VALUES(40,1,'admin','create','/api/warehouses',NULL,'TRM Godam','127.0.0.1','2026-06-19 11:08:22.495400');
INSERT INTO "activity_log" VALUES(41,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-19 11:08:37.846412');
INSERT INTO "activity_log" VALUES(42,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-19 11:08:38.876636');
INSERT INTO "activity_log" VALUES(43,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-19 11:08:48.468711');
INSERT INTO "activity_log" VALUES(44,1,'admin','update','/api/items/65',NULL,'4x4 Pickup (Double Cab)','127.0.0.1','2026-06-19 11:09:00.089419');
INSERT INTO "activity_log" VALUES(45,1,'admin','create','/api/items',NULL,'Rice basmati','127.0.0.1','2026-06-19 11:10:22.479776');
INSERT INTO "activity_log" VALUES(46,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-19 11:10:22.515883');
INSERT INTO "activity_log" VALUES(47,1,'admin','create','/api/items',NULL,'Daal Mix','127.0.0.1','2026-06-19 11:10:53.627362');
INSERT INTO "activity_log" VALUES(48,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-19 11:10:53.690195');
INSERT INTO "activity_log" VALUES(49,1,'admin','create','/api/items',NULL,'Bucket','127.0.0.1','2026-06-19 11:11:25.682072');
INSERT INTO "activity_log" VALUES(50,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-19 11:11:25.738163');
INSERT INTO "activity_log" VALUES(51,1,'admin','create','/api/items',NULL,'Blanket','127.0.0.1','2026-06-19 11:11:57.986799');
INSERT INTO "activity_log" VALUES(52,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-19 11:11:58.041248');
INSERT INTO "activity_log" VALUES(53,1,'admin','view','/api/suppliers',NULL,NULL,'127.0.0.1','2026-06-19 11:11:59.070630');
INSERT INTO "activity_log" VALUES(54,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-19 11:11:59.071855');
INSERT INTO "activity_log" VALUES(55,1,'admin','create','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-19 11:13:26.967704');
INSERT INTO "activity_log" VALUES(56,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-19 11:13:26.993802');
INSERT INTO "activity_log" VALUES(57,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:13:39.654579');
INSERT INTO "activity_log" VALUES(58,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:13:39.655056');
INSERT INTO "activity_log" VALUES(59,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:13:40.533966');
INSERT INTO "activity_log" VALUES(60,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:13:51.984882');
INSERT INTO "activity_log" VALUES(61,1,'admin','view','/api/users',NULL,NULL,'127.0.0.1','2026-06-19 11:14:12.531306');
INSERT INTO "activity_log" VALUES(62,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:14:14.880140');
INSERT INTO "activity_log" VALUES(63,1,'admin','create','/api/beneficiaries',NULL,'Prakash Bhandari','127.0.0.1','2026-06-19 11:15:24.885796');
INSERT INTO "activity_log" VALUES(64,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:15:24.900132');
INSERT INTO "activity_log" VALUES(65,1,'admin','view','/api/cash-receipts',NULL,NULL,'127.0.0.1','2026-06-19 11:16:08.704805');
INSERT INTO "activity_log" VALUES(66,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-19 11:16:17.853688');
INSERT INTO "activity_log" VALUES(67,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:16:33.739604');
INSERT INTO "activity_log" VALUES(68,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:16:33.744814');
INSERT INTO "activity_log" VALUES(69,1,'admin','create','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:17:10.516675');
INSERT INTO "activity_log" VALUES(70,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:17:10.534387');
INSERT INTO "activity_log" VALUES(71,1,'admin','view','/api/cash-funds',NULL,NULL,'127.0.0.1','2026-06-19 11:17:13.480166');
INSERT INTO "activity_log" VALUES(72,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:17:21.253756');
INSERT INTO "activity_log" VALUES(73,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-19 11:17:23.791431');
INSERT INTO "activity_log" VALUES(74,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:17:26.508500');
INSERT INTO "activity_log" VALUES(75,1,'admin','create','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-19 11:17:53.588829');
INSERT INTO "activity_log" VALUES(76,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:17:57.516438');
INSERT INTO "activity_log" VALUES(77,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:17:57.516858');
INSERT INTO "activity_log" VALUES(78,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:19:32.186106');
INSERT INTO "activity_log" VALUES(79,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:19:32.190928');
INSERT INTO "activity_log" VALUES(80,1,'admin','update','/api/relief-requests/1',NULL,NULL,'127.0.0.1','2026-06-19 11:19:38.194625');
INSERT INTO "activity_log" VALUES(81,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-19 11:19:39.994822');
INSERT INTO "activity_log" VALUES(82,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:19:40.456905');
INSERT INTO "activity_log" VALUES(83,1,'admin','create','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:20:03.459546');
INSERT INTO "activity_log" VALUES(84,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:20:09.153998');
INSERT INTO "activity_log" VALUES(85,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:24:46.394721');
INSERT INTO "activity_log" VALUES(86,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:24:46.407155');
INSERT INTO "activity_log" VALUES(87,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:24:57.199082');
INSERT INTO "activity_log" VALUES(88,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:25:05.686437');
INSERT INTO "activity_log" VALUES(89,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:25:05.704838');
INSERT INTO "activity_log" VALUES(90,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:25:21.793537');
INSERT INTO "activity_log" VALUES(91,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:25:21.833259');
INSERT INTO "activity_log" VALUES(92,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:25:23.042697');
INSERT INTO "activity_log" VALUES(93,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:29:13.969116');
INSERT INTO "activity_log" VALUES(94,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:29:14.009500');
INSERT INTO "activity_log" VALUES(95,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:29:15.788574');
INSERT INTO "activity_log" VALUES(96,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:29:28.700317');
INSERT INTO "activity_log" VALUES(97,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:29:54.695546');
INSERT INTO "activity_log" VALUES(98,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:29:54.700880');
INSERT INTO "activity_log" VALUES(99,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-19 11:30:12.368759');
INSERT INTO "activity_log" VALUES(100,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:30:15.276471');
INSERT INTO "activity_log" VALUES(101,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:30:34.296914');
INSERT INTO "activity_log" VALUES(102,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:30:34.302691');
INSERT INTO "activity_log" VALUES(103,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:32:48.262584');
INSERT INTO "activity_log" VALUES(104,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:35:58.356808');
INSERT INTO "activity_log" VALUES(105,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:35:58.362395');
INSERT INTO "activity_log" VALUES(106,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-19 11:35:58.369997');
INSERT INTO "activity_log" VALUES(107,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:35:58.376841');
INSERT INTO "activity_log" VALUES(108,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-19 11:36:14.596669');
INSERT INTO "activity_log" VALUES(109,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-19 11:36:21.268384');
INSERT INTO "activity_log" VALUES(110,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-19 11:36:21.289255');
INSERT INTO "activity_log" VALUES(111,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-19 11:36:23.722340');
INSERT INTO "activity_log" VALUES(112,1,'admin','update','/api/relief-requests/1',NULL,NULL,'127.0.0.1','2026-06-19 11:36:32.379949');
INSERT INTO "activity_log" VALUES(113,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-19 11:36:37.655843');
INSERT INTO "activity_log" VALUES(114,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-20 02:03:38.214069');
INSERT INTO "activity_log" VALUES(115,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-20 02:04:04.872402');
INSERT INTO "activity_log" VALUES(116,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:04:21.314637');
INSERT INTO "activity_log" VALUES(117,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-20 02:04:30.185858');
INSERT INTO "activity_log" VALUES(118,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-20 02:04:56.331324');
INSERT INTO "activity_log" VALUES(119,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-20 02:05:11.075529');
INSERT INTO "activity_log" VALUES(120,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:05:13.397119');
INSERT INTO "activity_log" VALUES(121,1,'admin','view','/api/cash-funds',NULL,NULL,'127.0.0.1','2026-06-20 02:05:41.508254');
INSERT INTO "activity_log" VALUES(122,1,'admin','view','/api/cash-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:06:10.380169');
INSERT INTO "activity_log" VALUES(123,1,'admin','view','/api/cash-funds',NULL,NULL,'127.0.0.1','2026-06-20 02:06:44.219861');
INSERT INTO "activity_log" VALUES(124,1,'admin','create','/api/cash-funds',NULL,'Disaster Relief','127.0.0.1','2026-06-20 02:07:07.162543');
INSERT INTO "activity_log" VALUES(125,1,'admin','create','/api/cash-funds',NULL,'Preparedness ','127.0.0.1','2026-06-20 02:08:21.621890');
INSERT INTO "activity_log" VALUES(126,1,'admin','view','/api/cash-funds',NULL,NULL,'127.0.0.1','2026-06-20 02:08:21.644597');
INSERT INTO "activity_log" VALUES(127,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:08:28.111619');
INSERT INTO "activity_log" VALUES(128,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:09:03.054736');
INSERT INTO "activity_log" VALUES(129,1,'admin','view','/api/cash-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:09:48.855342');
INSERT INTO "activity_log" VALUES(130,1,'admin','create','/api/cash-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:10:11.391057');
INSERT INTO "activity_log" VALUES(131,1,'admin','view','/api/cash-funds',NULL,NULL,'127.0.0.1','2026-06-20 02:10:26.256886');
INSERT INTO "activity_log" VALUES(132,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:11:08.730294');
INSERT INTO "activity_log" VALUES(133,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:11:19.676211');
INSERT INTO "activity_log" VALUES(134,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-20 02:11:19.678791');
INSERT INTO "activity_log" VALUES(135,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:11:39.697595');
INSERT INTO "activity_log" VALUES(136,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:11:43.154576');
INSERT INTO "activity_log" VALUES(137,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:13:03.368810');
INSERT INTO "activity_log" VALUES(138,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-20 02:13:07.955214');
INSERT INTO "activity_log" VALUES(139,1,'admin','view','/api/suppliers',NULL,NULL,'127.0.0.1','2026-06-20 02:13:17.163480');
INSERT INTO "activity_log" VALUES(140,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:13:17.189121');
INSERT INTO "activity_log" VALUES(141,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:14:35.719980');
INSERT INTO "activity_log" VALUES(142,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:14:38.727843');
INSERT INTO "activity_log" VALUES(143,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:15:32.004067');
INSERT INTO "activity_log" VALUES(144,1,'admin','create','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:16:11.220085');
INSERT INTO "activity_log" VALUES(145,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:16:11.236217');
INSERT INTO "activity_log" VALUES(146,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:16:18.610550');
INSERT INTO "activity_log" VALUES(147,1,'admin','create','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:17:10.623395');
INSERT INTO "activity_log" VALUES(148,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:17:10.657681');
INSERT INTO "activity_log" VALUES(149,1,'admin','view','/api/cash-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:17:28.323553');
INSERT INTO "activity_log" VALUES(150,1,'admin','view','/api/cash-funds',NULL,NULL,'127.0.0.1','2026-06-20 02:17:34.315828');
INSERT INTO "activity_log" VALUES(151,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:17:48.382521');
INSERT INTO "activity_log" VALUES(152,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:18:00.716787');
INSERT INTO "activity_log" VALUES(153,1,'admin','create','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:18:30.910061');
INSERT INTO "activity_log" VALUES(154,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:18:30.940635');
INSERT INTO "activity_log" VALUES(155,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:18:42.002095');
INSERT INTO "activity_log" VALUES(156,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-20 02:19:11.540632');
INSERT INTO "activity_log" VALUES(157,1,'admin','view','/api/suppliers',NULL,NULL,'127.0.0.1','2026-06-20 02:19:55.688909');
INSERT INTO "activity_log" VALUES(158,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:19:55.709283');
INSERT INTO "activity_log" VALUES(159,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-20 02:20:07.408613');
INSERT INTO "activity_log" VALUES(160,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:23:31.197976');
INSERT INTO "activity_log" VALUES(161,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-20 02:23:33.429450');
INSERT INTO "activity_log" VALUES(162,1,'admin','update','/api/warehouses/1',NULL,'Kathmandu','127.0.0.1','2026-06-20 02:24:00.416361');
INSERT INTO "activity_log" VALUES(163,1,'admin','update','/api/warehouses/1',NULL,'Kathmandu','127.0.0.1','2026-06-20 02:24:17.672876');
INSERT INTO "activity_log" VALUES(164,1,'admin','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-20 02:24:17.698155');
INSERT INTO "activity_log" VALUES(165,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:24:59.441518');
INSERT INTO "activity_log" VALUES(166,1,'admin','delete','/api/categories/12',NULL,NULL,'127.0.0.1','2026-06-20 02:27:35.514005');
INSERT INTO "activity_log" VALUES(167,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:27:35.531681');
INSERT INTO "activity_log" VALUES(168,1,'admin','delete','/api/categories/10',NULL,NULL,'127.0.0.1','2026-06-20 02:27:44.893060');
INSERT INTO "activity_log" VALUES(169,1,'admin','delete','/api/categories/8',NULL,NULL,'127.0.0.1','2026-06-20 02:27:49.645328');
INSERT INTO "activity_log" VALUES(170,1,'admin','delete','/api/categories/5',NULL,NULL,'127.0.0.1','2026-06-20 02:27:55.170633');
INSERT INTO "activity_log" VALUES(171,1,'admin','delete','/api/categories/7',NULL,NULL,'127.0.0.1','2026-06-20 02:28:09.321878');
INSERT INTO "activity_log" VALUES(172,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:28:09.348077');
INSERT INTO "activity_log" VALUES(173,1,'admin','delete','/api/categories/11',NULL,NULL,'127.0.0.1','2026-06-20 02:28:13.288500');
INSERT INTO "activity_log" VALUES(174,1,'admin','delete','/api/categories/9',NULL,NULL,'127.0.0.1','2026-06-20 02:28:33.182957');
INSERT INTO "activity_log" VALUES(175,1,'admin','delete','/api/categories/20',NULL,NULL,'127.0.0.1','2026-06-20 02:28:37.089441');
INSERT INTO "activity_log" VALUES(176,1,'admin','delete','/api/categories/4',NULL,NULL,'127.0.0.1','2026-06-20 02:29:09.758766');
INSERT INTO "activity_log" VALUES(177,1,'admin','view','/api/categories',NULL,NULL,'127.0.0.1','2026-06-20 02:29:09.780615');
INSERT INTO "activity_log" VALUES(178,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-20 02:29:20.092626');
INSERT INTO "activity_log" VALUES(179,1,'admin','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:30:17.581921');
INSERT INTO "activity_log" VALUES(180,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-20 02:30:23.932013');
INSERT INTO "activity_log" VALUES(181,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:30:23.944453');
INSERT INTO "activity_log" VALUES(182,1,'admin','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-20 02:30:40.914719');
INSERT INTO "activity_log" VALUES(183,1,'admin','update','/api/items/65',NULL,'4x4 Pickup (Double Cab)','127.0.0.1','2026-06-20 02:30:48.855010');
INSERT INTO "activity_log" VALUES(184,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-20 02:30:55.467787');
INSERT INTO "activity_log" VALUES(185,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:30:55.474906');
INSERT INTO "activity_log" VALUES(186,1,'admin','delete','/api/relief-requests/1',NULL,NULL,'127.0.0.1','2026-06-20 02:31:12.363781');
INSERT INTO "activity_log" VALUES(187,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-20 02:31:14.918603');
INSERT INTO "activity_log" VALUES(188,1,'admin','view','/api/dispatch',NULL,NULL,'127.0.0.1','2026-06-20 02:31:25.543808');
INSERT INTO "activity_log" VALUES(189,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-20 02:31:36.307082');
INSERT INTO "activity_log" VALUES(190,1,'admin','view','/api/distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:31:36.375561');
INSERT INTO "activity_log" VALUES(191,1,'admin','view','/api/cash-funds',NULL,NULL,'127.0.0.1','2026-06-20 02:31:48.674669');
INSERT INTO "activity_log" VALUES(192,1,'admin','view','/api/cash-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:32:02.036341');
INSERT INTO "activity_log" VALUES(193,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:32:06.759047');
INSERT INTO "activity_log" VALUES(194,1,'admin','view','/api/relief-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:32:25.012996');
INSERT INTO "activity_log" VALUES(195,1,'admin','view','/api/beneficiaries',NULL,NULL,'127.0.0.1','2026-06-20 02:32:25.020588');
INSERT INTO "activity_log" VALUES(196,1,'admin','view','/api/cash-distributions',NULL,NULL,'127.0.0.1','2026-06-20 02:32:33.425435');
INSERT INTO "activity_log" VALUES(197,1,'admin','view','/api/users',NULL,NULL,'127.0.0.1','2026-06-20 02:32:48.280830');
INSERT INTO "activity_log" VALUES(198,1,'admin','logout','auth',NULL,'User admin logged out','127.0.0.1','2026-06-20 02:33:12.279060');
INSERT INTO "activity_log" VALUES(199,3,'viewer','login','auth',NULL,'User viewer logged in','127.0.0.1','2026-06-20 02:33:25.604106');
INSERT INTO "activity_log" VALUES(200,3,'viewer','logout','auth',NULL,'User viewer logged out','127.0.0.1','2026-06-20 02:34:10.859536');
INSERT INTO "activity_log" VALUES(201,NULL,'System','login_failed','auth',NULL,'Failed login attempt for editor','127.0.0.1','2026-06-20 02:34:26.856539');
INSERT INTO "activity_log" VALUES(202,2,'editor','login','auth',NULL,'User editor logged in','127.0.0.1','2026-06-20 02:34:37.374643');
INSERT INTO "activity_log" VALUES(203,2,'editor','view','/api/warehouses',NULL,NULL,'127.0.0.1','2026-06-20 02:34:41.081120');
INSERT INTO "activity_log" VALUES(204,2,'editor','view','/api/stock-receipts',NULL,NULL,'127.0.0.1','2026-06-20 02:34:53.325435');
INSERT INTO "activity_log" VALUES(205,2,'editor','view','/api/items',NULL,NULL,'127.0.0.1','2026-06-20 02:34:54.322336');
INSERT INTO "activity_log" VALUES(206,2,'editor','logout','auth',NULL,'User editor logged out','127.0.0.1','2026-06-20 02:35:14.020336');
INSERT INTO "activity_log" VALUES(207,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-20 02:35:24.624431');
INSERT INTO "activity_log" VALUES(208,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:35:49.686390');
INSERT INTO "activity_log" VALUES(209,1,'admin','create','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:36:19.678855');
INSERT INTO "activity_log" VALUES(210,1,'admin','view','/api/cash-requests',NULL,NULL,'127.0.0.1','2026-06-20 02:36:19.692762');
INSERT INTO "activity_log" VALUES(211,1,'admin','view','/api/incidents',NULL,NULL,'127.0.0.1','2026-06-20 02:36:49.554933');
INSERT INTO "activity_log" VALUES(212,1,'admin','logout','auth',NULL,'User admin logged out','127.0.0.1','2026-06-20 02:36:52.751084');
INSERT INTO "activity_log" VALUES(213,1,'admin','login','auth',NULL,'User admin logged in','127.0.0.1','2026-06-20 02:37:38.565779');
INSERT INTO "activity_log" VALUES(214,1,'admin','view','/api/settings',NULL,NULL,'127.0.0.1','2026-06-20 02:37:53.943532');
CREATE TABLE app_settings (
	id INTEGER NOT NULL, 
	setting_key VARCHAR(100) NOT NULL, 
	setting_value TEXT NOT NULL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (setting_key)
);
INSERT INTO "app_settings" VALUES(1,'relief_items','["खाद्य सामाग्री (Food Packages)", "पानीको बोतल (Water Bottles)", "औषधि सामाग्री (Medical Supplies)", "कम्बल (Blankets)", "लुगा सामाग्री (Clothing)", "स्वास्थ्य सामाग्री (Hygiene Kits)", "घर बनाउने सामाग्री (Shelter Materials)", "बच्चाको हेरचाह (Baby Care)", "अन्य (Other)"]','2026-06-19 02:53:20.708349','2026-06-19 02:53:20.708354');
INSERT INTO "app_settings" VALUES(2,'fiscal_years','["2080/81", "2081/82", "2082/83", "2083/84", "2084/85"]','2026-06-19 02:53:20.713611','2026-06-19 02:53:20.713617');
INSERT INTO "app_settings" VALUES(3,'active_fiscal_year','2081/82','2026-06-19 02:53:20.718571','2026-06-19 02:53:20.718575');
INSERT INTO "app_settings" VALUES(4,'ssf_types','["OAS (बर्षा पेन्सन)", "विधवा (Widow)", "अपाङ्गता (Disabled)", "कोही नभएको (Endangered)", "बाल भत्ता (Child Grant)", "अन्य (Other)"]','2026-06-19 02:53:20.722945','2026-06-19 02:53:20.722951');
INSERT INTO "app_settings" VALUES(5,'disaster_types','["भूकम्प (Earthquake)", "बाढी (Flood)", "पहिरो (Landslide)", "आँधी (Storm)", "आगलागी (Fire)", "अन्य (Other)"]','2026-06-19 02:53:20.728332','2026-06-19 02:53:20.728340');
INSERT INTO "app_settings" VALUES(6,'organization_name','थलारा गाउँपालिका','2026-06-19 02:53:20.734443','2026-06-19 02:53:20.734449');
INSERT INTO "app_settings" VALUES(7,'organization_address','खोली, बझाङ','2026-06-19 02:53:20.739269','2026-06-19 02:53:20.739274');
INSERT INTO "app_settings" VALUES(8,'organization_phone','XXX-XXXXXXX','2026-06-19 02:53:20.743564','2026-06-19 02:53:20.743569');
INSERT INTO "app_settings" VALUES(9,'organization_email','leoc@thalara.gov.np','2026-06-19 02:53:20.749141','2026-06-19 02:53:20.749146');
INSERT INTO "app_settings" VALUES(10,'currency','NPR','2026-06-19 02:53:20.753473','2026-06-19 02:53:20.753477');
INSERT INTO "app_settings" VALUES(11,'language','ne','2026-06-19 02:53:20.757829','2026-06-19 02:53:20.757834');
INSERT INTO "app_settings" VALUES(12,'default_warehouse','','2026-06-19 02:53:20.763072','2026-06-19 02:53:20.763077');
INSERT INTO "app_settings" VALUES(13,'office_name','थलारा गाउँपालिका','2026-06-19 05:06:21.416844','2026-06-19 05:06:21.416849');
INSERT INTO "app_settings" VALUES(14,'default_language','Nepali','2026-06-19 05:06:21.420898','2026-06-19 05:06:21.420900');
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
INSERT INTO "beneficiary" VALUES(1,'Prakash Bhandari','1236','Man Bahadur Bhandari','9865654665','Thalara',5,'Kholi','Own','',2,'[{"name": "Sital Thapa", "id": "11", "relation": "Spouse", "age": 30, "gender": "Female", "is_pregnant": true, "is_disabled": false}, {"name": "Pinku", "id": "12111", "relation": "Son", "age": 3, "gender": "Male", "is_pregnant": false, "is_disabled": false}]',0,'',1,'','','','','',1,'2026-06-19 11:15:24.878098','2026-06-19 11:15:24.878104');
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
INSERT INTO "cash_distribution" VALUES(1,'CASH-DIST-0001','2026-06-20',1,1,1,NULL,'Individual',3500.0,'2081/82','Sankae','',1,'2026-06-20 02:17:10.594668');
INSERT INTO "cash_distribution" VALUES(2,'CASH-DIST-0002','2026-06-20',2,1,1,NULL,'Individual',1500.0,'2081/82','Sankae','',1,'2026-06-20 02:18:30.889767');
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
INSERT INTO "cash_distribution_beneficiary" VALUES(1,1,NULL,'Hiralal','112','Thalara','9865654665',3500.0);
INSERT INTO "cash_distribution_beneficiary" VALUES(2,2,NULL,'Hiralal','112','Thalara','9865654665',1500.0);
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
INSERT INTO "cash_fund" VALUES(1,'FUND-0001','Disaster Relief','2081/82','Municipality',10000.0,6500.0,'','Active',1,'2026-06-20 02:07:07.129724','2026-06-20 02:17:10.600035');
INSERT INTO "cash_fund" VALUES(2,'FUND-0002','Preparedness ','2081/82','NGO',25000.0,38500.0,'','Active',1,'2026-06-20 02:08:21.616503','2026-06-20 02:18:30.893656');
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
INSERT INTO "cash_receipt" VALUES(1,'CR-0001','2026-06-20',2,'NGO','','','',15000.0,'','',NULL,1,'2026-06-20 02:10:11.378119');
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
INSERT INTO "cash_request" VALUES(1,'CASH-REQ-0001','2026-06-20',1,'','Tilak Shah','9865654665','Medium',5000.0,'Immediate Relief','','Completed',NULL,'2026-06-20 02:16:11.212268','2026-06-20 02:18:30.895832');
INSERT INTO "cash_request" VALUES(2,'CASH-REQ-0002','2026-06-20',1,'gg','Tilak Shah','9841234567','Medium',6000.0,'Food Assistance','','Pending',NULL,'2026-06-20 02:36:19.672595','2026-06-20 02:36:19.672599');
CREATE TABLE category (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "category" VALUES(1,'Food',NULL,'2026-06-19 02:53:20.637216');
INSERT INTO "category" VALUES(2,'Shelter',NULL,'2026-06-19 02:53:20.637221');
INSERT INTO "category" VALUES(3,'Relief Supplies',NULL,'2026-06-19 02:53:20.637221');
INSERT INTO "category" VALUES(6,'Protection Gear',NULL,'2026-06-19 02:53:20.637224');
INSERT INTO "category" VALUES(13,'Other',NULL,'2026-06-19 02:53:20.637228');
INSERT INTO "category" VALUES(14,'Rescue - Search & Rescue Tools',NULL,'2026-06-19 02:53:20.637229');
INSERT INTO "category" VALUES(15,'Rescue - Ropes & Rigging',NULL,'2026-06-19 02:53:20.637229');
INSERT INTO "category" VALUES(16,'Rescue - Cutting & Breaking',NULL,'2026-06-19 02:53:20.637230');
INSERT INTO "category" VALUES(17,'Rescue - Lighting & Signal',NULL,'2026-06-19 02:53:20.637230');
INSERT INTO "category" VALUES(18,'Rescue - Water Rescue',NULL,'2026-06-19 02:53:20.637231');
INSERT INTO "category" VALUES(19,'Rescue - Confined Space',NULL,'2026-06-19 02:53:20.637231');
INSERT INTO "category" VALUES(21,'Medical - Equipment',NULL,'2026-06-19 02:53:20.637232');
INSERT INTO "category" VALUES(22,'Medical - First Aid',NULL,'2026-06-19 02:53:20.637233');
INSERT INTO "category" VALUES(23,'Medical - Diagnostic',NULL,'2026-06-19 02:53:20.637234');
INSERT INTO "category" VALUES(24,'Medical - Mobility & Transport',NULL,'2026-06-19 02:53:20.637234');
INSERT INTO "category" VALUES(25,'Vehicles - Light',NULL,'2026-06-19 02:53:20.637235');
INSERT INTO "category" VALUES(26,'Vehicles - Heavy',NULL,'2026-06-19 02:53:20.637235');
INSERT INTO "category" VALUES(27,'Vehicles - Water & Air',NULL,'2026-06-19 02:53:20.637236');
INSERT INTO "category" VALUES(28,'Vehicle Parts & Tools',NULL,'2026-06-19 02:53:20.637236');
INSERT INTO "category" VALUES(29,'Preparedness - Communication',NULL,'2026-06-19 02:53:20.637237');
INSERT INTO "category" VALUES(30,'Preparedness - Power & Lighting',NULL,'2026-06-19 02:53:20.637237');
INSERT INTO "category" VALUES(31,'Preparedness - Shelter & Camp',NULL,'2026-06-19 02:53:20.637238');
INSERT INTO "category" VALUES(32,'Preparedness - Water & Sanitation',NULL,'2026-06-19 02:53:20.637238');
INSERT INTO "category" VALUES(33,'Preparedness - Fire Safety',NULL,'2026-06-19 02:53:20.637239');
CREATE TABLE daily_bulletin (
	id INTEGER NOT NULL, 
	notice_title VARCHAR(300) NOT NULL, 
	notice_description TEXT, 
	priority VARCHAR(20), 
	report_status VARCHAR(20), 
	valid_from VARCHAR(10) NOT NULL, 
	valid_to VARCHAR(10), 
	weather_status VARCHAR(100), 
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
INSERT INTO "daily_report_log" VALUES(1,'2083-03-05','2026-06-19 09:49:28.392647');
INSERT INTO "daily_report_log" VALUES(2,'2083-03-06','2026-06-20 02:19:17.722483');
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
INSERT INTO "dispatch" VALUES(1,'DSP-9514','2026-06-19',1,1,NULL,'','','','',1,'2026-06-19 11:17:53.569790');
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
INSERT INTO "dispatch_item" VALUES(1,1,130,10,'Kg','','2026-06-19');
INSERT INTO "dispatch_item" VALUES(2,1,131,3,'Kg','','2026-06-19');
INSERT INTO "dispatch_item" VALUES(3,1,132,2,'Piece','','2026-06-19');
INSERT INTO "dispatch_item" VALUES(4,1,133,2,'Piece','','2026-06-19');
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
INSERT INTO "distribution" VALUES(1,'DIST-0480',1,1,'',NULL,NULL,'2081/82','2026-06-19','','Completed','',1,'2026-06-19 11:20:03.447132');
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
INSERT INTO "distribution_beneficiary" VALUES(1,1,1,'Prakash Bhandari','1236',2,'Rice basmati',10,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(2,1,1,'Prakash Bhandari','1236',2,'Daal Mix',3,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(3,1,1,'Prakash Bhandari','1236',2,'Bucket',2,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(4,1,1,'Prakash Bhandari','1236',2,'Blanket',2,'Received',NULL,NULL);
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
	injured_male INTEGER, 
	injured_female INTEGER, 
	deaths INTEGER, 
	death_male INTEGER, 
	death_female INTEGER, 
	missing_persons INTEGER, 
	missing_male INTEGER, 
	missing_female INTEGER, 
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
	updated_at DATETIME, weather_status VARCHAR(100), 
	PRIMARY KEY (id)
);
INSERT INTO "incident" VALUES(1,'Test Flood','बाढी (Flood)',1,'1969-10-05','Active','2081/82','','2083-03-05','04:46','','','medium',10,13,7,6,3,2,1,1,1,0,15,23,5,5,2,2,1,458000.0,'Agriculture land destroyed',1,1,0,1,15,25,15,30,4,2,1,0,'','2026-06-19 11:02:47.868593','2026-06-19 11:02:47.868598',NULL);
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
INSERT INTO "inventory" VALUES(1,130,1,190,0,'2026-06-19 11:17:53.572841');
INSERT INTO "inventory" VALUES(2,131,1,47,0,'2026-06-19 11:17:53.575255');
INSERT INTO "inventory" VALUES(3,132,1,48,0,'2026-06-19 11:17:53.576584');
INSERT INTO "inventory" VALUES(4,133,1,98,0,'2026-06-19 11:17:53.577972');
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
INSERT INTO "item" VALUES(1,'1f758348-0907-456d-a452-d2ddd63c8c18',NULL,NULL,NULL,15,'Cat-1 Rope (Static)',NULL,NULL,'Meter',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695739','2026-06-19 02:53:20.695744');
INSERT INTO "item" VALUES(2,'242313a9-6f6b-4dbc-aca1-2da416d93ad7',NULL,NULL,NULL,15,'Cat-2 Rope (Dynamic)',NULL,NULL,'Meter',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695747','2026-06-19 02:53:20.695747');
INSERT INTO "item" VALUES(3,'02beddab-ba3b-49c8-be86-d1c417f1ddc5',NULL,NULL,NULL,15,'Webbing Sling (60cm)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695749','2026-06-19 02:53:20.695750');
INSERT INTO "item" VALUES(4,'d4797e0c-8cd0-4e80-9113-fc366d04b553',NULL,NULL,NULL,15,'Webbing Sling (120cm)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695751','2026-06-19 02:53:20.695752');
INSERT INTO "item" VALUES(5,'30554e40-9691-4d66-b9be-08d3f75e956b',NULL,NULL,NULL,15,'Carabiner (Screw Lock)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695754','2026-06-19 02:53:20.695754');
INSERT INTO "item" VALUES(6,'9eaf99cb-379e-4f0a-9a26-c36e11873663',NULL,NULL,NULL,15,'Carabiner (Auto Lock)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695756','2026-06-19 02:53:20.695756');
INSERT INTO "item" VALUES(7,'09b33ff8-292d-432d-ab6a-0a7380c14a38',NULL,NULL,NULL,15,'Descender (Figure 8)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695758','2026-06-19 02:53:20.695759');
INSERT INTO "item" VALUES(8,'10268141-0dde-4022-a212-443ac92c168d',NULL,NULL,NULL,15,'Pulley (Single)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695760','2026-06-19 02:53:20.695761');
INSERT INTO "item" VALUES(9,'1fb6fbcc-3184-477c-9215-c2b533fef0c5',NULL,NULL,NULL,15,'Pulley (Double)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695762','2026-06-19 02:53:20.695763');
INSERT INTO "item" VALUES(10,'b00881fc-33c2-42de-b15d-444a51445f94',NULL,NULL,NULL,15,'Harness (Full Body)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695764','2026-06-19 02:53:20.695765');
INSERT INTO "item" VALUES(11,'5a7c6639-0b36-451e-ae13-55c3575f6fba',NULL,NULL,NULL,15,'Harness (Chest)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695767','2026-06-19 02:53:20.695768');
INSERT INTO "item" VALUES(12,'d1be78b5-e736-4da9-a2b5-f6ba723173e4',NULL,NULL,NULL,14,'Helmet (Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695769','2026-06-19 02:53:20.695770');
INSERT INTO "item" VALUES(13,'abc5f6f7-213b-48c9-92da-e7d54907ed77',NULL,NULL,NULL,17,'Headlamp (Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695772','2026-06-19 02:53:20.695772');
INSERT INTO "item" VALUES(14,'86d9fbfa-a9b1-4e36-aaa4-4f623f02eaf0',NULL,NULL,NULL,17,'Rescue Flashlight',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695774','2026-06-19 02:53:20.695774');
INSERT INTO "item" VALUES(15,'902630ff-83dd-41bf-ab78-25a91b31fe8d',NULL,NULL,NULL,17,'Signal Whistle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695776','2026-06-19 02:53:20.695777');
INSERT INTO "item" VALUES(16,'91235b24-7243-4b97-92f4-e576d1c1bdee',NULL,NULL,NULL,14,'Safety Glasses',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695778','2026-06-19 02:53:20.695779');
INSERT INTO "item" VALUES(17,'f94d9fd1-ab51-476c-a285-9230d533a1c1',NULL,NULL,NULL,14,'Work Gloves (Leather)',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695781','2026-06-19 02:53:20.695781');
INSERT INTO "item" VALUES(18,'fc9cf98e-98d6-4c97-9ac9-ccfe708f3653',NULL,NULL,NULL,14,'Knee Pads',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695785','2026-06-19 02:53:20.695785');
INSERT INTO "item" VALUES(19,'bdd5e70b-f45b-4d77-b85e-e8a93ef39c82',NULL,NULL,NULL,16,'Cutting Tool (Bolt Cutter)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695787','2026-06-19 02:53:20.695787');
INSERT INTO "item" VALUES(20,'89c27e32-7d4e-4e39-9df8-622e6cc10952',NULL,NULL,NULL,16,'Crowbar',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695789','2026-06-19 02:53:20.695790');
INSERT INTO "item" VALUES(21,'1255d9a0-c4a8-4c36-a9a0-d0face6d92a5',NULL,NULL,NULL,16,'Sledge Hammer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695791','2026-06-19 02:53:20.695792');
INSERT INTO "item" VALUES(22,'23c58aef-8089-47c4-82c7-149864349800',NULL,NULL,NULL,16,'Hacksaw',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695793','2026-06-19 02:53:20.695794');
INSERT INTO "item" VALUES(23,'d539cf8c-c973-48f0-a3a7-72be5bd98523',NULL,NULL,NULL,14,'Shovel (Folding)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695795','2026-06-19 02:53:20.695796');
INSERT INTO "item" VALUES(24,'6a96bccd-623a-4b7f-8ce2-0fb0566cc946',NULL,NULL,NULL,14,'Stretcher (Basket)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695798','2026-06-19 02:53:20.695798');
INSERT INTO "item" VALUES(25,'6634bd62-9b91-4e8b-b96b-af72a0d63828',NULL,NULL,NULL,14,'Stretcher (Foldable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695800','2026-06-19 02:53:20.695800');
INSERT INTO "item" VALUES(26,'dbf77a7d-9251-472d-801c-464484a6563e',NULL,NULL,NULL,14,'Spine Board',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695802','2026-06-19 02:53:20.695803');
INSERT INTO "item" VALUES(27,'a87fd241-6e83-4e0e-97ea-a2bb93c2c8c0',NULL,NULL,NULL,14,'Cervical Collar (Set)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695805','2026-06-19 02:53:20.695805');
INSERT INTO "item" VALUES(28,'08f8522a-4f16-489c-9911-2c40de62883f',NULL,NULL,NULL,18,'Life Jacket',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695807','2026-06-19 02:53:20.695808');
INSERT INTO "item" VALUES(29,'8aac6fab-6e77-441e-846c-38428af07fd9',NULL,NULL,NULL,18,'Throw Bag (Water Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695809','2026-06-19 02:53:20.695810');
INSERT INTO "item" VALUES(30,'90adb70c-f918-4994-a025-853e1f3ae753',NULL,NULL,NULL,18,'Rescue Tube',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695811','2026-06-19 02:53:20.695812');
INSERT INTO "item" VALUES(31,'cc36f873-e3ee-4e8d-bb8e-354a9b2073b2',NULL,NULL,NULL,19,'Gas Detector (Multi)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695813','2026-06-19 02:53:20.695814');
INSERT INTO "item" VALUES(32,'1654b88f-cae3-434a-88b5-61f0415a4cff',NULL,NULL,NULL,19,'Tripod Rescue System',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695816','2026-06-19 02:53:20.695816');
INSERT INTO "item" VALUES(33,'5cbc880c-da54-430f-90bd-f5dbd73a9b73',NULL,NULL,NULL,14,'Come-Along Winch',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695818','2026-06-19 02:53:20.695818');
INSERT INTO "item" VALUES(34,'4568f745-9574-4db8-a42a-cd6ee5db6baf',NULL,NULL,NULL,15,'Rope Grab (ASAP)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695820','2026-06-19 02:53:20.695821');
INSERT INTO "item" VALUES(35,'cf880fe2-dc27-4db9-9976-7b0ee4b9be1b',NULL,NULL,NULL,15,'Edge Roller',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695822','2026-06-19 02:53:20.695823');
INSERT INTO "item" VALUES(36,'f77be1a1-3bfe-4fcf-98d4-0f6a37c38f25',NULL,NULL,NULL,15,'Prusik Loop',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695824','2026-06-19 02:53:20.695825');
INSERT INTO "item" VALUES(37,'42f58c83-9fbe-46e9-b983-d990687dce1c',NULL,NULL,NULL,15,'Daisy Chain',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695826','2026-06-19 02:53:20.695827');
INSERT INTO "item" VALUES(38,'feaefd76-255b-4bc8-b78d-c1e3ecb33083',NULL,NULL,NULL,14,'Ratchet Strap (Heavy)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695828','2026-06-19 02:53:20.695829');
INSERT INTO "item" VALUES(39,'fa16738b-8cb7-4785-81c3-b74419b3c6a5',NULL,NULL,NULL,14,'Tarp (Waterproof)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695830','2026-06-19 02:53:20.695831');
INSERT INTO "item" VALUES(40,'96e4d89f-75c6-4330-8ea5-249b36925a53',NULL,NULL,NULL,21,'Oxygen Cylinder (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695833','2026-06-19 02:53:20.695833');
INSERT INTO "item" VALUES(41,'3316d1aa-201c-43bd-9141-3d8065431dba',NULL,NULL,NULL,21,'Oxygen Regulator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695835','2026-06-19 02:53:20.695835');
INSERT INTO "item" VALUES(42,'2e7445c3-c6c1-4a3a-927d-2c36f1ed7221',NULL,NULL,NULL,23,'Pulse Oximeter',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695837','2026-06-19 02:53:20.695838');
INSERT INTO "item" VALUES(43,'8b033974-73d2-40a5-ab30-0b2034d68749',NULL,NULL,NULL,23,'BP Monitor (Digital)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695839','2026-06-19 02:53:20.695840');
INSERT INTO "item" VALUES(44,'3f39d689-d5af-49bd-a479-a7959d6636bc',NULL,NULL,NULL,23,'Thermometer (Infrared)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695841','2026-06-19 02:53:20.695842');
INSERT INTO "item" VALUES(45,'e07e1408-9904-458e-936d-e2c103c140f8',NULL,NULL,NULL,23,'Stethoscope',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695843','2026-06-19 02:53:20.695844');
INSERT INTO "item" VALUES(46,'f91df575-0ab6-4fbf-8720-1a62e57799e2',NULL,NULL,NULL,23,'Glucometer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695845','2026-06-19 02:53:20.695846');
INSERT INTO "item" VALUES(47,'177a3ede-2732-4d2c-ae14-7b6eab203a1b',NULL,NULL,NULL,21,'Suction Machine',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695848','2026-06-19 02:53:20.695848');
INSERT INTO "item" VALUES(48,'a10c056c-46bf-4005-a25c-04517c5e98d0',NULL,NULL,NULL,21,'Bag Valve Mask (Adult)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695850','2026-06-19 02:53:20.695850');
INSERT INTO "item" VALUES(49,'e1a7fada-34bc-40fc-b886-d869fb8aa4ac',NULL,NULL,NULL,21,'Bag Valve Mask (Pediatric)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695852','2026-06-19 02:53:20.695852');
INSERT INTO "item" VALUES(50,'ccf61477-5c1e-4fbe-81e5-8514d0622ec7',NULL,NULL,NULL,21,'Laryngoscope Set',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695854','2026-06-19 02:53:20.695854');
INSERT INTO "item" VALUES(51,'056ad456-6262-4766-9055-412445742294',NULL,NULL,NULL,24,'Stretcher (Ambulance)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695856','2026-06-19 02:53:20.695857');
INSERT INTO "item" VALUES(52,'6d51c79c-ed06-47d9-ac09-d67d53ca3448',NULL,NULL,NULL,24,'Wheelchair',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695858','2026-06-19 02:53:20.695859');
INSERT INTO "item" VALUES(53,'34f06788-ba23-4c7b-a7aa-302981786eae',NULL,NULL,NULL,24,'Crutches (Pair)',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695860','2026-06-19 02:53:20.695863');
INSERT INTO "item" VALUES(54,'99ec3ac3-2903-4049-839f-433322930beb',NULL,NULL,NULL,24,'Walking Frame',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695865','2026-06-19 02:53:20.695866');
INSERT INTO "item" VALUES(55,'75516a96-1c35-4cc6-a5ca-ab3274d6f9db',NULL,NULL,NULL,21,'IV Stand',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695867','2026-06-19 02:53:20.695868');
INSERT INTO "item" VALUES(56,'006f7e82-0b7e-4786-9e0e-8e9552dec584',NULL,NULL,NULL,22,'First Aid Cabinet (Empty)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695869','2026-06-19 02:53:20.695870');
INSERT INTO "item" VALUES(57,'af6e0ee7-cbdf-4a71-9784-d14bbdcc86d1',NULL,NULL,NULL,22,'Splint Set (SAM)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695872','2026-06-19 02:53:20.695872');
INSERT INTO "item" VALUES(58,'9545c06e-7033-4f15-9fe1-a82c6e75f00b',NULL,NULL,NULL,22,'Tourniquet (CAT)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695874','2026-06-19 02:53:20.695874');
INSERT INTO "item" VALUES(59,'96b291e4-c129-4c64-bb98-8a170eb110a3',NULL,NULL,NULL,22,'Trauma Shears',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695876','2026-06-19 02:53:20.695876');
INSERT INTO "item" VALUES(60,'98150d57-608f-43c9-95f8-c232e0cd6c91',NULL,NULL,NULL,22,'Medical Backpack (Empty)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695878','2026-06-19 02:53:20.695878');
INSERT INTO "item" VALUES(61,'ce0fb3a8-a6ad-4450-9cb2-98c0981cd6e4',NULL,NULL,NULL,21,'CPR Pocket Mask',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695880','2026-06-19 02:53:20.695880');
INSERT INTO "item" VALUES(62,'568721a9-96ee-4369-be52-d5d683c15781',NULL,NULL,NULL,21,'Portable Ventilator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695882','2026-06-19 02:53:20.695883');
INSERT INTO "item" VALUES(63,'248d7854-c161-4b57-85cd-42c08d3a348d',NULL,NULL,NULL,21,'Defibrillator (AED)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695884','2026-06-19 02:53:20.695884');
INSERT INTO "item" VALUES(64,'d81f78f3-3269-41cb-a5e1-9d80a5abac7e',NULL,NULL,NULL,21,'Oxygen Tank (Large)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695886','2026-06-19 02:53:20.695887');
INSERT INTO "item" VALUES(65,'28b88e5b-9780-4553-ae44-bfaa1e5eb73d','','','',25,'4x4 Pickup (Double Cab)','','','Piece',0,0,0,0,0,0,0,0,'Normal','','Active',NULL,1,'2026-06-19 02:53:20.695888','2026-06-20 02:30:48.842148');
INSERT INTO "item" VALUES(66,'24eebf2c-d93f-4c0b-bfc7-2f23b40305e3',NULL,NULL,NULL,25,'SUV (4x4)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695890','2026-06-19 02:53:20.695891');
INSERT INTO "item" VALUES(67,'e215a70a-d163-49c6-8706-41073a1deacb',NULL,NULL,NULL,25,'Motorcycle (Dirt)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695892','2026-06-19 02:53:20.695893');
INSERT INTO "item" VALUES(68,'47415de0-83af-4f10-ab32-7d0c289b94f8',NULL,NULL,NULL,25,'Ambulance (4x4)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695895','2026-06-19 02:53:20.695895');
INSERT INTO "item" VALUES(69,'45589f30-3146-446c-acb5-6e415fe9a189',NULL,NULL,NULL,26,'Cargo Truck (6-Ton)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695897','2026-06-19 02:53:20.695897');
INSERT INTO "item" VALUES(70,'165522c8-071f-4877-aad5-d503f790354a',NULL,NULL,NULL,26,'Cargo Truck (10-Ton)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695899','2026-06-19 02:53:20.695899');
INSERT INTO "item" VALUES(71,'295ea173-9d16-430c-8cd6-d159f970ef88',NULL,NULL,NULL,26,'Dump Truck',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695901','2026-06-19 02:53:20.695901');
INSERT INTO "item" VALUES(72,'a0e48998-4fb0-4087-a7f0-491896494dfa',NULL,NULL,NULL,26,'Water Tanker Truck',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695903','2026-06-19 02:53:20.695904');
INSERT INTO "item" VALUES(73,'232586fa-3f8a-477c-9390-7efa9f78d182',NULL,NULL,NULL,26,'Fuel Tanker',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695905','2026-06-19 02:53:20.695906');
INSERT INTO "item" VALUES(74,'11633d86-96e2-4294-8c15-361649027df4',NULL,NULL,NULL,26,'Bulldozer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695907','2026-06-19 02:53:20.695908');
INSERT INTO "item" VALUES(75,'38290e87-2160-4a26-aaf1-0452b1e08285',NULL,NULL,NULL,26,'Excavator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695909','2026-06-19 02:53:20.695910');
INSERT INTO "item" VALUES(76,'50f5048c-c017-4933-a91b-f6f4fe53c45d',NULL,NULL,NULL,26,'Forklift',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695911','2026-06-19 02:53:20.695912');
INSERT INTO "item" VALUES(77,'5c97ad77-c53e-4c04-be9d-bf603ba2ebb9',NULL,NULL,NULL,26,'Backhoe Loader',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695913','2026-06-19 02:53:20.695914');
INSERT INTO "item" VALUES(78,'f01a07c7-9f54-408a-a68c-836db904feb8',NULL,NULL,NULL,27,'Outboard Motor (Boat)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695915','2026-06-19 02:53:20.695916');
INSERT INTO "item" VALUES(79,'fdf4b329-5870-433c-a89c-2d2b3f56eeca',NULL,NULL,NULL,27,'Rescue Boat (Inflatable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695917','2026-06-19 02:53:20.695918');
INSERT INTO "item" VALUES(80,'fcbe0a71-31b1-4d18-8b7c-babd5f7db699',NULL,NULL,NULL,27,'Drone (Search)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695919','2026-06-19 02:53:20.695920');
INSERT INTO "item" VALUES(81,'734ea4f8-92fa-419a-a142-7046d28ed10d',NULL,NULL,NULL,28,'Tire (Vehicle)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695922','2026-06-19 02:53:20.695922');
INSERT INTO "item" VALUES(82,'a9d3931f-9c1d-404b-b425-fa93f52c7310',NULL,NULL,NULL,28,'Jump Starter Pack',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695924','2026-06-19 02:53:20.695924');
INSERT INTO "item" VALUES(83,'9fa71b22-2fbb-450f-b5a9-43ad9d2bd2e8',NULL,NULL,NULL,28,'Tow Cable',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695926','2026-06-19 02:53:20.695926');
INSERT INTO "item" VALUES(84,'adeccaec-b854-4bde-97f3-79a0d2640957',NULL,NULL,NULL,28,'Hydraulic Jack',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695928','2026-06-19 02:53:20.695928');
INSERT INTO "item" VALUES(85,'a9ee741c-cd70-4edb-bedf-5dc28f858f66',NULL,NULL,NULL,28,'Tool Kit (Vehicle)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695930','2026-06-19 02:53:20.695931');
INSERT INTO "item" VALUES(86,'b4023b33-1f58-43f8-93e5-d4c7c1854d3a',NULL,NULL,NULL,28,'Fire Extinguisher (Vehicle)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695932','2026-06-19 02:53:20.695933');
INSERT INTO "item" VALUES(87,'8c31761c-c5fc-468d-81d6-84716094bb79',NULL,NULL,NULL,25,'Fuel Can (20L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Hazardous',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695934','2026-06-19 02:53:20.695935');
INSERT INTO "item" VALUES(88,'e50d1ccf-6f7c-46c5-966b-1c669703a215',NULL,NULL,NULL,28,'Warning Triangle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695936','2026-06-19 02:53:20.695937');
INSERT INTO "item" VALUES(89,'5d69fe56-8089-4d7d-9faa-137b0346fec3',NULL,NULL,NULL,28,'Safety Vest (Reflective)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695938','2026-06-19 02:53:20.695939');
INSERT INTO "item" VALUES(90,'363b5139-d7c7-4a2f-9ee6-398c3e64d330',NULL,NULL,NULL,29,'Satellite Phone',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695940','2026-06-19 02:53:20.695941');
INSERT INTO "item" VALUES(91,'59f2a24d-72cc-4689-a800-7a01f76270cc',NULL,NULL,NULL,29,'Handheld Radio (VHF)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695942','2026-06-19 02:53:20.695943');
INSERT INTO "item" VALUES(92,'369b4f8d-b6e8-4f11-950a-2ae2f86d330a',NULL,NULL,NULL,29,'Handheld Radio (UHF)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695944','2026-06-19 02:53:20.695945');
INSERT INTO "item" VALUES(93,'da248dcc-5d19-4929-aba6-22ba00d5043c',NULL,NULL,NULL,29,'Base Station Radio',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695946','2026-06-19 02:53:20.695947');
INSERT INTO "item" VALUES(94,'ba520492-44e3-4e0c-ae49-5fe2ba8b125f',NULL,NULL,NULL,29,'Megaphone (Battery)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695949','2026-06-19 02:53:20.695949');
INSERT INTO "item" VALUES(95,'b534147b-21b9-45ab-8f9b-9078908ab8b5',NULL,NULL,NULL,30,'Generator (2kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695951','2026-06-19 02:53:20.695951');
INSERT INTO "item" VALUES(96,'71a2e75d-1faf-4d53-90e6-b10ce85276ef',NULL,NULL,NULL,30,'Generator (5kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695955','2026-06-19 02:53:20.695956');
INSERT INTO "item" VALUES(97,'2043e739-f09d-4a5f-9837-e9cf4ab6c626',NULL,NULL,NULL,30,'Generator (10kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695957','2026-06-19 02:53:20.695958');
INSERT INTO "item" VALUES(98,'8afd8b9b-1975-4e65-9f70-ceffdfd9901a',NULL,NULL,NULL,30,'Solar Panel (Portable 100W)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695959','2026-06-19 02:53:20.695960');
INSERT INTO "item" VALUES(99,'af0af9c6-da0d-4a23-867c-5621c3722f8d',NULL,NULL,NULL,30,'Solar Panel (Portable 300W)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695962','2026-06-19 02:53:20.695962');
INSERT INTO "item" VALUES(100,'eabe9210-a5ca-464e-9346-138f19da7cb8',NULL,NULL,NULL,30,'Power Station (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695964','2026-06-19 02:53:20.695964');
INSERT INTO "item" VALUES(101,'ed030ead-1de6-4799-b640-a711014b7256',NULL,NULL,NULL,30,'LED Flood Light',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695966','2026-06-19 02:53:20.695966');
INSERT INTO "item" VALUES(102,'8fe9a4b6-d455-4ec4-95fa-25de186118db',NULL,NULL,NULL,30,'Extension Cable (50m)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695968','2026-06-19 02:53:20.695968');
INSERT INTO "item" VALUES(103,'dc35d125-905b-40f6-9c35-d615f471266b',NULL,NULL,NULL,30,'Power Distribution Box',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695970','2026-06-19 02:53:20.695970');
INSERT INTO "item" VALUES(104,'9f7dd9b5-29ea-452b-983a-5af4bf599386',NULL,NULL,NULL,31,'Camp Tent (10 Person)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695972','2026-06-19 02:53:20.695973');
INSERT INTO "item" VALUES(105,'49af2ede-60ee-41e9-bd3a-b543fef9aa6e',NULL,NULL,NULL,31,'Camp Tent (20 Person)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695974','2026-06-19 02:53:20.695975');
INSERT INTO "item" VALUES(106,'f8ebd217-6b27-4156-8c97-0502accce220',NULL,NULL,NULL,31,'Cot (Folding)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695976','2026-06-19 02:53:20.695977');
INSERT INTO "item" VALUES(107,'2b047fe8-a081-4818-b9e1-427881d2b6cf',NULL,NULL,NULL,31,'Sleeping Bag',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695978','2026-06-19 02:53:20.695979');
INSERT INTO "item" VALUES(108,'30afc87e-2d3e-407a-9186-4306d4d1f2e3',NULL,NULL,NULL,31,'Camp Table',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695980','2026-06-19 02:53:20.695981');
INSERT INTO "item" VALUES(109,'6db34d27-a55f-40c4-b642-5e1384c82e0c',NULL,NULL,NULL,31,'Camp Chair',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695982','2026-06-19 02:53:20.695983');
INSERT INTO "item" VALUES(110,'8ecc6a2e-a68d-4ba0-90b4-331edc600867',NULL,NULL,NULL,32,'Water Bladder (1000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695984','2026-06-19 02:53:20.695985');
INSERT INTO "item" VALUES(111,'ab95c371-a5cc-4270-8820-8c87d7da9ed3',NULL,NULL,NULL,32,'Water Bladder (2000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695987','2026-06-19 02:53:20.695987');
INSERT INTO "item" VALUES(112,'13248816-b2fc-4fd6-be5e-ce39d8e849fe',NULL,NULL,NULL,32,'Water Treatment Unit (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695989','2026-06-19 02:53:20.695989');
INSERT INTO "item" VALUES(113,'1bbac5dc-74a8-465d-8cbb-8958217dd979',NULL,NULL,NULL,32,'Water Pump (Submersible)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695991','2026-06-19 02:53:20.695991');
INSERT INTO "item" VALUES(114,'68429e8a-e144-4c2a-8a41-74d84f5f2a64',NULL,NULL,NULL,32,'Water Tank (Plastic 500L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695993','2026-06-19 02:53:20.695993');
INSERT INTO "item" VALUES(115,'2c021536-2cec-4890-9df2-fbbc30de5197',NULL,NULL,NULL,32,'Water Tank (Plastic 1000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695995','2026-06-19 02:53:20.695996');
INSERT INTO "item" VALUES(116,'6d0ed0f1-b4d7-4ebb-942c-b90360780ec3',NULL,NULL,NULL,32,'Collapsible Jerry Can (10L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695997','2026-06-19 02:53:20.695998');
INSERT INTO "item" VALUES(117,'8e177d17-85d9-45e4-8afc-e506aaf9588f',NULL,NULL,NULL,32,'Portable Toilet',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.695999','2026-06-19 02:53:20.696000');
INSERT INTO "item" VALUES(118,'31747b7c-0711-474a-8a0c-d0da0b3c5af6',NULL,NULL,NULL,32,'Shower Unit (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696001','2026-06-19 02:53:20.696002');
INSERT INTO "item" VALUES(119,'a4a7d377-f2b8-4e51-a4be-c7a3898680d3',NULL,NULL,NULL,33,'Fire Extinguisher (ABC 6kg)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696003','2026-06-19 02:53:20.696004');
INSERT INTO "item" VALUES(120,'e4570a9e-81a2-4126-b1b0-1ba70651ee9f',NULL,NULL,NULL,33,'Fire Extinguisher (CO2)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696005','2026-06-19 02:53:20.696006');
INSERT INTO "item" VALUES(121,'ac3e5350-15e3-48df-a8af-4da185e25618',NULL,NULL,NULL,33,'Fire Hose (15m)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696007','2026-06-19 02:53:20.696008');
INSERT INTO "item" VALUES(122,'a8688765-656f-47fe-b759-6204c5f87428',NULL,NULL,NULL,33,'Fire Nozzle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696009','2026-06-19 02:53:20.696010');
INSERT INTO "item" VALUES(123,'8a5655f7-3d72-4a1e-adef-86fdbbdeca9b',NULL,NULL,NULL,33,'Fire Blanket',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696011','2026-06-19 02:53:20.696012');
INSERT INTO "item" VALUES(124,'410fbf30-0e08-4bbc-b741-c6884335caae',NULL,NULL,NULL,33,'Smoke Detector',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696013','2026-06-19 02:53:20.696014');
INSERT INTO "item" VALUES(125,'ce7a7c0c-a486-494d-b461-511802304eb4',NULL,NULL,NULL,31,'First Aid Kit (Workplace)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696015','2026-06-19 02:53:20.696016');
INSERT INTO "item" VALUES(126,'455db8ee-2bd2-4857-947d-3aa0bd7178eb',NULL,NULL,NULL,31,'Emergency Whistle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696018','2026-06-19 02:53:20.696018');
INSERT INTO "item" VALUES(127,'b1b535a1-d0d8-41bb-86f6-82ee5c60006d',NULL,NULL,NULL,31,'Dust Mask (N95)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696020','2026-06-19 02:53:20.696020');
INSERT INTO "item" VALUES(128,'ad53975f-e383-4aaa-9089-1e4a5fe73613',NULL,NULL,NULL,31,'Safety Goggles',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696022','2026-06-19 02:53:20.696022');
INSERT INTO "item" VALUES(129,'b846082e-a3df-48a3-b12f-277e99e327af',NULL,NULL,NULL,31,'Rain Poncho',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-19 02:53:20.696024','2026-06-19 02:53:20.696024');
INSERT INTO "item" VALUES(130,'cd134f86-135a-4235-a3a8-82a3f68a7400','ITM-0130','','',1,'Rice basmati','चामल','','Kg',0,0,0,1,0,0,0,1,'','','Active',1,NULL,'2026-06-19 11:10:22.475483','2026-06-19 11:10:22.475487');
INSERT INTO "item" VALUES(131,'a5f8b23c-c339-4490-9933-c41912efb3ff','ITM-0131','','',1,'Daal Mix','दाल मिक्स','','Kg',0,0,0,1,0,0,0,1,'','','Active',1,NULL,'2026-06-19 11:10:53.619152','2026-06-19 11:10:53.619160');
INSERT INTO "item" VALUES(132,'c33e278f-e9f3-416b-8118-288937b40fa5','ITM-0132','','',3,'Bucket','बकेट','','Piece',0,0,0,0,0,0,0,1,'','','Active',1,NULL,'2026-06-19 11:11:25.675974','2026-06-19 11:11:25.675981');
INSERT INTO "item" VALUES(133,'bb22999f-0c41-434e-9c90-489dd3a2b630','ITM-0133','','',2,'Blanket','बिलेङकेट','','Piece',0,0,0,0,0,0,0,1,'','','Active',1,NULL,'2026-06-19 11:11:57.981085','2026-06-19 11:11:57.981092');
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
INSERT INTO "stock_receipt" VALUES(1,'RCPT-523481','2026-06-19',1,NULL,'Local Government','','','','','','','',NULL,'','',NULL,'','',1,'2026-06-19 11:13:26.949361');
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
INSERT INTO "stock_receipt_item" VALUES(1,1,130,200,'Kg','111','121','2026-06-19','2027-04-13',60.0,12000.0);
INSERT INTO "stock_receipt_item" VALUES(2,1,131,50,'Kg','222','231','2026-06-19','2027-04-13',150.0,7500.0);
INSERT INTO "stock_receipt_item" VALUES(3,1,132,50,'Piece','333','214','2026-06-19','2026-06-19',500.0,25000.0);
INSERT INTO "stock_receipt_item" VALUES(4,1,133,100,'Piece','444','234','2026-06-19','2026-06-19',100.0,10000.0);
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
INSERT INTO "user" VALUES(1,'admin','scrypt:32768:8:1$974ezo6MacXcg5yK$e7ddd91c833590fba83a29080ee519515bf91f7fdb241f13a0380019a7d53238f16f7622bec57410b9a84507ac116d33405f050677260af5cdab40f5f67d0a4f','admin','System Administrator',1,'2026-06-19 02:53:20','2026-06-20 02:37:38.562470+00:00');
INSERT INTO "user" VALUES(2,'editor','scrypt:32768:8:1$21XdXeVpFRzh4RBh$3cd30949ab530fed974094985542dc2e6063784312e0c66560319ce1d1c83779c9fb33cdfb70e3c9e386da53716fa3041184af4ff3395be652047d629e448012','editor','Data Editor',1,'2026-06-19 02:53:20','2026-06-20 02:34:37.370771+00:00');
INSERT INTO "user" VALUES(3,'viewer','scrypt:32768:8:1$4Q2dowKHesvlAUXV$f800f754a2fa2507db46a15b9e87c9482cba9fced839396c61daae33ca95dda18976f89d274954026855d7e43fa9d4fa0eac059dd6465d45f45fe65d28686b80','viewer','Read Only User',1,'2026-06-19 02:53:20','2026-06-20 02:33:25.600786+00:00');
INSERT INTO "user" VALUES(4,'operator','scrypt:32768:8:1$2KfXTtDOiaERNEH8$24a28a97c771108cc28aaf50ae5c00e9137eaf23bb07f15df3213e8889fcf435132e1762fd097b808d2922612f503d3bcd1504b82aba22ec2d302428997a0591','operator','Operations Officer',1,'2026-06-19 02:53:20',NULL);
INSERT INTO "user" VALUES(5,'finance','scrypt:32768:8:1$if4N3abp1UGZ7ZTF$1f0ffba696a336d24bb12645790ffdf76e5f39a3e01c1839e071ddf87e91abfbea1c435705e88cffb36014bd5f72644e72babdb9d1bd7936b396a1b098fc6d51','finance','Finance Officer',1,'2026-06-19 02:53:20',NULL);
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
INSERT INTO "warehouse" VALUES(1,'Kathmandu','TRM_WH2','Thalara Kholi','Prakash Bhandari','9741276350',2000.0,'This is main Warehouse operated by LEOC','2026-06-19 11:08:22.485841','2026-06-20 02:24:17.663068');
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
CREATE TABLE weekly_forecast (
	id INTEGER NOT NULL, 
	rainfall_snowfall VARCHAR(100), 
	high_temperature VARCHAR(50), 
	low_temperature VARCHAR(50), 
	forecast_status VARCHAR(100), 
	forecast_info TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, date_from VARCHAR(10), date_to VARCHAR(10), 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_warehouse_code ON warehouse (code);
CREATE INDEX ix_supplier_name ON supplier (name);
CREATE UNIQUE INDEX ix_category_name ON category (name);
CREATE INDEX ix_activity_log_created_at ON activity_log (created_at);
CREATE INDEX ix_activity_log_username ON activity_log (username);
CREATE INDEX ix_activity_log_user_id ON activity_log (user_id);
CREATE INDEX ix_activity_log_action ON activity_log (action);
CREATE INDEX ix_activity_log_resource ON activity_log (resource);
CREATE INDEX ix_incident_status ON incident (status);
CREATE INDEX ix_incident_fiscal_year ON incident (fiscal_year);
CREATE INDEX ix_incident_incident_type ON incident (incident_type);
CREATE UNIQUE INDEX ix_daily_report_log_report_date_bs ON daily_report_log (report_date_bs);
CREATE INDEX ix_daily_bulletin_valid_from ON daily_bulletin (valid_from);
CREATE UNIQUE INDEX ix_cash_fund_fund_no ON cash_fund (fund_no);
CREATE INDEX ix_beneficiary_name ON beneficiary (name);
CREATE INDEX ix_warehouse_zone_warehouse_id ON warehouse_zone (warehouse_id);
CREATE INDEX ix_item_category_id ON item (category_id);
CREATE UNIQUE INDEX ix_item_uuid ON item (uuid);
CREATE INDEX ix_item_name ON item (name);
CREATE UNIQUE INDEX ix_item_item_code ON item (item_code);
CREATE INDEX ix_stock_receipt_supplier_id ON stock_receipt (supplier_id);
CREATE INDEX ix_stock_receipt_warehouse_id ON stock_receipt (warehouse_id);
CREATE UNIQUE INDEX ix_stock_receipt_receipt_no ON stock_receipt (receipt_no);
CREATE INDEX ix_relief_request_status ON relief_request (status);
CREATE UNIQUE INDEX ix_relief_request_request_number ON relief_request (request_number);
CREATE INDEX ix_relief_request_priority ON relief_request (priority);
CREATE INDEX ix_relief_request_incident_id ON relief_request (incident_id);
CREATE INDEX ix_disaster_assessment_incident_id ON disaster_assessment (incident_id);
CREATE INDEX ix_disaster_assessment_fiscal_year ON disaster_assessment (fiscal_year);
CREATE INDEX ix_disaster_assessment_disaster_type ON disaster_assessment (disaster_type);
CREATE INDEX ix_disaster_assessment_disaster_date_bs ON disaster_assessment (disaster_date_bs);
CREATE INDEX ix_stock_transfer_from_warehouse_id ON stock_transfer (from_warehouse_id);
CREATE INDEX ix_stock_transfer_to_warehouse_id ON stock_transfer (to_warehouse_id);
CREATE UNIQUE INDEX ix_stock_transfer_transfer_no ON stock_transfer (transfer_no);
CREATE INDEX ix_cash_receipt_fund_id ON cash_receipt (fund_id);
CREATE UNIQUE INDEX ix_cash_receipt_receipt_no ON cash_receipt (receipt_no);
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
CREATE INDEX ix_dispatch_relief_request_id ON dispatch (relief_request_id);
CREATE UNIQUE INDEX ix_dispatch_dispatch_number ON dispatch (dispatch_number);
CREATE INDEX ix_stock_transfer_item_transfer_id ON stock_transfer_item (transfer_id);
CREATE UNIQUE INDEX ix_cash_distribution_distribution_no ON cash_distribution (distribution_no);
CREATE INDEX ix_cash_distribution_incident_id ON cash_distribution (incident_id);
CREATE INDEX ix_cash_distribution_fund_id ON cash_distribution (fund_id);
CREATE INDEX ix_cash_distribution_fiscal_year ON cash_distribution (fiscal_year);
CREATE INDEX ix_cash_distribution_relief_request_id ON cash_distribution (relief_request_id);
CREATE INDEX ix_cash_distribution_cash_request_id ON cash_distribution (cash_request_id);
CREATE INDEX ix_dispatch_item_dispatch_id ON dispatch_item (dispatch_id);
CREATE INDEX ix_distribution_fiscal_year ON distribution (fiscal_year);
CREATE INDEX ix_distribution_incident_id ON distribution (incident_id);
CREATE UNIQUE INDEX ix_distribution_distribution_no ON distribution (distribution_no);
CREATE INDEX ix_distribution_dispatch_id ON distribution (dispatch_id);
CREATE INDEX ix_cash_distribution_beneficiary_beneficiary_id ON cash_distribution_beneficiary (beneficiary_id);
CREATE INDEX ix_cash_distribution_beneficiary_distribution_id ON cash_distribution_beneficiary (distribution_id);
CREATE INDEX ix_distribution_beneficiary_beneficiary_id ON distribution_beneficiary (beneficiary_id);
CREATE INDEX ix_distribution_beneficiary_distribution_id ON distribution_beneficiary (distribution_id);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('user',5);
COMMIT;
