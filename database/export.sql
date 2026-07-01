-- ============================================================
-- 金三角网吧管理系统 - 数据库导出
-- 导出时间: 2026-07-02 02:20:34
-- ============================================================

-- 1. 创建数据库
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'GoldenTriangleCafe')
    CREATE DATABASE GoldenTriangleCafe;
GO

USE GoldenTriangleCafe;
GO

-- 2. 清理旧表
IF OBJECT_ID('ZONE', 'U') IS NOT NULL DROP TABLE ZONE;
IF OBJECT_ID('COMPUTER', 'U') IS NOT NULL DROP TABLE COMPUTER;
IF OBJECT_ID('MEMBER', 'U') IS NOT NULL DROP TABLE MEMBER;
IF OBJECT_ID('RECHARGE_RECORD', 'U') IS NOT NULL DROP TABLE RECHARGE_RECORD;
IF OBJECT_ID('ONLINE_RECORD', 'U') IS NOT NULL DROP TABLE ONLINE_RECORD;
IF OBJECT_ID('PRODUCT', 'U') IS NOT NULL DROP TABLE PRODUCT;
IF OBJECT_ID('PRODUCT_ORDER', 'U') IS NOT NULL DROP TABLE PRODUCT_ORDER;
IF OBJECT_ID('ORDER_DETAIL', 'U') IS NOT NULL DROP TABLE ORDER_DETAIL;
IF OBJECT_ID('EQUIPMENT_RENTAL', 'U') IS NOT NULL DROP TABLE EQUIPMENT_RENTAL;
IF OBJECT_ID('SYSTEM_CONFIG', 'U') IS NOT NULL DROP TABLE SYSTEM_CONFIG;
IF OBJECT_ID('OPERATOR', 'U') IS NOT NULL DROP TABLE OPERATOR;
GO

-- 3. 创建表
CREATE TABLE COMPUTER (
    Computer_ID INT NOT NULL,
    Zone_ID INT NOT NULL,
    Computer_No NVARCHAR(20) NOT NULL,
    Room_No NVARCHAR(10) NULL,
    Status NVARCHAR(10) NOT NULL DEFAULT (N'free'),
    CONSTRAINT PK_COMPUTER PRIMARY KEY (Computer_ID),
    CONSTRAINT FK_Computer_Zone FOREIGN KEY (Zone_ID) REFERENCES ZONE(Zone_ID),
    CONSTRAINT CK_Computer_Status CHECK (([Status]=N'fault' OR [Status]=N'using' OR [Status]=N'free'))
);
GO

CREATE TABLE EQUIPMENT_RENTAL (
    Rental_ID INT NOT NULL,
    Member_ID INT NOT NULL,
    Equipment_Name NVARCHAR(50) NOT NULL,
    Rental_Fee_Per_Day DECIMAL(10,2) NOT NULL,
    Start_Time DATETIME NOT NULL DEFAULT GETDATE(),
    End_Time DATETIME NULL,
    Total_Fee DECIMAL(10,2) NULL,
    Status NVARCHAR(10) NOT NULL DEFAULT (N'active'),
    CONSTRAINT PK_EQUIPMENT_RENTAL PRIMARY KEY (Rental_ID),
    CONSTRAINT FK_Rental_Member FOREIGN KEY (Member_ID) REFERENCES MEMBER(Member_ID),
    CONSTRAINT CK_Rental_FeePerDay CHECK (([Rental_Fee_Per_Day]>(0))),
    CONSTRAINT CK_Rental_TotalFee CHECK (([Total_Fee] IS NULL OR [Total_Fee]>=(0))),
    CONSTRAINT CK_Rental_Status CHECK (([Status]=N'returned' OR [Status]=N'active'))
);
GO

