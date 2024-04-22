/****** Object:  Database [weight]    ******/
CREATE DATABASE [weight]
GO

USE [weight]
GO

--------------------------------------------------------------------------------
-- type table
--------------------------------------------------------------------------------

CREATE TABLE weight.dbo.type (
    type_id 				INT PRIMARY KEY IDENTITY(1,1),
    type_name 				NVARCHAR(255) NOT NULL,
    UNIQUE(type_name)
	);
	GO

--------------------------------------------------------------------------------
-- units table
--------------------------------------------------------------------------------

CREATE TABLE weight.dbo.unit (
    unit_id 				INT PRIMARY KEY IDENTITY(1,1),
    unit_name 				NVARCHAR(255) NOT NULL,
    UNIQUE(unit_name)
	);
	GO

 --------------------------------------------------------------------------------
-- line table
--------------------------------------------------------------------------------

CREATE TABLE weight.dbo.line (
	line_id 				INT PRIMARY KEY IDENTITY(1,1),
	type_id 				INT NOT NULL,
	site_id 				INT NOT NULL,
	line_name 				NVARCHAR(255) NOT NULL,
	line_material 			NVARCHAR(255) NULL,
	
	CONSTRAINT FK_type_id FOREIGN KEY (type_id) REFERENCES weight.dbo.type(type_id),
	CONSTRAINT UQ_site_type_line UNIQUE (site_id, type_id, line_name)
	);
	GO
	

--------------------------------------------------------------------------------
-- filler table
--------------------------------------------------------------------------------

CREATE TABLE weight.dbo.filler (
    filler_id 						INT PRIMARY KEY IDENTITY(1,1),
    line_id 						INT NOT NULL,
    unit_id 						INT NOT NULL,
    filler_name 					NVARCHAR(255) NOT NULL,
    filler_design					DECIMAL(10, 2) NOT NULL,
    filler_sp_low 					DECIMAL(10, 2) NOT NULL,
    filler_sp						DECIMAL(10, 2) NOT NULL,    
    filler_sp_high 					DECIMAL(10, 2) NOT NULL,
    filler_sp_low_tag				NVARCHAR(255) NULL,
    filler_sp_tag					NVARCHAR(255) NULL,      
    filler_sp_high_tag				NVARCHAR(255) NULL,
	filler_reject 					NVARCHAR(255) NULL,
	filler_reject_cond				NVARCHAR(255) NULL,
	filler_metal 					NVARCHAR(255) NULL,
	filler_metal_cond				NVARCHAR(255) NULL,
	filler_reason_over 				NVARCHAR(255) NULL,
	filler_reason_over_cond		NVARCHAR(255) NULL,
	filler_reason_under 			NVARCHAR(255) NULL,
	filler_reason_under_cond		NVARCHAR(255) NULL,
	filler_reason_metal 			NVARCHAR(255) NULL,
	filler_reason_metal_cond		NVARCHAR(255) NULL,
    
    CONSTRAINT FK_line_id FOREIGN KEY (line_id) REFERENCES weight.dbo.line(line_id),
    CONSTRAINT FK_unit_id FOREIGN KEY (unit_id) REFERENCES weight.dbo.unit(unit_id),
    CONSTRAINT UQ_line_filler UNIQUE (line_id, filler_name)
	);
	GO		
	
--------------------------------------------------------------------------------
-- scale table
--------------------------------------------------------------------------------

CREATE TABLE weight.dbo.scale (
    scale_id 				INT PRIMARY KEY IDENTITY(1,1),
    filler_id 				INT NOT NULL,
    scale_name 				NVARCHAR(255) NOT NULL,
    scale_weight			NVARCHAR(255) NOT NULL,
    
    CONSTRAINT FK_filler_id FOREIGN KEY (filler_id) REFERENCES weight.dbo.filler(filler_id),
    CONSTRAINT UQ_scale_filler UNIQUE (filler_id, scale_name)
	);
	GO

--------------------------------------------------------------------------------
-- aggregate table
--------------------------------------------------------------------------------

CREATE TABLE weight.dbo.aggregated (
    aggregate_id 			INT PRIMARY KEY IDENTITY(1,1),
    scale_id 				INT NOT NULL,
    time_start 				DATETIME2 NOT NULL,
    count	 				INT NOT NULL,
    weight_avg 				DECIMAL(10, 2) NOT NULL,
    weight_sum 				DECIMAL(10, 2) NOT NULL,
    weight_diff 			DECIMAL(10, 2) NOT NULL,
    pct_weight_over 		DECIMAL(5, 2) NOT NULL,
    pct_weight_under 		DECIMAL(5, 2) NOT NULL,
    pct_out_of_range 		DECIMAL(5, 2) NOT NULL,
    standard_deviation 	DECIMAL(10, 2) NOT NULL,
    variance 				DECIMAL(20, 2) NOT NULL,
    weight_range 			DECIMAL(10, 2) NOT NULL,
    weight_max 				DECIMAL(10, 2) NOT NULL,
    weight_min 				DECIMAL(10, 2) NOT NULL,
    percentile25 			DECIMAL(10, 2) NOT NULL,
    percentile50 			DECIMAL(10, 2) NOT NULL,
    percentile75			DECIMAL(10, 2) NOT NULL,
    reject_metal			INT NOT NULL,
    reject_over				INT NOT NULL,
    reject_under			INT NOT NULL,
    material				NVARCHAR(50) NOT NULL,
    sp_high					DECIMAL(10, 2) NOT NULL,
    sp						DECIMAL(10, 2) NOT NULL,
    sp_low					DECIMAL(10, 2) NOT NULL,
    sp_high_plc				DECIMAL(10, 2) NOT NULL,
    sp_plc					DECIMAL(10, 2) NOT NULL,
    sp_low_plc				DECIMAL(10, 2) NOT NULL,
    design					DECIMAL(10, 2) NOT NULL,
    

    CONSTRAINT FK_scale_id FOREIGN KEY (scale_id) REFERENCES weight.dbo.scale(scale_id)
);
GO

--------------------------------------------------------------------------------
-- Permissions stuf
--------------------------------------------------------------------------------
IF NOT EXISTS(SELECT * FROM system.dbo.projects WHERE project_name = 'WeightTracking') 
BEGIN
	INSERT INTO system.dbo.projects (project_name, project_display_name, is_active) 
	VALUES ('WeightTracking', 'Weight Tracking', 1)
END

GO 

-- Create SITEADMIN permission
insert into system.dbo.project_permissions (project_id, permission_code, permission_display_name, area_type)
values ((select project_id from system.dbo.projects where project_name = 'WeightTracking'), 'SITEADMIN', 'Site Admin', 'site');
insert into system.dbo.project_permissions (project_id, permission_code, permission_display_name, area_type)
values ((select project_id from system.dbo.projects where project_name = 'WeightTracking'), 'USERADMIN', 'User Admin', 'site');

GO

--------------------------------------------------------------------------------
-- Versions table
--------------------------------------------------------------------------------
CREATE TABLE weight.dbo.versions
	(
	version_number decimal(5,2) NOT NULL,
	install_dt smalldatetime NOT NULL
	)  ON [PRIMARY];
GO	
ALTER TABLE weight.dbo.versions ADD CONSTRAINT
	DF_Table_1_install_dt DEFAULT CURRENT_TIMESTAMP FOR install_dt;
GO
ALTER TABLE weight.dbo.versions ADD CONSTRAINT
PK_Table_1 PRIMARY KEY CLUSTERED (version_number) WITH( STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
GO
insert into weight.dbo.versions (version_number) values (1.00);
GO


