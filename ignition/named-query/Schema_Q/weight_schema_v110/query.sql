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


INSERT INTO weight.dbo.versions (version_number) VALUES (1.10);
