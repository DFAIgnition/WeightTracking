--------------------------------------------------------------------------------
-- Use weight DB
--------------------------------------------------------------------------------

USE [weight];
GO

-- Add a starr_unit_id column to optionally use instead of material tag
ALTER TABLE weight.dbo.line
ADD starr_unit_id INT DEFAULT NULL;

ALTER TABLE weight.dbo.line
ADD metal_reject_tag NVARCHAR(255) DEFAULT NULL, 
weight_reject_tag NVARCHAR(255) DEFAULT NULL, 
metal_reject_tag_type char(1),
weight_reject_tag_type char(1);


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


CREATE TABLE weight.dbo.rejects (
    reject_id 		INT PRIMARY KEY IDENTITY(1,1),
    line_id			INT NOT NULL,
	time_start		datetime2(0),
	metal_count		int, 
	weight_count	int,
	material		nvarchar(32)
);

-- Add the po number column in
alter table [weight].dbo.aggregated
add po_number int default null;

drop index aggregated.aggregated_u;
/****** Object:  Index [aggregated_u]    Script Date: 9/06/2025 10:38:56 am ******/
CREATE UNIQUE NONCLUSTERED INDEX [aggregated_u] ON [dbo].[aggregated]
(
	[time_start] ASC,
	[scale_id] ASC,
	[material] ASC,
	[po_number] ASC
)

WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

alter table weight.dbo.[type]
add fill_type nvarchar(8) default 'item';
update weight.dbo.[type] set fill_type='item';
update weight.dbo.[type] set fill_type='case' where type_name = 'Case';

--------------------------------------------------------------------------------
-- Versions table update
--------------------------------------------------------------------------------
INSERT INTO weight.dbo.versions (version_number) VALUES (1.03);
GO
