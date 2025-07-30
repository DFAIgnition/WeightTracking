USE [weight];
GO

alter table weight.dbo.filler add is_line_total bit default 0;
update weight.dbo.filler set is_line_total = 0;


INSERT INTO weight.dbo.versions (version_number) VALUES (1.06);
