USE [weight];
GO


-- Add the po number column in
alter table [weight].dbo.rejects
add po_number int default null;


INSERT INTO weight.dbo.versions (version_number) VALUES (1.05);
