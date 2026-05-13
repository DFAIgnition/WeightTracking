USE [weight];
GO

ALTER TABLE weight.dbo.line
ADD metal_test_tag NVARCHAR(255) NULL,
    metal_test_tag_type char(1) NULL;
    
ALTER TABLE weight.dbo.rejects
ADD metal_test_count INT DEFAULT 0,
    metal_actual_count INT DEFAULT 0;

INSERT INTO weight.dbo.versions (version_number) VALUES (1.09);
