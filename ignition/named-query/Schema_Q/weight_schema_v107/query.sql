USE [weight];
GO

alter table weight.dbo.line add exclude_out_of_range bit default 0;
update weight.dbo.line set exclude_out_of_range = 0;

-- Count can now exclude units that are over/underweight, so we need to also record Total count 
-- as a measure of how many things were created, flawed or not
alter table aggregated add total_count int default 0;
update aggregated set total_count = [count];

INSERT INTO weight.dbo.versions (version_number) VALUES (1.07);
