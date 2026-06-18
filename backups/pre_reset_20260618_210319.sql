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
INSERT INTO "app_settings" VALUES(13,'office_name','थलारा गाउँपालिका','2026-06-18 15:17:12.433857','2026-06-18 15:17:12.433862');
INSERT INTO "app_settings" VALUES(14,'default_language','Nepali','2026-06-18 15:17:12.437739','2026-06-18 15:17:12.437741');
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
CREATE TABLE daily_report_log (
	id INTEGER NOT NULL, 
	report_date_bs VARCHAR(10) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
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
	updated_at DATETIME, weather_status VARCHAR(100), 
	PRIMARY KEY (id)
);
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
INSERT INTO "item" VALUES(36,'1cf40c8c-08b4-4bf4-aafb-287ab725af75',NULL,NULL,NULL,15,'Prusik Loop',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Dry Storage',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036686','2026-06-18 14:48:34.036686');
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
INSERT INTO "item" VALUES(65,'24fd82e3-d7e5-4edf-8b95-96f6b9bca6df',NULL,NULL,NULL,25,'4x4 Pickup (Double Cab)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036712','2026-06-18 14:48:34.036713');
INSERT INTO "item" VALUES(66,'9c44726e-812d-4aa7-aea8-dc1075c12a69',NULL,NULL,NULL,25,'SUV (4x4)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036713','2026-06-18 14:48:34.036714');
INSERT INTO "item" VALUES(67,'40d2fafc-efa6-48a3-bd52-d44714de3415',NULL,NULL,NULL,25,'Motorcycle (Dirt)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036714','2026-06-18 14:48:34.036714');
INSERT INTO "item" VALUES(68,'ceb7a9a1-518f-42ce-ba42-33401aa6f0b4',NULL,NULL,NULL,25,'Ambulance (4x4)',NULL,NULL,'Piece',0,0,NULL,0,0,0,0,0,'Normal',NULL,'Active',NULL,NULL,'2026-06-18 14:48:34.036715','2026-06-18 14:48:34.036716');
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
INSERT INTO "user" VALUES(1,'admin','scrypt:32768:8:1$k2COQgO3yfRx8BQg$8a5c1bac376ee6f0072ceb442c1d4977ac1015cea64f807bb6ba764af6ab64a7aebe69823e9c39dc4be493da3bd2d08267805abb7ed629316c9c5b2de8953e0a','admin','System Administrator',1,'2026-06-18 14:48:34',NULL);
INSERT INTO "user" VALUES(2,'editor','scrypt:32768:8:1$hynLA0mcsu8D5kPk$712ddee14ef8818957809fb38f30fdb10c12cd99a06880a09289aacdb8ebcfd3bcfa949874072395ea01105427ff56588f798711767fac3e963b29f5535f938e','editor','Data Editor',1,'2026-06-18 14:48:34',NULL);
INSERT INTO "user" VALUES(3,'viewer','scrypt:32768:8:1$7hQSQyYmbn9YKOFI$37499c3b9d25af0379fa361416c879e5f00ff363d23cd5a6fc041debc2b3f9f509bb5bbb7c8f8e2072c4b16e4d70439966e17ee19bf5fa3c3d22263e28017d47','viewer','Read Only User',1,'2026-06-18 14:48:34',NULL);
INSERT INTO "user" VALUES(4,'operator','scrypt:32768:8:1$RyqQpHSR3rk8tthg$225d5e6230b42e979ab46a67a9326b1009de4befe51ddd6f8d059ab0f92f2bc3f6d48da6bb73417af67872d9bc000b97b6b4cb617e5664d46d25de8fa105f71a','operator','Operations Officer',1,'2026-06-18 14:48:34',NULL);
INSERT INTO "user" VALUES(5,'finance','scrypt:32768:8:1$jGVYGN6ZWYtvvElG$e96bc8a4b2adf810e6c33ff36eff00333eecedf6d0c68b0fc1d33796129a2225de6889f9a93c8ae01b9ea8905b6ecbc4c2e0d612ba9c90c1577592de8debd04b','finance','Finance Officer',1,'2026-06-18 14:48:34',NULL);
CREATE TABLE ward (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	sort_order INTEGER, 
	PRIMARY KEY (id)
);
INSERT INTO "ward" VALUES(1,'Ward 1',1);
INSERT INTO "ward" VALUES(2,'Ward 2',2);
INSERT INTO "ward" VALUES(3,'Ward 3',3);
INSERT INTO "ward" VALUES(4,'Ward 4',4);
INSERT INTO "ward" VALUES(5,'Ward 5',5);
INSERT INTO "ward" VALUES(6,'Ward 6',6);
INSERT INTO "ward" VALUES(7,'Ward 7',7);
INSERT INTO "ward" VALUES(8,'Ward 8',8);
INSERT INTO "ward" VALUES(9,'Ward 9',9);
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
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('user',5);
COMMIT;