CREATE TABLE MEMBER (
    Member_ID INT NOT NULL,
    Phone VARCHAR(11) NOT NULL,
    Name NVARCHAR(20) NOT NULL,
    Password_Hash VARCHAR(128) NOT NULL,
    Balance DECIMAL(10,2) NOT NULL DEFAULT ((0)),
    Total_Recharged DECIMAL(10,2) NOT NULL DEFAULT ((0)),
    Points INT NOT NULL DEFAULT ((0)),
    Is_Active BIT NOT NULL DEFAULT ((1)),
    Created_At DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_MEMBER PRIMARY KEY (Member_ID),
    CONSTRAINT CK_Member_Balance CHECK (([Balance]>=(0))),
    CONSTRAINT CK_Member_Recharged CHECK (([Total_Recharged]>=(0))),
    CONSTRAINT CK_Member_Points CHECK (([Points]>=(0)))
);
GO

CREATE TABLE ONLINE_RECORD (
    Record_ID INT NOT NULL,
    Computer_ID INT NOT NULL,
    Member_ID INT NULL,
    Start_Time DATETIME NOT NULL,
    End_Time DATETIME NULL,
    Billing_Mode NVARCHAR(20) NOT NULL DEFAULT (N'hourly'),
    Actual_Amount DECIMAL(10,2) NULL,
    Amount_Detail NVARCHAR(500) NULL,
    Status NVARCHAR(10) NOT NULL DEFAULT (N'active'),
    Is_Guest BIT NOT NULL DEFAULT ((0)),
    Guest_Phone VARCHAR(11) NULL,
    CONSTRAINT PK_ONLINE_RECORD PRIMARY KEY (Record_ID),
    CONSTRAINT FK_Online_Computer FOREIGN KEY (Computer_ID) REFERENCES COMPUTER(Computer_ID),
    CONSTRAINT FK_Online_Member FOREIGN KEY (Member_ID) REFERENCES MEMBER(Member_ID),
    CONSTRAINT CK_Online_BillingMode CHECK (([Billing_Mode]=N'overnight' OR [Billing_Mode]=N'hourly')),
    CONSTRAINT CK_Online_Status CHECK (([Status]=N'cancelled' OR [Status]=N'completed' OR [Status]=N'active')),
    CONSTRAINT CK_Online_Amount CHECK (([Actual_Amount] IS NULL OR [Actual_Amount]>=(0)))
);
GO

CREATE TABLE OPERATOR (
    Operator_ID INT NOT NULL,
    Login_Name VARCHAR(50) NOT NULL,
    Password_Hash VARCHAR(128) NOT NULL,
    Name NVARCHAR(20) NOT NULL,
    Role NVARCHAR(20) NOT NULL DEFAULT ('cashier'),
    Created_At DATETIME NULL DEFAULT GETDATE(),
    CONSTRAINT PK_OPERATOR PRIMARY KEY (Operator_ID),
    CONSTRAINT CK_Operator_Role CHECK (([Role]='cashier' OR [Role]='super_admin'))
);
GO

CREATE TABLE ORDER_DETAIL (
    Detail_ID INT NOT NULL,
    Order_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Quantity INT NOT NULL,
    Unit_Price DECIMAL(10,2) NOT NULL,
    CONSTRAINT PK_ORDER_DETAIL PRIMARY KEY (Detail_ID),
    CONSTRAINT FK_Detail_Product FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID),
    CONSTRAINT FK_Detail_Order FOREIGN KEY (Order_ID) REFERENCES PRODUCT_ORDER(Order_ID),
    CONSTRAINT CK_Detail_Quantity CHECK (([Quantity]>(0))),
    CONSTRAINT CK_Detail_UnitPrice CHECK (([Unit_Price]>(0)))
);
GO

