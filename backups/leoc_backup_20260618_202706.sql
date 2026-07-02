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
INSERT INTO "app_settings" VALUES(1,'office_name','"थलारा गाउँपालिका"','2026-06-10 10:49:54.015097','2026-06-17 00:04:21.185630');
INSERT INTO "app_settings" VALUES(2,'fiscal_year','2081/82','2026-06-10 10:49:54.018146','2026-06-10 10:49:54.018148');
INSERT INTO "app_settings" VALUES(3,'default_language','"Nepali"','2026-06-10 10:49:54.020458','2026-06-17 00:03:20.468878');
INSERT INTO "app_settings" VALUES(4,'fiscal_years','["2080/81", "2081/82", "2082/83", "2083/84", "2084/85"]','2026-06-10 10:49:54.022737','2026-06-10 10:49:54.022739');
INSERT INTO "app_settings" VALUES(5,'active_fiscal_year','2081/82','2026-06-10 10:49:54.024983','2026-06-10 10:49:54.024985');
INSERT INTO "app_settings" VALUES(6,'disaster_types','["\u092d\u0942\u0915\u092e\u094d\u092a (Earthquake)", "\u092c\u093e\u0922\u0940 (Flood)", "\u092a\u0939\u093f\u0930\u094b (Landslide)", "\u0906\u0901\u0927\u0940 (Storm)", "\u0906\u0917\u0932\u093e\u0917\u0940 (Fire)", "\u0905\u0928\u094d\u092f (Other)"]','2026-06-10 10:49:54.027183','2026-06-10 10:49:54.027187');
INSERT INTO "app_settings" VALUES(7,'ssf_types','["OAS (\u092c\u0930\u094d\u0937\u093e \u092a\u0947\u0928\u094d\u0938\u0928)", "\u0935\u093f\u0927\u0935\u093e (Widow)", "\u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e (Disabled)", "\u0915\u094b\u0939\u0940 \u0928\u092d\u090f\u0915\u094b (Endangered)", "\u092c\u093e\u0932 \u092d\u0924\u094d\u0924\u093e (Child Grant)", "\u0905\u0928\u094d\u092f (Other)"]','2026-06-10 10:49:54.029473','2026-06-10 10:49:54.029476');
INSERT INTO "app_settings" VALUES(8,'phone','"9865654665"','2026-06-10 11:05:29.008119','2026-06-17 00:03:20.404393');
INSERT INTO "app_settings" VALUES(9,'email','"thalaramun@gmail.com"','2026-06-10 11:05:29.038358','2026-06-10 12:58:19.781012');
INSERT INTO "app_settings" VALUES(10,'address','"खोली बझाङ"','2026-06-10 11:05:29.071623','2026-06-17 00:04:21.250245');
INSERT INTO "app_settings" VALUES(11,'report_header','"Thalara Rural municipality\nOffice of Rural Municipal Executive\nKholi, Bajhang"','2026-06-10 11:05:29.128241','2026-06-17 00:03:20.493030');
INSERT INTO "app_settings" VALUES(12,'report_footer','"All Rights Reserved TRM - 2026"','2026-06-10 11:05:29.156811','2026-06-17 00:03:20.515648');
INSERT INTO "app_settings" VALUES(13,'relief_items','["खाद्य सामाग्री (Food Packages)", "पानीको बोतल (Water Bottles)", "औषधि सामाग्री (Medical Supplies)", "कम्बल (Blankets)", "लुगा सामाग्री (Clothing)", "स्वास्थ्य सामाग्री (Hygiene Kits)", "घर बनाउने सामाग्री (Shelter Materials)", "बच्चाको हेरचाह (Baby Care)", "अन्य (Other)"]','2026-06-17 13:41:20.653969','2026-06-17 13:41:20.653975');
INSERT INTO "app_settings" VALUES(14,'organization_name','थलारा गाउँपालिका','2026-06-17 13:41:20.660258','2026-06-17 13:41:20.660263');
INSERT INTO "app_settings" VALUES(15,'organization_address','खोली, बझाङ','2026-06-17 13:41:20.664364','2026-06-17 13:41:20.664368');
INSERT INTO "app_settings" VALUES(16,'organization_phone','XXX-XXXXXXX','2026-06-17 13:41:20.668221','2026-06-17 13:41:20.668227');
INSERT INTO "app_settings" VALUES(17,'organization_email','leoc@thalara.gov.np','2026-06-17 13:41:20.671799','2026-06-17 13:41:20.671803');
INSERT INTO "app_settings" VALUES(18,'currency','NPR','2026-06-17 13:41:20.675451','2026-06-17 13:41:20.675456');
INSERT INTO "app_settings" VALUES(19,'language','ne','2026-06-17 13:41:20.679272','2026-06-17 13:41:20.679277');
INSERT INTO "app_settings" VALUES(20,'default_warehouse','','2026-06-17 13:41:20.682722','2026-06-17 13:41:20.682726');
CREATE TABLE beneficiary (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	national_id VARCHAR(100), 
	phone VARCHAR(50), 
	address VARCHAR(300), 
	municipality VARCHAR(200), 
	ward INTEGER, 
	family_members INTEGER, 
	bank_account VARCHAR(100), 
	mobile_wallet VARCHAR(100), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, father_name VARCHAR(200), tole VARCHAR(200), current_shelter_location VARCHAR(300), coordinates VARCHAR(100), family_members_json TEXT DEFAULT '[]', in_social_security_fund BOOLEAN DEFAULT 0, ssf_type VARCHAR(100), poverty_card_holder BOOLEAN DEFAULT 0, bank_account_holder_name VARCHAR(200), bank_name VARCHAR(200), 
	PRIMARY KEY (id)
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
	officer VARCHAR(200), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, fiscal_year VARCHAR(20), 
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
INSERT INTO "category" VALUES(1,'Food',NULL,'2026-06-10 10:50:01.244892');
INSERT INTO "category" VALUES(2,'Rescue','','2026-06-17 00:06:24.207959');
INSERT INTO "category" VALUES(3,'Shelter',NULL,'2026-06-17 13:41:40.419629');
INSERT INTO "category" VALUES(4,'Relief Supplies',NULL,'2026-06-17 13:41:40.419636');
INSERT INTO "category" VALUES(5,'WASH (Water/Sanitation)',NULL,'2026-06-17 13:41:40.419637');
INSERT INTO "category" VALUES(6,'Education Materials',NULL,'2026-06-17 13:41:40.419638');
INSERT INTO "category" VALUES(7,'Protection Gear',NULL,'2026-06-17 13:41:40.419639');
INSERT INTO "category" VALUES(8,'Fuel & Lubricants',NULL,'2026-06-17 13:41:40.419640');
INSERT INTO "category" VALUES(9,'Construction Materials',NULL,'2026-06-17 13:41:40.419640');
INSERT INTO "category" VALUES(10,'Livestock Supplies',NULL,'2026-06-17 13:41:40.419641');
INSERT INTO "category" VALUES(11,'Clothing & Textiles',NULL,'2026-06-17 13:41:40.419641');
INSERT INTO "category" VALUES(12,'Kitchen & Cooking',NULL,'2026-06-17 13:41:40.419642');
INSERT INTO "category" VALUES(13,'Baby & Child Care',NULL,'2026-06-17 13:41:40.419643');
INSERT INTO "category" VALUES(14,'Other',NULL,'2026-06-17 13:41:40.419643');
INSERT INTO "category" VALUES(15,'Rescue - Search & Rescue Tools',NULL,'2026-06-17 13:41:40.419644');
INSERT INTO "category" VALUES(16,'Rescue - Ropes & Rigging',NULL,'2026-06-17 13:41:40.419645');
INSERT INTO "category" VALUES(17,'Rescue - Cutting & Breaking',NULL,'2026-06-17 13:41:40.419645');
INSERT INTO "category" VALUES(18,'Rescue - Lighting & Signal',NULL,'2026-06-17 13:41:40.419646');
INSERT INTO "category" VALUES(19,'Rescue - Water Rescue',NULL,'2026-06-17 13:41:40.419647');
INSERT INTO "category" VALUES(20,'Rescue - Confined Space',NULL,'2026-06-17 13:41:40.419647');
INSERT INTO "category" VALUES(21,'Medical - Consumables',NULL,'2026-06-17 13:41:40.419648');
INSERT INTO "category" VALUES(22,'Medical - Equipment',NULL,'2026-06-17 13:41:40.419648');
INSERT INTO "category" VALUES(23,'Medical - First Aid',NULL,'2026-06-17 13:41:40.419649');
INSERT INTO "category" VALUES(24,'Medical - Diagnostic',NULL,'2026-06-17 13:41:40.419649');
INSERT INTO "category" VALUES(25,'Medical - Mobility & Transport',NULL,'2026-06-17 13:41:40.419650');
INSERT INTO "category" VALUES(26,'Vehicles - Light',NULL,'2026-06-17 13:41:40.419651');
INSERT INTO "category" VALUES(27,'Vehicles - Heavy',NULL,'2026-06-17 13:41:40.419651');
INSERT INTO "category" VALUES(28,'Vehicles - Water & Air',NULL,'2026-06-17 13:41:40.419652');
INSERT INTO "category" VALUES(29,'Vehicle Parts & Tools',NULL,'2026-06-17 13:41:40.419652');
INSERT INTO "category" VALUES(30,'Preparedness - Communication',NULL,'2026-06-17 13:41:40.419653');
INSERT INTO "category" VALUES(31,'Preparedness - Power & Lighting',NULL,'2026-06-17 13:41:40.419653');
INSERT INTO "category" VALUES(32,'Preparedness - Shelter & Camp',NULL,'2026-06-17 13:41:40.419654');
INSERT INTO "category" VALUES(33,'Preparedness - Water & Sanitation',NULL,'2026-06-17 13:41:40.419654');
INSERT INTO "category" VALUES(34,'Preparedness - Fire Safety',NULL,'2026-06-17 13:41:40.419655');
CREATE TABLE daily_report_log (
	id INTEGER NOT NULL, 
	report_date_bs VARCHAR(10) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO "daily_report_log" VALUES(1,'2026-06-10','2026-06-10 10:59:22.300581');
INSERT INTO "daily_report_log" VALUES(2,'2026-06-17','2026-06-17 16:31:14.631250');
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
INSERT INTO "disaster_assessment" VALUES(1,1,'भूकम्प (Earthquake)','2081/82','','',0,0,0,0,0,0,0,0,0,0,0,0.0,'',0,0,0,0,0,0,0,0,0,0,0,0,'',1,'2026-06-10 10:59:49.469347','2026-06-10 10:59:49.469351');
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
INSERT INTO "dispatch" VALUES(1,'DSP-0001','2026-06-10',1,1,NULL,'Ward 5','Shyam',NULL,NULL,1,'2026-06-10 10:50:01.318776');
INSERT INTO "dispatch" VALUES(2,'DSP-0002','2026-06-10',1,1,NULL,'Ward 5','Shyam',NULL,NULL,1,'2026-06-10 10:50:01.387607');
INSERT INTO "dispatch" VALUES(3,'DSP-1336','2026-06-10',1,2,NULL,'Ward 5','Kiran Singh','','',1,'2026-06-10 12:08:05.850260');
INSERT INTO "dispatch" VALUES(4,'DSP-8818','2026-06-17',1,3,4,'','','','',1,'2026-06-17 01:23:54.876523');
INSERT INTO "dispatch" VALUES(5,'DSP-1986','2026-06-18',1,7,6,'Kholi','Bharat Rokaya','1234567890','',1,'2026-06-18 01:22:26.326481');
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
INSERT INTO "dispatch_item" VALUES(1,1,1,100,NULL,'B001',NULL);
INSERT INTO "dispatch_item" VALUES(2,2,1,100,NULL,'B002',NULL);
INSERT INTO "dispatch_item" VALUES(3,3,1,10,'Kg','','2026-06-30');
INSERT INTO "dispatch_item" VALUES(4,3,2,2,'Piece','',NULL);
INSERT INTO "dispatch_item" VALUES(5,4,2,1,'Piece','',NULL);
INSERT INTO "dispatch_item" VALUES(6,4,3,1,'Packet','',NULL);
INSERT INTO "dispatch_item" VALUES(7,4,1,5,'Kg','',NULL);
INSERT INTO "dispatch_item" VALUES(8,5,1,25,'Kg','',NULL);
INSERT INTO "dispatch_item" VALUES(9,5,2,5,'Piece','',NULL);
INSERT INTO "dispatch_item" VALUES(10,5,3,5,'Packet','',NULL);
CREATE TABLE distribution (
	id INTEGER NOT NULL, 
	distribution_no VARCHAR(50) NOT NULL, 
	dispatch_id INTEGER NOT NULL, 
	incident_id INTEGER NOT NULL, 
	location VARCHAR(300), 
	distribution_date DATE NOT NULL, 
	officer VARCHAR(200), 
	remarks TEXT, 
	created_by INTEGER, 
	created_at DATETIME, latitude FLOAT, longitude FLOAT, fiscal_year VARCHAR(20), status VARCHAR(20) DEFAULT 'Completed', 
	PRIMARY KEY (id), 
	FOREIGN KEY(dispatch_id) REFERENCES dispatch (id), 
	FOREIGN KEY(incident_id) REFERENCES incident (id)
);
INSERT INTO "distribution" VALUES(1,'DIST-1906',4,3,'','2026-06-17','','',1,'2026-06-17 01:41:00.650236',NULL,NULL,NULL,'Completed');
INSERT INTO "distribution" VALUES(2,'DIST-7559',4,3,'','2026-06-17','','',1,'2026-06-17 17:05:51.653191',NULL,NULL,'2081/82','Completed');
INSERT INTO "distribution" VALUES(3,'DIST-3118',5,7,'','2026-06-18','','',1,'2026-06-18 02:36:54.713336',NULL,NULL,'2081/82','Completed');
CREATE TABLE distribution_beneficiary (
	id INTEGER NOT NULL, 
	distribution_id INTEGER NOT NULL, 
	family_name VARCHAR(200) NOT NULL, 
	id_number VARCHAR(100), 
	members INTEGER, 
	item VARCHAR(200), 
	quantity INTEGER NOT NULL, beneficiary_id INTEGER REFERENCES beneficiary(id), status VARCHAR(20) DEFAULT 'Received', photo VARCHAR(255), document VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(distribution_id) REFERENCES distribution (id)
);
INSERT INTO "distribution_beneficiary" VALUES(1,1,'Liladhar','',3,'PForm',1,NULL,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(2,1,'Liladhar','',3,'Masala',1,NULL,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(3,1,'Liladhar','',3,'Rice',5,NULL,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(4,2,'Manju Joshi','713036-364',5,'Masala',1,NULL,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(5,3,'मनमोहन अधिकारी','251002',3,'Rice',25,NULL,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(6,3,'मनमोहन अधिकारी','251002',3,'PForm',5,NULL,'Received',NULL,NULL);
INSERT INTO "distribution_beneficiary" VALUES(7,3,'मनमोहन अधिकारी','251002',3,'Masala',5,NULL,'Received',NULL,NULL);
CREATE TABLE incident (
	id INTEGER NOT NULL, 
	incident_name VARCHAR(200) NOT NULL, 
	incident_type VARCHAR(100) NOT NULL, 
	province VARCHAR(100), 
	district VARCHAR(100), 
	municipality VARCHAR(200), 
	ward INTEGER, 
	start_date DATE NOT NULL, 
	status VARCHAR(50), 
	description TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, disaster_date_bs VARCHAR(10), incident_time VARCHAR(10), coordinates VARCHAR(100), tole VARCHAR(200), severity VARCHAR(20) DEFAULT 'medium', weather_status VARCHAR(100), affected_people INTEGER DEFAULT 0, injured INTEGER DEFAULT 0, deaths INTEGER DEFAULT 0, missing_persons INTEGER DEFAULT 0, affected_people_male INTEGER DEFAULT 0, affected_people_female INTEGER DEFAULT 0, affected_households INTEGER DEFAULT 0, house_damaged INTEGER DEFAULT 0, house_destroyed INTEGER DEFAULT 0, public_building_damaged INTEGER DEFAULT 0, public_building_destroyed INTEGER DEFAULT 0, estimated_loss FLOAT DEFAULT 0.0, agriculture_crop_damage TEXT, road_blocked BOOLEAN DEFAULT 0, electricity_blocked BOOLEAN DEFAULT 0, communication_blocked BOOLEAN DEFAULT 0, drinking_water_disrupted BOOLEAN DEFAULT 0, cattle_lost INTEGER DEFAULT 0, cattle_injured INTEGER DEFAULT 0, poultry_lost INTEGER DEFAULT 0, poultry_injured INTEGER DEFAULT 0, goats_sheep_lost INTEGER DEFAULT 0, goats_sheep_injured INTEGER DEFAULT 0, other_livestock_lost INTEGER DEFAULT 0, other_livestock_injured INTEGER DEFAULT 0, rescue_operations TEXT, fiscal_year VARCHAR(20), 
	PRIMARY KEY (id)
);
INSERT INTO "incident" VALUES(1,'Flood','Flood','','','',NULL,'2026-06-10','Closed','','2026-06-10 10:50:01.220902','2026-06-17 00:31:00.206468',NULL,NULL,NULL,NULL,'medium',NULL,0,0,0,0,0,0,0,0,0,0,0,0.0,NULL,0,0,0,0,0,0,0,0,0,0,0,0,NULL,NULL);
INSERT INTO "incident" VALUES(2,'Landslide','Landslide','Supa','Bajhang','Thalara',5,'2026-06-10','Closed','','2026-06-10 12:04:56.000253','2026-06-17 00:31:06.046011',NULL,NULL,NULL,NULL,'medium',NULL,0,0,0,0,0,0,0,0,0,0,0,0.0,NULL,0,0,0,0,0,0,0,0,0,0,0,0,NULL,NULL);
INSERT INTO "incident" VALUES(3,'Fire ward 7','Fire','Supa','bajhang','Thalara',7,'2026-06-17','Active','','2026-06-17 00:31:51.009550','2026-06-17 00:31:51.009561',NULL,NULL,NULL,NULL,'medium',NULL,0,0,0,0,0,0,0,0,0,0,0,0.0,NULL,0,0,0,0,0,0,0,0,0,0,0,0,NULL,NULL);
INSERT INTO "incident" VALUES(6,'Heavy Rainfall','बाढी (Flood)',NULL,NULL,NULL,1,'2026-06-17','Active','','2026-06-17 15:55:24.413046','2026-06-17 15:55:24.413052','2052-01-05','10:20','','Kholi','medium','',0,0,0,0,0,0,0,0,0,0,0,0.0,'',1,1,0,0,0,0,0,0,0,0,0,0,'',NULL);
INSERT INTO "incident" VALUES(7,'आगलागि','आगलागी (Fire)',NULL,NULL,NULL,5,'2026-06-18','Active','विद्युत सट भएर आगलागि','2026-06-18 01:08:08.129847','2026-06-18 01:08:08.129860','2082-05-11','10:25','29.458965, 81.057157','हाट','high',NULL,3,1,0,0,1,2,1,1,0,0,0,50000.0,'सबै खाद्यान्न जलेको',0,1,0,0,3,0,0,1,0,1,0,0,'','2081/82');
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
INSERT INTO "inventory" VALUES(1,1,1,1013,0,'2026-06-18 01:22:26.334045');
INSERT INTO "inventory" VALUES(2,2,1,67,0,'2026-06-18 01:22:26.338067');
INSERT INTO "inventory" VALUES(3,3,1,194,0,'2026-06-18 01:22:26.340192');
INSERT INTO "inventory" VALUES(4,98,1,1,0,'2026-06-17 13:54:35.403863');
INSERT INTO "inventory" VALUES(5,15,1,10,0,'2026-06-17 14:01:34.562085');
INSERT INTO "inventory" VALUES(6,4,1,10,0,'2026-06-17 14:23:27.146923');
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
	storage_requirement VARCHAR(50), 
	photo VARCHAR(500), 
	status VARCHAR(20), 
	created_by INTEGER, 
	updated_by INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, is_distributable BOOLEAN DEFAULT 1, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
);
INSERT INTO "item" VALUES(1,'80a2adb5-2f18-4190-bf2c-d9ee6cffee32','ITM-0001','123',NULL,1,'Rice',NULL,NULL,'Kg',0,0,NULL,0,0,0,1,'Normal',NULL,'Active',1,NULL,'2026-06-10 10:50:01.260154','2026-06-10 10:50:01.260159',1);
INSERT INTO "item" VALUES(2,'e2ef4f53-3f06-4ad5-997d-64a8231ca300','ITM-0002','','',1,'PForm','पिफम','','Piece',25,100,0,0,1,0,0,'Normal','','Active',1,NULL,'2026-06-10 12:00:56.850724','2026-06-10 12:00:56.850735',1);
INSERT INTO "item" VALUES(3,'f114662c-d0e3-4c9d-b914-0c2559fada00','ITM-0003','','',1,'Masala','मसला','','Packet',100,500,365,1,0,0,1,'Cold Storage','','Active',1,NULL,'2026-06-17 00:07:52.538932','2026-06-17 00:07:52.538941',1);
INSERT INTO "item" VALUES(4,'15eb65e1-5164-441e-a17c-0f2ab401294e',NULL,NULL,NULL,16,'Cat-1 Rope (Static)',NULL,NULL,'Meter',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441492','2026-06-17 13:41:40.441499',0);
INSERT INTO "item" VALUES(5,'b74e4342-969c-4d43-bd36-3d34aa08336f',NULL,NULL,NULL,16,'Cat-2 Rope (Dynamic)',NULL,NULL,'Meter',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441502','2026-06-17 13:41:40.441503',0);
INSERT INTO "item" VALUES(6,'18fb1b92-52f6-4ac3-be57-3fbd610aefd9',NULL,NULL,NULL,16,'Webbing Sling (60cm)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441505','2026-06-17 13:41:40.441506',0);
INSERT INTO "item" VALUES(7,'a1e64bd8-88c9-48f8-9924-033257726b43',NULL,NULL,NULL,16,'Webbing Sling (120cm)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441508','2026-06-17 13:41:40.441509',0);
INSERT INTO "item" VALUES(8,'e9363062-1497-4495-b5c4-b3fbd8bda39f',NULL,NULL,NULL,16,'Carabiner (Screw Lock)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441510','2026-06-17 13:41:40.441511',0);
INSERT INTO "item" VALUES(9,'a0ae8ce3-30c7-4a51-9bb3-c607fe1177d8',NULL,NULL,NULL,16,'Carabiner (Auto Lock)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441513','2026-06-17 13:41:40.441513',0);
INSERT INTO "item" VALUES(10,'378c31e3-fa0e-4767-b654-49406e092cf5',NULL,NULL,NULL,16,'Descender (Figure 8)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441515','2026-06-17 13:41:40.441516',0);
INSERT INTO "item" VALUES(11,'fc7a23c8-c542-4a9e-8ee6-0fb76e8eac3e',NULL,NULL,NULL,16,'Pulley (Single)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441518','2026-06-17 13:41:40.441518',0);
INSERT INTO "item" VALUES(12,'855d1813-5ee6-44fc-8cc0-a394baa068ec',NULL,NULL,NULL,16,'Pulley (Double)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441520','2026-06-17 13:41:40.441521',0);
INSERT INTO "item" VALUES(13,'27bb6b21-a14b-4113-9e15-84dbb0c5aa8c',NULL,NULL,NULL,16,'Harness (Full Body)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441522','2026-06-17 13:41:40.441523',0);
INSERT INTO "item" VALUES(14,'ebbdde96-5e34-468f-b8c8-4fc9ee1ffe4b',NULL,NULL,NULL,16,'Harness (Chest)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441525','2026-06-17 13:41:40.441526',0);
INSERT INTO "item" VALUES(15,'27743c3e-0e63-401b-b468-e22b6675d317',NULL,NULL,NULL,15,'Helmet (Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441527','2026-06-17 13:41:40.441528',0);
INSERT INTO "item" VALUES(16,'6bca5e83-8a3c-4026-8a05-3f03cbbc25c9',NULL,NULL,NULL,18,'Headlamp (Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441529','2026-06-17 13:41:40.441530',0);
INSERT INTO "item" VALUES(17,'709775b1-f9ac-4df8-8f6f-639535c22993',NULL,NULL,NULL,18,'Rescue Flashlight',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441532','2026-06-17 13:41:40.441533',0);
INSERT INTO "item" VALUES(18,'ccf120d2-a5f0-4873-98e9-04b90161d5ef',NULL,NULL,NULL,18,'Signal Whistle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441534','2026-06-17 13:41:40.441535',0);
INSERT INTO "item" VALUES(19,'b9729464-7132-449b-b624-f63f113cd497',NULL,NULL,NULL,15,'Safety Glasses',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441536','2026-06-17 13:41:40.441537',0);
INSERT INTO "item" VALUES(20,'83088b73-2d66-4433-832b-fff48cac79b6',NULL,NULL,NULL,15,'Work Gloves (Leather)',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441539','2026-06-17 13:41:40.441540',0);
INSERT INTO "item" VALUES(21,'af1177ba-5927-4fa6-bff2-68d31318a69f',NULL,NULL,NULL,15,'Knee Pads',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441541','2026-06-17 13:41:40.441542',0);
INSERT INTO "item" VALUES(22,'e5835ea8-8f99-4162-803f-f62d13af3aa7',NULL,NULL,NULL,17,'Cutting Tool (Bolt Cutter)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441544','2026-06-17 13:41:40.441545',0);
INSERT INTO "item" VALUES(23,'098af332-2ba0-4931-8106-1948c0f1b45c',NULL,NULL,NULL,17,'Crowbar',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441547','2026-06-17 13:41:40.441548',0);
INSERT INTO "item" VALUES(24,'b22ca307-a7c4-4987-a8a5-dd2b48a59c94',NULL,NULL,NULL,17,'Sledge Hammer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441550','2026-06-17 13:41:40.441551',0);
INSERT INTO "item" VALUES(25,'037c7694-da1c-4d61-9b4d-225b17dd7bed',NULL,NULL,NULL,17,'Hacksaw',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441553','2026-06-17 13:41:40.441554',0);
INSERT INTO "item" VALUES(26,'5f1d2dd6-9b10-4958-9355-2c661e7caf24',NULL,NULL,NULL,15,'Shovel (Folding)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441556','2026-06-17 13:41:40.441556',0);
INSERT INTO "item" VALUES(27,'a286f990-b8a1-4868-a884-bfb439cb4466',NULL,NULL,NULL,15,'Stretcher (Basket)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441558','2026-06-17 13:41:40.441559',0);
INSERT INTO "item" VALUES(28,'66ffbe71-6b03-4f28-94d7-167417928034',NULL,NULL,NULL,15,'Stretcher (Foldable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441561','2026-06-17 13:41:40.441562',0);
INSERT INTO "item" VALUES(29,'7d6e718c-7ab4-49f4-b83d-0dd8e6a600c1',NULL,NULL,NULL,15,'Spine Board',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441564','2026-06-17 13:41:40.441565',0);
INSERT INTO "item" VALUES(30,'88c4fee5-7297-4090-afa5-ae235df134e7',NULL,NULL,NULL,15,'Cervical Collar (Set)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441569','2026-06-17 13:41:40.441570',0);
INSERT INTO "item" VALUES(31,'d8eeee47-72cd-450e-83a6-417f9972411d',NULL,NULL,NULL,19,'Life Jacket',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441571','2026-06-17 13:41:40.441571',0);
INSERT INTO "item" VALUES(32,'33e6caf7-49e3-4ebf-a6c3-e9a151e4f819',NULL,NULL,NULL,19,'Throw Bag (Water Rescue)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441573','2026-06-17 13:41:40.441573',0);
INSERT INTO "item" VALUES(33,'5f491456-1ac4-41dd-bca9-7db4bf3cab62',NULL,NULL,NULL,19,'Rescue Tube',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441574','2026-06-17 13:41:40.441575',0);
INSERT INTO "item" VALUES(34,'56ff92d6-e6b0-4a8d-8d45-1156991ac340',NULL,NULL,NULL,20,'Gas Detector (Multi)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441576','2026-06-17 13:41:40.441576',0);
INSERT INTO "item" VALUES(35,'c80967d9-b81b-4c3d-a9bd-d2efb6ccfc06',NULL,NULL,NULL,20,'Tripod Rescue System',NULL,NULL,'Set',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441577','2026-06-17 13:41:40.441578',0);
INSERT INTO "item" VALUES(36,'b18128e8-59bd-4220-9666-9711e9ea06d3',NULL,NULL,NULL,15,'Come-Along Winch',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441579','2026-06-17 13:41:40.441580',0);
INSERT INTO "item" VALUES(37,'b3e06a48-fe75-46a5-b664-2897c4f6dab5',NULL,NULL,NULL,16,'Rope Grab (ASAP)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441581','2026-06-17 13:41:40.441581',0);
INSERT INTO "item" VALUES(38,'fcaed1d9-6de6-49b7-aa2e-dba3847d37f3',NULL,NULL,NULL,16,'Edge Roller',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441582','2026-06-17 13:41:40.441583',0);
INSERT INTO "item" VALUES(39,'ff1fb2fb-6cd9-4eda-b0b8-604b410e74a8',NULL,NULL,NULL,16,'Prusik Loop',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441584','2026-06-17 13:41:40.441584',0);
INSERT INTO "item" VALUES(40,'209dc48b-015a-4ca0-9841-367d3abdec12',NULL,NULL,NULL,16,'Daisy Chain',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441585','2026-06-17 13:41:40.441586',0);
INSERT INTO "item" VALUES(41,'87733ee4-758a-45c0-a61b-ad4c4425b22f',NULL,NULL,NULL,15,'Ratchet Strap (Heavy)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441587','2026-06-17 13:41:40.441587',0);
INSERT INTO "item" VALUES(42,'af7925ac-6286-4e35-a861-2c59d14f3979',NULL,NULL,NULL,15,'Tarp (Waterproof)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441589','2026-06-17 13:41:40.441589',0);
INSERT INTO "item" VALUES(43,'bf09effa-b309-4101-94fe-8cd5daa1e0c4',NULL,NULL,NULL,22,'Oxygen Cylinder (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441590','2026-06-17 13:41:40.441591',0);
INSERT INTO "item" VALUES(44,'517b5593-99a6-4d43-bcba-fc3f392970d6',NULL,NULL,NULL,22,'Oxygen Regulator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441592','2026-06-17 13:41:40.441592',0);
INSERT INTO "item" VALUES(45,'6e76f613-9f42-4f63-acfa-86211eec0af6',NULL,NULL,NULL,24,'Pulse Oximeter',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441593','2026-06-17 13:41:40.441594',0);
INSERT INTO "item" VALUES(46,'6d61e570-5fe4-4473-b6ca-1af06c9ea2d6',NULL,NULL,NULL,24,'BP Monitor (Digital)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441595','2026-06-17 13:41:40.441595',0);
INSERT INTO "item" VALUES(47,'32421b75-2a83-4fbb-ac36-2e215598e285',NULL,NULL,NULL,24,'Thermometer (Infrared)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441596','2026-06-17 13:41:40.441597',0);
INSERT INTO "item" VALUES(48,'6133b0c9-19e2-458f-a9f5-b02313103d99',NULL,NULL,NULL,24,'Stethoscope',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441598','2026-06-17 13:41:40.441598',0);
INSERT INTO "item" VALUES(49,'d1b2367a-f56a-475a-9fd6-f3d8a3564664',NULL,NULL,NULL,24,'Glucometer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441600','2026-06-17 13:41:40.441600',0);
INSERT INTO "item" VALUES(50,'53923c11-85be-4667-ace0-4ec86bbe818a',NULL,NULL,NULL,22,'Suction Machine',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441601','2026-06-17 13:41:40.441602',0);
INSERT INTO "item" VALUES(51,'349dcfe9-43df-4c21-bb50-fde876c11240',NULL,NULL,NULL,22,'Bag Valve Mask (Adult)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441603','2026-06-17 13:41:40.441603',0);
INSERT INTO "item" VALUES(52,'0b593c54-e1eb-4e16-80ed-91d1f185b9ca',NULL,NULL,NULL,22,'Bag Valve Mask (Pediatric)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441604','2026-06-17 13:41:40.441605',0);
INSERT INTO "item" VALUES(53,'93dd60c6-e62d-4c20-a576-61f0bfe40dc7',NULL,NULL,NULL,22,'Laryngoscope Set',NULL,NULL,'Set',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441606','2026-06-17 13:41:40.441606',0);
INSERT INTO "item" VALUES(54,'010e29fe-fc6a-4d3d-9c3a-34afefaac4d8',NULL,NULL,NULL,25,'Stretcher (Ambulance)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441607','2026-06-17 13:41:40.441608',0);
INSERT INTO "item" VALUES(55,'75e486ea-083f-4122-82db-1f981b4a062b',NULL,NULL,NULL,25,'Wheelchair',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441609','2026-06-17 13:41:40.441609',0);
INSERT INTO "item" VALUES(56,'b978681f-3613-4d93-b5f0-93d18a44f72a',NULL,NULL,NULL,25,'Crutches (Pair)',NULL,NULL,'Pair',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441610','2026-06-17 13:41:40.441611',0);
INSERT INTO "item" VALUES(57,'94cecebb-ab60-4116-86b7-d6806c07ed3c',NULL,NULL,NULL,25,'Walking Frame',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441612','2026-06-17 13:41:40.441612',0);
INSERT INTO "item" VALUES(58,'c8a93b3c-2817-42b4-a632-568badae0d99',NULL,NULL,NULL,22,'IV Stand',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441613','2026-06-17 13:41:40.441614',0);
INSERT INTO "item" VALUES(59,'c910fb90-ba0e-4f3d-907b-c3231397b2bd',NULL,NULL,NULL,23,'First Aid Cabinet (Empty)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441615','2026-06-17 13:41:40.441615',0);
INSERT INTO "item" VALUES(60,'a2b4bb98-26da-44d7-87b2-97a65d8a2e7a',NULL,NULL,NULL,23,'Splint Set (SAM)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441617','2026-06-17 13:41:40.441617',0);
INSERT INTO "item" VALUES(61,'8b651b7c-8919-4b20-8182-6e39dd6add49',NULL,NULL,NULL,23,'Tourniquet (CAT)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441618','2026-06-17 13:41:40.441619',0);
INSERT INTO "item" VALUES(62,'4d6ee045-7dbe-477e-ab9f-9ebb8d488751',NULL,NULL,NULL,23,'Trauma Shears',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441620','2026-06-17 13:41:40.441620',0);
INSERT INTO "item" VALUES(63,'eed5a092-784f-4215-9281-7beaaf5b0629',NULL,NULL,NULL,23,'Medical Backpack (Empty)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441621','2026-06-17 13:41:40.441622',0);
INSERT INTO "item" VALUES(64,'029f1fc4-da7c-4f1f-86a3-2b888d151206',NULL,NULL,NULL,22,'CPR Pocket Mask',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441623','2026-06-17 13:41:40.441623',0);
INSERT INTO "item" VALUES(65,'9cba145e-8b54-4994-b25a-ea6550599850',NULL,NULL,NULL,22,'Portable Ventilator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441624','2026-06-17 13:41:40.441625',0);
INSERT INTO "item" VALUES(66,'53dda54c-d229-49c1-a87c-ef0ee34f1b01',NULL,NULL,NULL,22,'Defibrillator (AED)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441626','2026-06-17 13:41:40.441626',0);
INSERT INTO "item" VALUES(67,'936258c4-7df0-4ee7-9548-85d13a83f373',NULL,NULL,NULL,22,'Oxygen Tank (Large)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441628','2026-06-17 13:41:40.441628',0);
INSERT INTO "item" VALUES(68,'496c9260-b11a-4b61-bf43-b6341d30546f','','','',26,'4x4 Pickup (Double Cab)','','','Piece',0,0,0,0,0,0,0,'Normal','/uploads/item_e526418706bf47bdb95631d547024bef.png','Active',NULL,1,'2026-06-17 13:41:40.441629','2026-06-17 13:53:44.762681',0);
INSERT INTO "item" VALUES(69,'55b220de-8e2e-4ca3-96cc-5d86180b71a6',NULL,NULL,NULL,26,'SUV (4x4)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441631','2026-06-17 13:41:40.441631',0);
INSERT INTO "item" VALUES(70,'54c35c5b-778c-452f-bfe1-b6cd87db08fb',NULL,NULL,NULL,26,'Motorcycle (Dirt)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441632','2026-06-17 13:41:40.441633',0);
INSERT INTO "item" VALUES(71,'4a28f3cf-225d-4847-9a0b-98ece41f8aad',NULL,NULL,NULL,26,'Ambulance (4x4)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441634','2026-06-17 13:41:40.441634',0);
INSERT INTO "item" VALUES(72,'56a5dc98-6764-4934-ba89-4063dea4a78c',NULL,NULL,NULL,27,'Cargo Truck (6-Ton)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441635','2026-06-17 13:41:40.441638',0);
INSERT INTO "item" VALUES(74,'43d422d3-3678-41f9-a274-ab9dd37b13a9',NULL,NULL,NULL,27,'Dump Truck',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441641','2026-06-17 13:41:40.441641',0);
INSERT INTO "item" VALUES(75,'c9b66599-1724-4efd-8925-e4c198ee8f46',NULL,NULL,NULL,27,'Water Tanker Truck',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441642','2026-06-17 13:41:40.441643',0);
INSERT INTO "item" VALUES(76,'8a62564e-bbec-4082-8f6a-7325f3ba47bb',NULL,NULL,NULL,27,'Fuel Tanker',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441644','2026-06-17 13:41:40.441644',0);
INSERT INTO "item" VALUES(77,'ac575cf3-b487-442e-8b7d-59afe2553ec6',NULL,NULL,NULL,27,'Bulldozer',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441645','2026-06-17 13:41:40.441646',0);
INSERT INTO "item" VALUES(78,'c624c6ee-ee29-4f26-adb3-0323e6d1f25c',NULL,NULL,NULL,27,'Excavator',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441647','2026-06-17 13:41:40.441648',0);
INSERT INTO "item" VALUES(79,'3192778a-7280-447a-8247-7d89c0ba3625',NULL,NULL,NULL,27,'Forklift',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441649','2026-06-17 13:41:40.441649',0);
INSERT INTO "item" VALUES(80,'2208265d-e3e7-4013-8be7-fb97f1e08388',NULL,NULL,NULL,27,'Backhoe Loader',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441650','2026-06-17 13:41:40.441651',0);
INSERT INTO "item" VALUES(81,'f67a6561-4ad0-42b8-93d0-0ba862bfa3a6',NULL,NULL,NULL,28,'Outboard Motor (Boat)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441652','2026-06-17 13:41:40.441652',0);
INSERT INTO "item" VALUES(82,'ef7d9c60-f84b-4426-b2a4-6d0c10f4f660',NULL,NULL,NULL,28,'Rescue Boat (Inflatable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441653','2026-06-17 13:41:40.441654',0);
INSERT INTO "item" VALUES(83,'6e7ecbe4-b460-4d52-a1bf-c69a45351b60',NULL,NULL,NULL,28,'Drone (Search)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441655','2026-06-17 13:41:40.441656',0);
INSERT INTO "item" VALUES(84,'eb0bfaab-ad36-4df4-b22b-0bf2ececa402',NULL,NULL,NULL,29,'Tire (Vehicle)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441657','2026-06-17 13:41:40.441657',0);
INSERT INTO "item" VALUES(85,'896ff4b6-db5c-404f-83c4-bf2ae896abf1',NULL,NULL,NULL,29,'Jump Starter Pack',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441658','2026-06-17 13:41:40.441659',0);
INSERT INTO "item" VALUES(86,'44131626-5e83-481e-8063-8f5af16ed2cb',NULL,NULL,NULL,29,'Tow Cable',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441660','2026-06-17 13:41:40.441660',0);
INSERT INTO "item" VALUES(87,'989c5be2-a849-43d1-9ec6-e1d0be71bc70',NULL,NULL,NULL,29,'Hydraulic Jack',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441661','2026-06-17 13:41:40.441662',0);
INSERT INTO "item" VALUES(88,'2bea983e-e782-4757-b7dc-a15d762b8e4a',NULL,NULL,NULL,29,'Tool Kit (Vehicle)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441663','2026-06-17 13:41:40.441663',0);
INSERT INTO "item" VALUES(89,'53db93cd-9a31-490e-ab18-5e9a4bf4b3b6',NULL,NULL,NULL,29,'Fire Extinguisher (Vehicle)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441664','2026-06-17 13:41:40.441665',0);
INSERT INTO "item" VALUES(90,'9ca566df-574e-4003-9a64-c93bde681706',NULL,NULL,NULL,26,'Fuel Can (20L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Hazardous',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441666','2026-06-17 13:41:40.441667',0);
INSERT INTO "item" VALUES(91,'9d713540-633b-437d-87f5-d6cfd0462ebb',NULL,NULL,NULL,29,'Warning Triangle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441668','2026-06-17 13:41:40.441668',0);
INSERT INTO "item" VALUES(92,'649c8b7a-d5ff-4d79-92e3-d3e8275da982',NULL,NULL,NULL,29,'Safety Vest (Reflective)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441669','2026-06-17 13:41:40.441670',0);
INSERT INTO "item" VALUES(93,'b816fec8-8109-4fb0-96e7-4a74ad2656c7',NULL,NULL,NULL,30,'Satellite Phone',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441671','2026-06-17 13:41:40.441671',0);
INSERT INTO "item" VALUES(94,'5c9c1c44-3a9d-4a72-8ac7-773b3bacafe7',NULL,NULL,NULL,30,'Handheld Radio (VHF)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441672','2026-06-17 13:41:40.441673',0);
INSERT INTO "item" VALUES(95,'0d3e4ee0-feb8-4745-950c-bb2e3c62d4c8',NULL,NULL,NULL,30,'Handheld Radio (UHF)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441674','2026-06-17 13:41:40.441674',0);
INSERT INTO "item" VALUES(96,'25822874-fea1-4e5c-8037-ce36d06cc86e',NULL,NULL,NULL,30,'Base Station Radio',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441675','2026-06-17 13:41:40.441676',0);
INSERT INTO "item" VALUES(97,'e9bbe4b6-0d02-4922-833b-fc1839d6b4c0',NULL,NULL,NULL,30,'Megaphone (Battery)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441677','2026-06-17 13:41:40.441677',0);
INSERT INTO "item" VALUES(98,'02a791de-d469-4cac-971e-e2238ed695e5',NULL,NULL,NULL,31,'Generator (2kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441679','2026-06-17 13:41:40.441679',0);
INSERT INTO "item" VALUES(99,'7b85a165-59d8-4103-a1c0-fdde1f16f3b0',NULL,NULL,NULL,31,'Generator (5kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441680','2026-06-17 13:41:40.441681',0);
INSERT INTO "item" VALUES(100,'d94669be-7111-42c1-9cc5-29b43fd37657',NULL,NULL,NULL,31,'Generator (10kW)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441682','2026-06-17 13:41:40.441682',0);
INSERT INTO "item" VALUES(101,'c1edae90-06ff-4056-8bfc-376052dd51b1',NULL,NULL,NULL,31,'Solar Panel (Portable 100W)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441683','2026-06-17 13:41:40.441684',0);
INSERT INTO "item" VALUES(102,'2ae6f097-b348-4ab6-840a-5f5dd626adb8',NULL,NULL,NULL,31,'Solar Panel (Portable 300W)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441685','2026-06-17 13:41:40.441685',0);
INSERT INTO "item" VALUES(103,'02fa4f68-2f1f-4b24-bbb2-cc59e7f6238c',NULL,NULL,NULL,31,'Power Station (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441687','2026-06-17 13:41:40.441687',0);
INSERT INTO "item" VALUES(104,'eadf52af-1b5c-449c-86f9-00b431c32a46',NULL,NULL,NULL,31,'LED Flood Light',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441689','2026-06-17 13:41:40.441690',0);
INSERT INTO "item" VALUES(105,'4169bfae-3cc4-4020-9801-389c42fbcc41',NULL,NULL,NULL,31,'Extension Cable (50m)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441692','2026-06-17 13:41:40.441693',0);
INSERT INTO "item" VALUES(106,'137d020d-bbf8-454f-abdd-ea5972177449',NULL,NULL,NULL,31,'Power Distribution Box',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441695','2026-06-17 13:41:40.441696',0);
INSERT INTO "item" VALUES(107,'8e195c9f-20f2-4dec-acae-7107ca138abc',NULL,NULL,NULL,32,'Camp Tent (10 Person)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441698','2026-06-17 13:41:40.441699',0);
INSERT INTO "item" VALUES(108,'466a86fc-fea1-4fb9-b219-ddfcda7288d8',NULL,NULL,NULL,32,'Camp Tent (20 Person)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441701','2026-06-17 13:41:40.441702',0);
INSERT INTO "item" VALUES(109,'3427ce32-44c8-4d82-9f09-dc1d2d4eb58b',NULL,NULL,NULL,32,'Cot (Folding)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441704','2026-06-17 13:41:40.441705',0);
INSERT INTO "item" VALUES(110,'82281e70-d091-4306-ba2f-3152d6d2e3f6',NULL,NULL,NULL,32,'Sleeping Bag',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441707','2026-06-17 13:41:40.441708',0);
INSERT INTO "item" VALUES(111,'17fe5a90-1c2f-4d61-a8d8-9822e557fdab',NULL,NULL,NULL,32,'Camp Table',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441711','2026-06-17 13:41:40.441711',0);
INSERT INTO "item" VALUES(112,'2b658ece-553d-4267-9876-ef62428c80e3',NULL,NULL,NULL,32,'Camp Chair',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441713','2026-06-17 13:41:40.441713',0);
INSERT INTO "item" VALUES(113,'b8247cd4-aee6-4da7-95a1-6dd27ff6b520',NULL,NULL,NULL,33,'Water Bladder (1000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441714','2026-06-17 13:41:40.441715',0);
INSERT INTO "item" VALUES(114,'26321603-ab4d-4c4c-b3e0-61b4e9892d1d',NULL,NULL,NULL,33,'Water Bladder (2000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441716','2026-06-17 13:41:40.441716',0);
INSERT INTO "item" VALUES(115,'a50824f5-2e20-4aba-a23a-0d917ef519b5',NULL,NULL,NULL,33,'Water Treatment Unit (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441719','2026-06-17 13:41:40.441720',0);
INSERT INTO "item" VALUES(116,'dd0c8531-bbca-45df-97cd-63d3d8135d65',NULL,NULL,NULL,33,'Water Pump (Submersible)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441721','2026-06-17 13:41:40.441722',0);
INSERT INTO "item" VALUES(117,'423995e5-85b3-45f8-900e-825fdfe5eb70',NULL,NULL,NULL,33,'Water Tank (Plastic 500L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441724','2026-06-17 13:41:40.441725',0);
INSERT INTO "item" VALUES(118,'25d41295-5fcc-44d8-8f98-6e21b6e98bdb',NULL,NULL,NULL,33,'Water Tank (Plastic 1000L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441727','2026-06-17 13:41:40.441728',0);
INSERT INTO "item" VALUES(119,'36b517d9-2dd1-4f07-9c61-30df635f1739',NULL,NULL,NULL,33,'Collapsible Jerry Can (10L)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441730','2026-06-17 13:41:40.441731',0);
INSERT INTO "item" VALUES(120,'0032ec74-28e2-4a7e-8c66-285070132071',NULL,NULL,NULL,33,'Portable Toilet',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441733','2026-06-17 13:41:40.441734',0);
INSERT INTO "item" VALUES(121,'c0264db4-e2e6-4f62-bf42-099e4cb4fce7',NULL,NULL,NULL,33,'Shower Unit (Portable)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441736','2026-06-17 13:41:40.441737',0);
INSERT INTO "item" VALUES(122,'4fcd90a5-dadb-44ea-80a4-005ac23fe20f',NULL,NULL,NULL,34,'Fire Extinguisher (ABC 6kg)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441739','2026-06-17 13:41:40.441739',0);
INSERT INTO "item" VALUES(123,'5ad0f50d-feed-4681-97aa-64b83515113a',NULL,NULL,NULL,34,'Fire Extinguisher (CO2)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441740','2026-06-17 13:41:40.441742',0);
INSERT INTO "item" VALUES(124,'3828ae6d-6111-42a5-9c20-a35a6e2a8d2c',NULL,NULL,NULL,34,'Fire Hose (15m)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441744','2026-06-17 13:41:40.441745',0);
INSERT INTO "item" VALUES(125,'583f8b6e-fce6-4469-b441-aabca812c8d2',NULL,NULL,NULL,34,'Fire Nozzle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441747','2026-06-17 13:41:40.441748',0);
INSERT INTO "item" VALUES(126,'94827d0d-4544-4a65-b4b0-10cfb2f922c6',NULL,NULL,NULL,34,'Fire Blanket',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441750','2026-06-17 13:41:40.441751',0);
INSERT INTO "item" VALUES(127,'00d97880-b631-4801-89c8-47a17ed76a45',NULL,NULL,NULL,34,'Smoke Detector',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441754','2026-06-17 13:41:40.441755',0);
INSERT INTO "item" VALUES(128,'4c2233fe-8531-416c-845e-ac0713d98999',NULL,NULL,NULL,32,'First Aid Kit (Workplace)',NULL,NULL,'Set',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441756','2026-06-17 13:41:40.441757',0);
INSERT INTO "item" VALUES(129,'a7e49cc5-fc65-4370-bfd5-0c48c5260248',NULL,NULL,NULL,32,'Emergency Whistle',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441758','2026-06-17 13:41:40.441759',0);
INSERT INTO "item" VALUES(130,'35561f9f-90e3-4e47-a248-83cf71d128aa',NULL,NULL,NULL,32,'Dust Mask (N95)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441761','2026-06-17 13:41:40.441762',0);
INSERT INTO "item" VALUES(131,'7f2b2532-f867-4d3f-aba6-a67f48ef5cb6',NULL,NULL,NULL,32,'Safety Goggles',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441764','2026-06-17 13:41:40.441765',0);
INSERT INTO "item" VALUES(132,'82ed106f-1b42-4aee-a4e6-7396768a917a',NULL,NULL,NULL,32,'Rain Poncho',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-17 13:41:40.441767','2026-06-17 13:41:40.441768',0);
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
INSERT INTO "relief_request" VALUES(4,'REQ-5414','2026-06-17',3,'','Rajesh Hamal','986523100','High',5000.0,5000.0,'Medical Support','','Completed','2026-06-17 01:00:59.052192');
INSERT INTO "relief_request" VALUES(6,'REQ-0545','2026-06-18',7,'','मनमोहन अधिकारी','','Low',10000.0,3500.0,'Livelihood Support','','Completed','2026-06-18 01:20:59.001426');
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
INSERT INTO "relief_request_item" VALUES(8,4,2,1,1,'Piece');
INSERT INTO "relief_request_item" VALUES(9,4,3,1,1,'Packet');
INSERT INTO "relief_request_item" VALUES(10,4,1,5,5,'');
INSERT INTO "relief_request_item" VALUES(12,6,1,25,0,'Kg');
INSERT INTO "relief_request_item" VALUES(13,6,2,5,0,'Piece');
INSERT INTO "relief_request_item" VALUES(14,6,3,5,0,'Packet');
CREATE TABLE stock_receipt (
	id INTEGER NOT NULL, 
	receipt_no VARCHAR(50) NOT NULL, 
	date DATE NOT NULL, 
	warehouse_id INTEGER NOT NULL, 
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
	created_at DATETIME, supplier_id INTEGER REFERENCES supplier(id), 
	PRIMARY KEY (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouse (id)
);
INSERT INTO "stock_receipt" VALUES(1,'RCPT-0001','2026-06-10',1,'Government',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2026-06-10 10:50:01.277791',NULL);
INSERT INTO "stock_receipt" VALUES(2,'RCPT-865767','2026-06-10',1,'Local Government','','Bharat Sir','9852103366','','','12','230',NULL,'','',NULL,'Hakim Saab','',1,'2026-06-10 12:02:42.159837',NULL);
INSERT INTO "stock_receipt" VALUES(3,'RCPT-910134','2026-06-17',1,'Purchase','Thalara RM','Prakash Bhandari','9865654665','rosyprakash786@gmail.com','New Baneshwor, Kathmandu
Baneshwor','124','230','2026-06-17','Delivered','',NULL,'Naresh Parki','',1,'2026-06-17 00:10:12.967730',NULL);
INSERT INTO "stock_receipt" VALUES(4,'RCPT-436836','2026-06-17',1,'Purchase','','','','','','','',NULL,'','',NULL,'','',1,'2026-06-17 13:54:35.390150',NULL);
INSERT INTO "stock_receipt" VALUES(5,'RCPT-865189','2026-06-17',1,'Local Government','','','','','','','',NULL,'','',NULL,'','',1,'2026-06-17 14:01:34.554962',NULL);
INSERT INTO "stock_receipt" VALUES(6,'TEST-14031ff7','2026-06-17',1,'Supplier','PIN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2026-06-17 14:20:07.372812',NULL);
INSERT INTO "stock_receipt" VALUES(7,'RCPT-0007','2026-06-17',1,'Supplier','PIN','Pankaj Sit','','','',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2026-06-17 14:20:17.489396',NULL);
INSERT INTO "stock_receipt" VALUES(8,'RCPT-150237','2026-06-17',1,'Local Government','Thalara RM','Bharat Rokaya','1111','rokayabharat@gmail.com','Kholi','','',NULL,'','',NULL,'','',1,'2026-06-17 14:23:27.140251',NULL);
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
INSERT INTO "stock_receipt_item" VALUES(1,1,1,1000,NULL,NULL,NULL,NULL,NULL,0.0,0.0);
INSERT INTO "stock_receipt_item" VALUES(2,2,1,250,'Kg','','',NULL,NULL,3500.0,875000.0);
INSERT INTO "stock_receipt_item" VALUES(3,2,2,75,'Piece','','',NULL,NULL,1200.0,90000.0);
INSERT INTO "stock_receipt_item" VALUES(4,3,3,200,'Packet','#12K','112233','2025-06-17','2026-06-30',50.0,10000.0);
INSERT INTO "stock_receipt_item" VALUES(5,4,98,1,'Piece','','',NULL,NULL,0.0,0.0);
INSERT INTO "stock_receipt_item" VALUES(6,5,15,10,'Piece','','',NULL,NULL,2000.0,20000.0);
INSERT INTO "stock_receipt_item" VALUES(7,7,1,3,NULL,NULL,NULL,NULL,NULL,0.0,0.0);
INSERT INTO "stock_receipt_item" VALUES(8,8,4,10,'Meter','','',NULL,NULL,0.0,0.0);
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
INSERT INTO "user" VALUES(1,'admin','scrypt:32768:8:1$rMz5lLZLEZL15lFS$385dc9b0b4ed5faac8467ec75561309c23d613b6b7dcdd64427d608386c4f49db5813c26c38f73ff2b9f6b205b3f9de7e6b63aa9f876c64b1ecccceee2a5123d','admin','System Administrator',1,'2026-06-10 10:49:53','2026-06-18 14:42:06.725214+00:00');
INSERT INTO "user" VALUES(2,'manager','scrypt:32768:8:1$z0oO4x3fz623Llfz$c21d2fab1e0ed429b2b18ac9f532c6d08a9dd7617664706b8bf9df105cb016f49974a8fd0494889ee9d61e4082e83c800c8630810452e95c348350edad20608c','manager','Warehouse Manager',1,'2026-06-10 10:49:53',NULL);
INSERT INTO "user" VALUES(3,'dataentry','scrypt:32768:8:1$rH54pi0U0poWTNQM$bcf0d9ed07678c75d28fdd0652a3b8c671849d3e743c51a44071e67080c3b0cc929a29aa549e5aeb7cdfe5927785fd6da596d7640d612a7f7fd52bd8f53769ff','dataentry','Data Entry Operator',1,'2026-06-10 10:49:53',NULL);
INSERT INTO "user" VALUES(4,'viewer','scrypt:32768:8:1$iqgLtuwCuAJdVzjt$fcb84877f9ef1712360eed3208c2cc22c424b53cff81eb50cff77b1def374a794808c03b81f94d0e687e5f5921963d125f4693127e3ec486175e4ec7e78ca4ca','viewer','Read Only User',1,'2026-06-10 10:49:53',NULL);
CREATE TABLE ward (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	sort_order INTEGER, 
	PRIMARY KEY (id)
);
INSERT INTO "ward" VALUES(1,'ward 1',1);
INSERT INTO "ward" VALUES(2,'ward 2',2);
INSERT INTO "ward" VALUES(3,'ward 3',3);
INSERT INTO "ward" VALUES(4,'ward 4',4);
INSERT INTO "ward" VALUES(5,'ward 5',5);
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
INSERT INTO "warehouse" VALUES(1,'Main WH','WH-01','Thalara','Prakash','',1000.0,'','2026-06-10 10:50:01.234321','2026-06-10 16:30:30.626553');
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
CREATE UNIQUE INDEX ix_category_name ON category (name);
CREATE INDEX ix_incident_status ON incident (status);
CREATE INDEX ix_incident_incident_type ON incident (incident_type);
CREATE UNIQUE INDEX ix_daily_report_log_report_date_bs ON daily_report_log (report_date_bs);
CREATE UNIQUE INDEX ix_cash_fund_fund_no ON cash_fund (fund_no);
CREATE INDEX ix_beneficiary_name ON beneficiary (name);
CREATE INDEX ix_item_name ON item (name);
CREATE UNIQUE INDEX ix_item_uuid ON item (uuid);
CREATE UNIQUE INDEX ix_item_item_code ON item (item_code);
CREATE INDEX ix_item_category_id ON item (category_id);
CREATE INDEX ix_stock_receipt_warehouse_id ON stock_receipt (warehouse_id);
CREATE UNIQUE INDEX ix_stock_receipt_receipt_no ON stock_receipt (receipt_no);
CREATE INDEX ix_relief_request_priority ON relief_request (priority);
CREATE INDEX ix_relief_request_incident_id ON relief_request (incident_id);
CREATE INDEX ix_relief_request_status ON relief_request (status);
CREATE UNIQUE INDEX ix_relief_request_request_number ON relief_request (request_number);
CREATE INDEX ix_disaster_assessment_incident_id ON disaster_assessment (incident_id);
CREATE INDEX ix_disaster_assessment_fiscal_year ON disaster_assessment (fiscal_year);
CREATE INDEX ix_disaster_assessment_disaster_type ON disaster_assessment (disaster_type);
CREATE INDEX ix_disaster_assessment_disaster_date_bs ON disaster_assessment (disaster_date_bs);
CREATE UNIQUE INDEX ix_cash_receipt_receipt_no ON cash_receipt (receipt_no);
CREATE INDEX ix_cash_receipt_fund_id ON cash_receipt (fund_id);
CREATE INDEX ix_cash_request_incident_id ON cash_request (incident_id);
CREATE UNIQUE INDEX ix_cash_request_request_number ON cash_request (request_number);
CREATE INDEX ix_stock_receipt_item_receipt_id ON stock_receipt_item (receipt_id);
CREATE INDEX ix_stock_receipt_attachment_receipt_id ON stock_receipt_attachment (receipt_id);
CREATE UNIQUE INDEX ix_manual_adjustment_adjustment_no ON manual_adjustment (adjustment_no);
CREATE INDEX ix_manual_adjustment_warehouse_id ON manual_adjustment (warehouse_id);
CREATE INDEX ix_inventory_item_id ON inventory (item_id);
CREATE INDEX ix_inventory_warehouse_id ON inventory (warehouse_id);
CREATE INDEX ix_relief_request_item_request_id ON relief_request_item (request_id);
CREATE INDEX ix_dispatch_relief_request_id ON dispatch (relief_request_id);
CREATE UNIQUE INDEX ix_dispatch_dispatch_number ON dispatch (dispatch_number);
CREATE INDEX ix_dispatch_incident_id ON dispatch (incident_id);
CREATE INDEX ix_dispatch_warehouse_id ON dispatch (warehouse_id);
CREATE INDEX ix_cash_distribution_fund_id ON cash_distribution (fund_id);
CREATE INDEX ix_cash_distribution_relief_request_id ON cash_distribution (relief_request_id);
CREATE INDEX ix_cash_distribution_cash_request_id ON cash_distribution (cash_request_id);
CREATE UNIQUE INDEX ix_cash_distribution_distribution_no ON cash_distribution (distribution_no);
CREATE INDEX ix_cash_distribution_incident_id ON cash_distribution (incident_id);
CREATE INDEX ix_dispatch_item_dispatch_id ON dispatch_item (dispatch_id);
CREATE INDEX ix_distribution_incident_id ON distribution (incident_id);
CREATE INDEX ix_distribution_dispatch_id ON distribution (dispatch_id);
CREATE UNIQUE INDEX ix_distribution_distribution_no ON distribution (distribution_no);
CREATE INDEX ix_cash_distribution_beneficiary_beneficiary_id ON cash_distribution_beneficiary (beneficiary_id);
CREATE INDEX ix_cash_distribution_beneficiary_distribution_id ON cash_distribution_beneficiary (distribution_id);
CREATE INDEX ix_distribution_beneficiary_distribution_id ON distribution_beneficiary (distribution_id);
CREATE INDEX ix_supplier_name ON supplier (name);
CREATE INDEX ix_warehouse_zone_warehouse_id ON warehouse_zone (warehouse_id);
CREATE INDEX ix_stock_transfer_from_warehouse_id ON stock_transfer (from_warehouse_id);
CREATE INDEX ix_stock_transfer_to_warehouse_id ON stock_transfer (to_warehouse_id);
CREATE UNIQUE INDEX ix_stock_transfer_transfer_no ON stock_transfer (transfer_no);
CREATE INDEX ix_stock_transfer_item_transfer_id ON stock_transfer_item (transfer_id);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('user',4);
COMMIT;
