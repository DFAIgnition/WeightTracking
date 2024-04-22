--------------------------------------------------------------------------------
-- Use weight DB
--------------------------------------------------------------------------------

USE [weight];
GO

--------------------------------------------------------------------------------
-- Add conversion factor for unit to convert to gram
--------------------------------------------------------------------------------

ALTER TABLE weight.dbo.unit
ADD unit_conversion FLOAT NOT NULL CONSTRAINT DF_Unit_Conversion DEFAULT 1;
GO

--------------------------------------------------------------------------------
-- Add description field to tables
--------------------------------------------------------------------------------

ALTER TABLE weight.dbo.type
ADD type_desc NVARCHAR(255);
GO

ALTER TABLE weight.dbo.line
ADD line_desc NVARCHAR(255);
GO

ALTER TABLE weight.dbo.filler
ADD filler_desc NVARCHAR(255);
GO


--------------------------------------------------------------------------------
-- Permissions stuf
--------------------------------------------------------------------------------


-- Create SITEADMIN permission
insert into system.dbo.project_permissions (project_id, permission_code, permission_display_name, area_type)
values ((select project_id from system.dbo.projects where project_name = 'WeightTracking'), 'APPADMIN', 'App Admin', 'site');

GO

--------------------------------------------------------------------------------
-- Versions table update
--------------------------------------------------------------------------------

insert into weight.dbo.versions (version_number) values (1.01);
GO


