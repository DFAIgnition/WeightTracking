--------------------------------------------------------------------------------
-- Use weight DB
--------------------------------------------------------------------------------

USE [weight];
GO

alter table unit
add unit_description nvarchar(32);

update unit set unit_description = 'Grams' where unit_name = 'g';
update unit set unit_description = 'Pounds' where unit_name = 'lbs';
update unit set unit_description = 'Kilograms' where unit_name = 'kg';
update unit set unit_description = 'Ounces' where unit_name = 'oz';

--------------------------------------------------------------------------------
-- Versions table update
--------------------------------------------------------------------------------
INSERT INTO weight.dbo.versions (version_number) VALUES (1.04);
GO