CREATE TABLE PRODUCT (
    Product_ID INT NOT NULL,
    Name NVARCHAR(50) NOT NULL,
    Category NVARCHAR(20) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    Stock INT NOT NULL DEFAULT ((0)),
    Unit NVARCHAR(10) NOT NULL DEFAULT (N'个'),
    Is_Available BIT NOT NULL DEFAULT ((1)),
    CONSTRAINT PK_PRODUCT PRIMARY KEY (Product_ID),
    CONSTRAINT CK_Product_Price CHECK (([Price]>(0))),
    CONSTRAINT CK_Product_Stock CHECK (([Stock]>=(0)))
);
GO

CREATE TABLE PRODUCT_ORDER (
    Order_ID INT NOT NULL,
    Member_ID INT NOT NULL,
    Total_Amount DECIMAL(10,2) NOT NULL DEFAULT ((0)),
    Order_Time DATETIME NOT NULL DEFAULT GETDATE(),
    Operator NVARCHAR(20) NULL,
    CONSTRAINT PK_PRODUCT_ORDER PRIMARY KEY (Order_ID),
    CONSTRAINT FK_Order_Member FOREIGN KEY (Member_ID) REFERENCES MEMBER(Member_ID),
    CONSTRAINT CK_Order_TotalAmount CHECK (([Total_Amount]>=(0)))
);
GO

CREATE TABLE RECHARGE_RECORD (
    Recharge_ID INT NOT NULL,
    Member_ID INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    Bonus DECIMAL(10,2) NOT NULL DEFAULT ((0)),
    Total DECIMAL(10,2) NULL,
    Balance_After DECIMAL(10,2) NOT NULL,
    Recharge_Time DATETIME NOT NULL DEFAULT GETDATE(),
    Operator NVARCHAR(20) NULL,
    CONSTRAINT PK_RECHARGE_RECORD PRIMARY KEY (Recharge_ID),
    CONSTRAINT FK_Recharge_Member FOREIGN KEY (Member_ID) REFERENCES MEMBER(Member_ID),
    CONSTRAINT CK_Recharge_Amount CHECK (([Amount]>(0))),
    CONSTRAINT CK_Recharge_Bonus CHECK (([Bonus]>=(0))),
    CONSTRAINT CK_Recharge_BalanceAfter CHECK (([Balance_After]>=(0)))
);
GO

CREATE TABLE SYSTEM_CONFIG (
    Config_Key NVARCHAR(50) NOT NULL,
    Config_Value NVARCHAR(200) NOT NULL,
    Description NVARCHAR(200) NULL,
    CONSTRAINT PK_SYSTEM_CONFIG PRIMARY KEY (Config_Key)
);
GO

CREATE TABLE ZONE (
    Zone_ID INT NOT NULL,
    Zone_Name NVARCHAR(50) NOT NULL,
    Hourly_Member DECIMAL(10,2) NOT NULL,
    Hourly_Guest DECIMAL(10,2) NOT NULL,
    Overnight_Member DECIMAL(10,2) NOT NULL,
    Overnight_Guest DECIMAL(10,2) NOT NULL,
    Sort_Order INT NOT NULL DEFAULT ((0)),
    CONSTRAINT PK_ZONE PRIMARY KEY (Zone_ID),
    CONSTRAINT CK_Zone_HourlyM CHECK (([Hourly_Member]>(0))),
    CONSTRAINT CK_Zone_HourlyG CHECK (([Hourly_Guest]>(0))),
    CONSTRAINT CK_Zone_OvernightM CHECK (([Overnight_Member]>(0))),
    CONSTRAINT CK_Zone_OvernightG CHECK (([Overnight_Guest]>(0)))
);
GO

