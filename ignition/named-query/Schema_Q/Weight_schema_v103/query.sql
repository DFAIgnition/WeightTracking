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


CREATE UNIQUE NONCLUSTERED INDEX [aggregated_u] ON [dbo].[aggregated]
(
	[time_start] ASC,
	[scale_id] ASC,
	[material] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO



--------------------------------------------------------------------------------
-- Versions table update
--------------------------------------------------------------------------------
INSERT INTO weight.dbo.versions (version_number) VALUES (1.03);
GO
