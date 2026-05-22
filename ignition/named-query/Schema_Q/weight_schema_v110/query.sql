USE [weight];
GO
-- Add in shift config columns
alter table line add shifts_per_day int default 2;
alter table line add shift_length int default 12;
alter table line add shift_start int default 0;
update line set shifts_per_day=2, shift_length=12, shift_start=0 where shifts_per_day is null; 

-- Add in shift tracking columns
alter table aggregated add shift_date char(8) default null;
alter table aggregated add shift_number int default 1;

INSERT INTO weight.dbo.versions (version_number) VALUES (1.10);
