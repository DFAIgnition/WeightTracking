--------------------------------------------------------------------------------
-- Use weight DB
--------------------------------------------------------------------------------

USE [weight];
GO

-- Add a starr_unit_id column to optionally use instead of material tag
ALTER TABLE weight.dbo.line
ADD starr_unit_id INT DEFAULT NULL;

-- Get rid of all the extra sub-second precision in the dates
alter table [weight].dbo.aggregated
alter column time_start datetime2(0);

--------------------------------------------------------------------------------
-- Versions table update
--------------------------------------------------------------------------------
INSERT INTO weight.dbo.versions (version_number) VALUES (1.03);
GO