-- 4. 导入数据
-- COMPUTER (160 rows)
SET IDENTITY_INSERT COMPUTER ON;
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (1, 1, N'A001', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (2, 1, N'A002', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (3, 1, N'A003', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (4, 1, N'A004', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (5, 1, N'A005', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (6, 1, N'A006', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (7, 1, N'A007', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (8, 1, N'A008', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (9, 1, N'A009', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (10, 1, N'A010', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (11, 1, N'A011', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (12, 1, N'A012', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (13, 1, N'A013', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (14, 1, N'A014', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (15, 1, N'A015', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (16, 1, N'A016', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (17, 1, N'A017', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (18, 1, N'A018', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (19, 1, N'A019', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (20, 1, N'A020', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (21, 1, N'A021', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (22, 1, N'A022', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (23, 1, N'A023', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (24, 1, N'A024', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (25, 1, N'A025', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (26, 1, N'A026', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (27, 1, N'A027', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (28, 1, N'A028', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (29, 1, N'A029', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (30, 1, N'A030', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (31, 1, N'A031', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (32, 1, N'A032', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (33, 1, N'A033', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (34, 1, N'A034', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (35, 1, N'A035', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (36, 1, N'A036', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (37, 1, N'A037', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (38, 1, N'A038', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (39, 1, N'A039', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (40, 1, N'A040', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (41, 1, N'A041', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (42, 1, N'A042', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (43, 1, N'A043', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (44, 1, N'A044', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (45, 1, N'A045', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (46, 1, N'A046', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (47, 1, N'A047', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (48, 1, N'A048', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (49, 1, N'A049', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (50, 1, N'A050', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (51, 1, N'A051', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (52, 1, N'A052', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (53, 1, N'A053', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (54, 1, N'A054', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (55, 1, N'A055', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (56, 1, N'A056', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (57, 1, N'A057', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (58, 1, N'A058', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (59, 1, N'A059', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (60, 1, N'A060', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (61, 1, N'A061', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (62, 1, N'A062', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (63, 1, N'A063', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (64, 1, N'A064', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (65, 1, N'A065', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (66, 1, N'A066', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (67, 1, N'A067', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (68, 1, N'A068', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (69, 1, N'A069', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (70, 1, N'A070', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (71, 1, N'A071', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (72, 1, N'A072', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (73, 1, N'A073', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (74, 1, N'A074', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (75, 1, N'A075', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (76, 1, N'A076', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (77, 1, N'A077', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (78, 1, N'A078', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (79, 1, N'A079', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (80, 1, N'A080', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (81, 1, N'A081', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (82, 1, N'A082', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (83, 1, N'A083', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (84, 1, N'A084', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (85, 1, N'A085', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (86, 1, N'A086', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (87, 1, N'A087', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (88, 1, N'A088', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (89, 1, N'A089', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (90, 1, N'A090', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (91, 1, N'A091', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (92, 1, N'A092', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (93, 1, N'A093', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (94, 1, N'A094', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (95, 1, N'A095', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (96, 1, N'A096', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (97, 2, N'B001', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (98, 2, N'B002', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (99, 2, N'B003', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (100, 2, N'B004', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (101, 2, N'B005', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (102, 2, N'B006', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (103, 2, N'B007', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (104, 2, N'B008', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (105, 2, N'B009', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (106, 2, N'B010', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (107, 2, N'B011', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (108, 2, N'B012', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (109, 2, N'B013', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (110, 2, N'B014', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (111, 2, N'B015', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (112, 2, N'B016', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (113, 2, N'B017', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (114, 2, N'B018', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (115, 2, N'B019', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (116, 2, N'B020', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (117, 2, N'B021', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (118, 2, N'B022', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (119, 2, N'B023', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (120, 2, N'B024', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (121, 2, N'B025', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (122, 2, N'B026', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (123, 2, N'B027', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (124, 2, N'B028', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (125, 2, N'B029', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (126, 2, N'B030', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (127, 2, N'B031', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (128, 2, N'B032', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (129, 2, N'B033', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (130, 2, N'B034', NULL, N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (131, 3, N'C101-1', N'C101', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (132, 3, N'C101-2', N'C101', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (133, 3, N'C102-1', N'C102', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (134, 3, N'C102-2', N'C102', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (135, 3, N'C103-1', N'C103', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (136, 3, N'C103-2', N'C103', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (137, 3, N'C104-1', N'C104', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (138, 3, N'C104-2', N'C104', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (139, 3, N'C105-1', N'C105', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (140, 3, N'C105-2', N'C105', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (141, 3, N'C106-1', N'C106', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (142, 3, N'C106-2', N'C106', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (143, 3, N'C107-1', N'C107', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (144, 3, N'C107-2', N'C107', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (145, 3, N'C108-1', N'C108', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (146, 3, N'C108-2', N'C108', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (147, 4, N'D201-1', N'D201', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (148, 4, N'D201-2', N'D201', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (149, 4, N'D201-3', N'D201', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (150, 4, N'D201-4', N'D201', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (151, 4, N'D201-5', N'D201', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (152, 4, N'D202-1', N'D202', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (153, 4, N'D202-2', N'D202', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (154, 4, N'D202-3', N'D202', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (155, 4, N'D202-4', N'D202', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (156, 4, N'D202-5', N'D202', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (157, 5, N'E301', N'E301', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (158, 5, N'E302', N'E302', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (159, 5, N'E303', N'E303', N'free');
INSERT INTO COMPUTER (Computer_ID, Zone_ID, Computer_No, Room_No, Status) VALUES (160, 5, N'E304', N'E304', N'free');
SET IDENTITY_INSERT COMPUTER OFF;
GO

-- EQUIPMENT_RENTAL (6 rows)
SET IDENTITY_INSERT EQUIPMENT_RENTAL ON;
INSERT INTO EQUIPMENT_RENTAL (Rental_ID, Member_ID, Equipment_Name, Rental_Fee_Per_Day, Start_Time, End_Time, Total_Fee, Status) VALUES (1, 3, N'游戏耳机', 10.0, '2026-07-01 15:05:42', NULL, 10.0, N'returned');
INSERT INTO EQUIPMENT_RENTAL (Rental_ID, Member_ID, Equipment_Name, Rental_Fee_Per_Day, Start_Time, End_Time, Total_Fee, Status) VALUES (2, 5, N'机械键盘', 15.0, '2026-07-01 15:05:42', NULL, 30.0, N'returned');
INSERT INTO EQUIPMENT_RENTAL (Rental_ID, Member_ID, Equipment_Name, Rental_Fee_Per_Day, Start_Time, End_Time, Total_Fee, Status) VALUES (3, 6, N'充电宝', 5.0, '2026-07-01 15:05:42', '2026-07-01 17:37:05', 5.0, N'returned');
INSERT INTO EQUIPMENT_RENTAL (Rental_ID, Member_ID, Equipment_Name, Rental_Fee_Per_Day, Start_Time, End_Time, Total_Fee, Status) VALUES (4, 12, N'鼠标', 10.0, '2026-07-01 17:37:21', '2026-07-01 17:37:27', 10.0, N'returned');
INSERT INTO EQUIPMENT_RENTAL (Rental_ID, Member_ID, Equipment_Name, Rental_Fee_Per_Day, Start_Time, End_Time, Total_Fee, Status) VALUES (5, 10, N'充电宝', 5.0, '2026-07-01 18:41:57', '2026-07-01 18:43:14', 5.0, N'returned');
INSERT INTO EQUIPMENT_RENTAL (Rental_ID, Member_ID, Equipment_Name, Rental_Fee_Per_Day, Start_Time, End_Time, Total_Fee, Status) VALUES (6, 10, N'充电宝', 5.0, '2026-07-01 18:42:04', '2026-07-01 18:43:08', 5.0, N'returned');
SET IDENTITY_INSERT EQUIPMENT_RENTAL OFF;
GO

-- MEMBER (12 rows)
SET IDENTITY_INSERT MEMBER ON;
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (1, N'13800001111', N'张三', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 72.0, 100.0, 50, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (2, N'13800002222', N'李四', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 150.0, 200.0, 100, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (3, N'13800003333', N'王五', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 50.0, 100.0, 20, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (4, N'13800004444', N'赵六', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 320.0, 500.0, 220, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (5, N'13800005555', N'孙七', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 200.0, 0.0, 200, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (6, N'13800006666', N'周八', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 60.0, 0.0, 30, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (7, N'13800007777', N'吴九', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 500.0, 500.0, 600, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (8, N'13800008888', N'郑十', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 10.0, 0.0, 10, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (9, N'13800009999', N'陈一', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 90.0, 0.0, 40, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (10, N'13800001010', N'林二', N'$2b$12$04NMLyuQoeT2oYh9wdJN/.xDeWXJWIklhC271O97RQC.MDckMpTN.', 412.0, 0.0, 260, 1, '2026-07-01 15:05:42');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (11, N'13900000001', N'测试用户', N'$2b$12$ineCAkcpWv4IF0ap0h/1z.lM453CUN.7av2/7k80.EK2lQ9D3Vf0y', 0.0, 0.0, 0, 1, '2026-07-01 16:58:39');
INSERT INTO MEMBER (Member_ID, Phone, Name, Password_Hash, Balance, Total_Recharged, Points, Is_Active, Created_At) VALUES (12, N'12345678912', N'张伟', N'$2b$12$id3bIi2YNu4aOhdiNE9pUOFEFe9GHKDGIppXPFnPbPHP/0.yPG.r2', 1500.0, 1000.0, 0, 1, '2026-07-01 17:01:22');
SET IDENTITY_INSERT MEMBER OFF;
GO

-- ONLINE_RECORD (12 rows)
SET IDENTITY_INSERT ONLINE_RECORD ON;
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (1, 1, 1, '2026-06-29 14:00:00', '2026-06-29 16:30:00', N'hourly', 7.5, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (2, 2, 2, '2026-06-29 20:00:00', '2026-06-30 06:00:00', N'overnight', 28.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (3, 3, 3, '2026-06-29 09:00:00', '2026-06-29 11:00:00', N'hourly', 8.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (4, 4, 4, '2026-06-29 22:30:00', '2026-06-30 07:30:00', N'overnight', 28.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (5, 5, 5, '2026-06-30 10:00:00', '2026-06-30 13:00:00', N'hourly', 15.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (6, 6, 6, '2026-06-30 21:00:00', '2026-06-30 23:00:00', N'hourly', 10.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (7, 7, 7, '2026-06-29 12:00:00', '2026-06-30 08:00:00', N'overnight', 28.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (8, 8, 8, '2026-06-30 15:00:00', '2026-06-30 15:12:00', N'hourly', 0.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (9, 9, 9, '2026-06-30 16:00:00', '2026-06-30 18:00:00', N'hourly', 10.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (10, 10, 10, '2026-06-30 19:00:00', '2026-06-30 21:00:00', N'hourly', 10.0, NULL, N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (11, 157, 1, '2026-07-01 17:20:38', '2026-07-01 17:27:58', N'hourly', 0.0, N'总时长 8 分钟 × 0.1167 元/分钟 = 0.93 元；最低消费：上机 8 分钟 ≤ 15 分钟，免计费', N'completed', 0, NULL);
INSERT INTO ONLINE_RECORD (Record_ID, Computer_ID, Member_ID, Start_Time, End_Time, Billing_Mode, Actual_Amount, Amount_Detail, Status, Is_Guest, Guest_Phone) VALUES (12, 65, 12, '2026-07-01 17:29:45', '2026-07-01 17:29:56', N'hourly', 0.0, N'总时长 1 分钟 × 0.0500 元/分钟 = 0.05 元；最低消费：上机 1 分钟 ≤ 15 分钟，免计费', N'completed', 0, NULL);
SET IDENTITY_INSERT ONLINE_RECORD OFF;
GO

-- OPERATOR (3 rows)
SET IDENTITY_INSERT OPERATOR ON;
INSERT INTO OPERATOR (Operator_ID, Login_Name, Password_Hash, Name, Role, Created_At) VALUES (1, N'admin', N'$2b$12$0wDZzN75WCjRV4hm.Y8rme1mu1lg2UNQkx2ifCnCAuCSsw192HOMG', N'张三', N'super_admin', '2026-07-01 17:59:36');
INSERT INTO OPERATOR (Operator_ID, Login_Name, Password_Hash, Name, Role, Created_At) VALUES (2, N'cashier1', N'$2b$12$0wDZzN75WCjRV4hm.Y8rme1mu1lg2UNQkx2ifCnCAuCSsw192HOMG', N'李收银', N'cashier', '2026-07-01 17:59:36');
INSERT INTO OPERATOR (Operator_ID, Login_Name, Password_Hash, Name, Role, Created_At) VALUES (4, N'cashier2', N'$2b$12$LsiWmkvmExz31UwSdSEPVeua.d9Nu8PcghUnvDA3BjP/fRrJaGKi6', N'王收银', N'cashier', '2026-07-01 18:51:07');
SET IDENTITY_INSERT OPERATOR OFF;
GO

-- ORDER_DETAIL (9 rows)
SET IDENTITY_INSERT ORDER_DETAIL ON;
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (1, 1, 1, 2, 4.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (2, 1, 9, 2, 2.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (3, 2, 4, 2, 6.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (4, 2, 5, 3, 5.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (5, 2, 7, 1, 7.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (6, 3, 8, 1, 8.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (7, 4, 10, 1, 2.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (8, 4, 3, 1, 2.0);
INSERT INTO ORDER_DETAIL (Detail_ID, Order_ID, Product_ID, Quantity, Unit_Price) VALUES (9, 4, 1, 1, 4.0);
SET IDENTITY_INSERT ORDER_DETAIL OFF;
GO

-- PRODUCT (10 rows)
SET IDENTITY_INSERT PRODUCT ON;
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (1, N'可口可乐', N'饮料', 4.0, 51, N'瓶', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (2, N'雪碧', N'饮料', 4.0, 50, N'瓶', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (3, N'农夫山泉', N'饮料', 2.0, 59, N'瓶', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (4, N'红牛', N'饮料', 6.0, 30, N'罐', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (5, N'康师傅红烧牛肉面', N'泡面', 5.0, 40, N'桶', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (6, N'统一老坛酸菜面', N'泡面', 5.0, 30, N'桶', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (7, N'乐事薯片', N'零食', 7.0, 35, N'袋', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (8, N'奥利奥', N'零食', 8.0, 14, N'盒', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (9, N'火腿肠', N'零食', 2.0, 50, N'根', 1);
INSERT INTO PRODUCT (Product_ID, Name, Category, Price, Stock, Unit, Is_Available) VALUES (10, N'纸巾', N'日用品', 2.0, 29, N'包', 1);
SET IDENTITY_INSERT PRODUCT OFF;
GO

-- PRODUCT_ORDER (4 rows)
SET IDENTITY_INSERT PRODUCT_ORDER ON;
INSERT INTO PRODUCT_ORDER (Order_ID, Member_ID, Total_Amount, Order_Time, Operator) VALUES (1, 1, 12.0, '2026-07-01 15:05:42', N'收银员');
INSERT INTO PRODUCT_ORDER (Order_ID, Member_ID, Total_Amount, Order_Time, Operator) VALUES (2, 2, 34.0, '2026-07-01 15:05:42', N'收银员');
INSERT INTO PRODUCT_ORDER (Order_ID, Member_ID, Total_Amount, Order_Time, Operator) VALUES (3, 1, 8.0, '2026-07-01 17:21:01', N'收银员');
INSERT INTO PRODUCT_ORDER (Order_ID, Member_ID, Total_Amount, Order_Time, Operator) VALUES (4, 10, 8.0, '2026-07-01 18:34:59', N'收银员');
SET IDENTITY_INSERT PRODUCT_ORDER OFF;
GO

-- RECHARGE_RECORD (6 rows)
SET IDENTITY_INSERT RECHARGE_RECORD ON;
INSERT INTO RECHARGE_RECORD (Recharge_ID, Member_ID, Amount, Bonus, Balance_After, Recharge_Time, Operator) VALUES (1, 1, 100.0, 30.0, 130.0, '2026-07-01 15:05:42', N'收银员');
INSERT INTO RECHARGE_RECORD (Recharge_ID, Member_ID, Amount, Bonus, Balance_After, Recharge_Time, Operator) VALUES (2, 2, 200.0, 70.0, 270.0, '2026-07-01 15:05:42', N'收银员');
INSERT INTO RECHARGE_RECORD (Recharge_ID, Member_ID, Amount, Bonus, Balance_After, Recharge_Time, Operator) VALUES (3, 3, 100.0, 30.0, 130.0, '2026-07-01 15:05:42', N'收银员');
INSERT INTO RECHARGE_RECORD (Recharge_ID, Member_ID, Amount, Bonus, Balance_After, Recharge_Time, Operator) VALUES (4, 4, 500.0, 220.0, 720.0, '2026-07-01 15:05:42', N'收银员');
INSERT INTO RECHARGE_RECORD (Recharge_ID, Member_ID, Amount, Bonus, Balance_After, Recharge_Time, Operator) VALUES (5, 7, 500.0, 220.0, 720.0, '2026-07-01 15:05:42', N'收银员');
INSERT INTO RECHARGE_RECORD (Recharge_ID, Member_ID, Amount, Bonus, Balance_After, Recharge_Time, Operator) VALUES (6, 12, 1000.0, 500.0, 1500.0, '2026-07-01 17:29:21', N'收银员');
SET IDENTITY_INSERT RECHARGE_RECORD OFF;
GO

-- SYSTEM_CONFIG (2 rows)
INSERT INTO SYSTEM_CONFIG (Config_Key, Config_Value, Description) VALUES (N'holiday_surcharge', N'0', N'节假日加价开关 0=关 1=开');
INSERT INTO SYSTEM_CONFIG (Config_Key, Config_Value, Description) VALUES (N'min_charge_threshold', N'15', N'最低消费免计分钟数');
GO

-- ZONE (5 rows)
SET IDENTITY_INSERT ZONE ON;
INSERT INTO ZONE (Zone_ID, Zone_Name, Hourly_Member, Hourly_Guest, Overnight_Member, Overnight_Guest, Sort_Order) VALUES (1, N'普通大厅区', 3.0, 4.0, 18.0, 25.0, 1);
INSERT INTO ZONE (Zone_ID, Zone_Name, Hourly_Member, Hourly_Guest, Overnight_Member, Overnight_Guest, Sort_Order) VALUES (2, N'电竞大厅区', 5.0, 6.0, 28.0, 38.0, 2);
INSERT INTO ZONE (Zone_ID, Zone_Name, Hourly_Member, Hourly_Guest, Overnight_Member, Overnight_Guest, Sort_Order) VALUES (3, N'双人包间', 6.0, 8.0, 35.0, 45.0, 3);
INSERT INTO ZONE (Zone_ID, Zone_Name, Hourly_Member, Hourly_Guest, Overnight_Member, Overnight_Guest, Sort_Order) VALUES (4, N'五人战队包间', 6.0, 8.0, 35.0, 45.0, 4);
INSERT INTO ZONE (Zone_ID, Zone_Name, Hourly_Member, Hourly_Guest, Overnight_Member, Overnight_Guest, Sort_Order) VALUES (5, N'单人私密包间', 7.0, 9.0, 40.0, 50.0, 5);
SET IDENTITY_INSERT ZONE OFF;
GO
