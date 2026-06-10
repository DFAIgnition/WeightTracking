USE [weight];
GO
-- Add in shift config columns
alter table line add shifts_per_day int default 1;
alter table line add shift_length int default 24;
alter table line add shift_start int default 0;
update line set shifts_per_day=1, shift_length=24, shift_start=0 where shifts_per_day is null; 

-- Add in shift tracking columns
alter table aggregated add shift_date char(8) default null;
alter table aggregated add shift_number int default 1;

create table manual_losses(
	manual_loss_id int IDENTITY(1,1) NOT NULL,
	line_id int not null, 
	shift_id char(10), 
    shift_date char(8), 
	shift_number int,
	loss_grams decimal(10,2),
	loss_per_hour decimal(10,2),
    cost_per_hour decimal(10,2),
	edited_dt	datetime2(0),
	edited_by	varchar(32)
);

-- Create date entry permission
IF NOT EXISTS(SELECT * FROM system.dbo.project_permissions WHERE project_id = (select project_id from system.dbo.projects where project_name = 'WeightTracking') and permission_code = 'SITEDATA') 
BEGIN
	insert into system.dbo.project_permissions (project_id, permission_code, permission_display_name, area_type)
	values ((select project_id from system.dbo.projects where project_name = 'WeightTracking'), 'SITEDATA', 'Site Data Entry', 'site')
END
GO 

-- Add some more indexes to speed things up...
CREATE INDEX [aggregated_shift_i] ON [dbo].[aggregated]
(
	[shift_date] asc, 
	[shift_number] asc,
	[scale_id] ASC,
	[material] ASC,
	[po_number] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [aggregated_shift_i2] ON [dbo].[aggregated] ([shift_date],[shift_number]) 
INCLUDE ([scale_id],[time_start],[count],[weight_sum],[weight_diff],[pct_weight_over],[pct_weight_under],[material],[total_count]);

CREATE NONCLUSTERED INDEX [aggregated_shift_i3] ON [dbo].[aggregated] ([scale_id],[shift_date],[shift_number]) 
INCLUDE ([time_start],[count],[weight_sum],[weight_diff],[pct_weight_over],[pct_weight_under],[material],[total_count])

CREATE NONCLUSTERED INDEX rejects_i ON [dbo].[rejects] ([line_id],[time_start],[material]) INCLUDE ([metal_count],[weight_count])

CREATE INDEX IX_giveaway_line_eventdt 
ON weight.dbo.giveaway (line_id, event_dt, quality_flag)
INCLUDE (site_id, filler_id, sku_id, 
         delta_target_grams, delta_actual_grams, delta_giveaway_grams)


update statistics [aggregated];
update statistics [rejects];


INSERT INTO weight.dbo.versions (version_number) VALUES (1.10);
