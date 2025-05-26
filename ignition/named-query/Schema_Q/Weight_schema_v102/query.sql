--------------------------------------------------------------------------------
-- Use weight DB
--------------------------------------------------------------------------------

USE [weight];
GO

--------------------------------------------------------------------------------
-- Add description field to tables
--------------------------------------------------------------------------------

-- Adding line_weight_min
ALTER TABLE weight.dbo.line
ADD line_weight_min FLOAT NOT NULL CONSTRAINT DF_Line_Weight_Min DEFAULT 20000.0;
GO

-- Adding line_weight_max
ALTER TABLE weight.dbo.line
ADD line_weight_max FLOAT NOT NULL CONSTRAINT DF_Line_Weight_Max DEFAULT 30000.0;
GO

-- Adding constraint to ensure line_weight_max is greater than line_weight_min
ALTER TABLE weight.dbo.line
ADD CONSTRAINT CK_Line_Weight CHECK (line_weight_max > line_weight_min);
GO



--------------------------------------------------------------------------------
-- Versions table update
--------------------------------------------------------------------------------

INSERT INTO weight.dbo.versions (version_number) VALUES (1.02);
GO
