USE [weight]
GO

-- ============================================================
-- sku_type
-- ============================================================

IF OBJECT_ID('dbo.sku_type', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.sku_type (
        sku_id INT IDENTITY(1,1) NOT NULL,
        sku_code NVARCHAR(50) NOT NULL,
        sku_description NVARCHAR(255) NULL,
        nominal_net_grams DECIMAL(12,3) NULL,
        CONSTRAINT PK_sku_type PRIMARY KEY CLUSTERED (sku_id),
        CONSTRAINT UQ_sku_type_code UNIQUE (sku_code)
    );
END
GO

-- Seed values
MERGE dbo.sku_type AS t
USING (VALUES
    ('3OZ',  '3 oz retail',  85.05),
    ('8OZ',  '8 oz retail',  226.80),
    ('16OZ', '16 oz retail', 453.59),
    ('24OZ', '24 oz retail', 680.39)
) AS s (sku_code, sku_description, nominal_net_grams)
ON t.sku_code = s.sku_code
WHEN NOT MATCHED THEN
    INSERT (sku_code, sku_description, nominal_net_grams)
    VALUES (s.sku_code, s.sku_description, s.nominal_net_grams);
GO

-- ============================================================
-- sku_cost
-- ============================================================

IF OBJECT_ID('dbo.sku_cost', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.sku_cost (
        sku_cost_id BIGINT IDENTITY(1,1) NOT NULL,
        sku_id INT NOT NULL,
        effective_start_dt DATE NOT NULL,
        effective_end_dt DATE NULL,
        cost_per_lb DECIMAL(18,6) NOT NULL,
        comment NVARCHAR(255) NULL,
        site_id INT NOT NULL,
        CONSTRAINT PK_sku_cost PRIMARY KEY CLUSTERED (sku_cost_id),
        CONSTRAINT UQ_sku_cost_start UNIQUE (site_id, sku_id, effective_start_dt)
    );
END
GO

-- ============================================================
-- sku_map
-- ============================================================

IF OBJECT_ID('dbo.sku_map', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.sku_map (
        sku_map_id INT IDENTITY(1,1) NOT NULL,
        site_id INT NOT NULL,
        line_id INT NOT NULL,
        recipe_no INT NOT NULL,
        sku_id INT NOT NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_dt DATETIME2(7) NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT PK_sku_map PRIMARY KEY CLUSTERED (sku_map_id),
        CONSTRAINT UQ_sku_map UNIQUE (site_id, line_id, recipe_no)
    );
END
GO

-- ============================================================
-- giveaway
-- ============================================================

IF OBJECT_ID('dbo.giveaway', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.giveaway (
        giveaway_id BIGINT IDENTITY(1,1) NOT NULL,
        event_dt DATETIME2(7) NOT NULL,
        site_id INT NOT NULL,
        line_id INT NOT NULL,
        filler_id INT NULL,
        sku_id INT NOT NULL,
        campaign_id NVARCHAR(80) NULL,

        campaign_key AS ISNULL(campaign_id, N'') PERSISTED,
        filler_key   AS ISNULL(filler_id, -1) PERSISTED,

        delta_target_grams DECIMAL(18,3) NOT NULL,
        delta_actual_grams DECIMAL(18,3) NOT NULL,
        delta_giveaway_grams AS (delta_actual_grams - delta_target_grams) PERSISTED,

        quality_flag TINYINT NOT NULL DEFAULT 0,
        inserted_dt DATETIME2(7) NOT NULL DEFAULT SYSDATETIME(),

        target_grams_total DECIMAL(18,3) NULL,
        actual_grams_total DECIMAL(18,3) NULL,

        CONSTRAINT PK_giveaway PRIMARY KEY CLUSTERED (giveaway_id)
    );
END
GO

-- ============================================================
-- giveaway_config
-- ============================================================

IF OBJECT_ID('dbo.giveaway_config', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.giveaway_config (
        giveaway_config_id INT IDENTITY(1,1) NOT NULL,
        is_enabled BIT NOT NULL DEFAULT 1,
        site_id INT NOT NULL,
        line_id INT NOT NULL,
        filler_id INT NULL,
        use_campaign_id BIT NOT NULL DEFAULT 0,
        jobid_tag NVARCHAR(255) NOT NULL,
        recipe_tag NVARCHAR(255) NOT NULL,
        weight_target_tag NVARCHAR(255) NOT NULL,
        weight_actual_tag NVARCHAR(255) NOT NULL,
        reset_threshold_grams DECIMAL(18,3) NOT NULL DEFAULT 200,
        max_delta_grams DECIMAL(18,3) NOT NULL DEFAULT 5000000,
        created_dt DATETIME2(7) NOT NULL DEFAULT SYSDATETIME(),
        updated_dt DATETIME2(7) NOT NULL DEFAULT SYSDATETIME(),
        filler_key AS ISNULL(filler_id, -1) PERSISTED,
        CONSTRAINT PK_giveaway_config PRIMARY KEY CLUSTERED (giveaway_config_id)
    );
END
GO

-- ============================================================
-- giveaway_tag_state
-- ============================================================

IF OBJECT_ID('dbo.giveaway_tag_state', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.giveaway_tag_state (
        giveaway_state_id BIGINT IDENTITY(1,1) NOT NULL,
        line_id INT NOT NULL,
        filler_id INT NULL,
        sku_id INT NOT NULL,
        campaign_id NVARCHAR(80) NULL,

        campaign_key AS ISNULL(campaign_id, N'') PERSISTED,
        filler_key   AS ISNULL(filler_id, -1) PERSISTED,

        last_event_dt DATETIME2(7) NOT NULL,
        last_target_grams DECIMAL(18,3) NOT NULL,
        last_actual_grams DECIMAL(18,3) NOT NULL,

        CONSTRAINT PK_giveaway_tag_state PRIMARY KEY CLUSTERED (giveaway_state_id)
    );
END
GO

-- ============================================================
-- USEFUL INDEXES (from your original script)
-- ============================================================

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_sku_cost_lookup')
CREATE INDEX IX_sku_cost_lookup
ON dbo.sku_cost (site_id, sku_id, effective_start_dt DESC, effective_end_dt);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_giveaway_time_line_sku')
CREATE INDEX IX_giveaway_time_line_sku
ON dbo.giveaway (event_dt, line_id, sku_id)
INCLUDE (delta_target_grams, delta_actual_grams, delta_giveaway_grams,
         filler_id, campaign_id, site_id, quality_flag);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_giveaway_line_time')
CREATE INDEX IX_giveaway_line_time
ON dbo.giveaway (line_id, event_dt)
INCLUDE (sku_id, delta_target_grams, delta_actual_grams, delta_giveaway_grams,
         filler_id, campaign_id, site_id, quality_flag);
GO

-- ============================================================
-- VIEW: DAILY
-- ============================================================

CREATE OR ALTER VIEW dbo.vw_giveaway_daily
AS
SELECT
    g.site_id,
    CAST(g.event_dt AS date)  AS production_date,
    g.line_id,
    g.filler_id,

    s.sku_code,
    s.sku_description,

    SUM(g.delta_target_grams)   AS target_grams,
    SUM(g.delta_actual_grams)   AS actual_grams,
    SUM(g.delta_giveaway_grams) AS giveaway_grams,

    SUM(g.delta_giveaway_grams) / NULLIF(453.59237, 0)                              AS giveaway_lbs,
    SUM(g.delta_actual_grams)   / NULLIF(s.nominal_net_grams, 0)                    AS packages_produced,
    SUM(g.delta_giveaway_grams) / NULLIF(SUM(g.delta_actual_grams), 0) * 100        AS giveaway_percent,

    SUM(g.delta_giveaway_grams)
        / NULLIF(SUM(g.delta_actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)     AS giveaway_per_package_grams,

    sc.cost_per_lb,

    (SUM(g.delta_giveaway_grams) / NULLIF(453.59237, 0)) * sc.cost_per_lb           AS giveaway_dollars,

    ((SUM(g.delta_giveaway_grams) / NULLIF(453.59237, 0)) * sc.cost_per_lb)
        / NULLIF(SUM(g.delta_actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)     AS giveaway_dollars_per_package

FROM dbo.giveaway g

LEFT JOIN dbo.sku_type s
    ON g.sku_id = s.sku_id

LEFT JOIN dbo.sku_cost sc
    ON  sc.site_id = g.site_id
    AND sc.sku_id  = g.sku_id
    AND CAST(g.event_dt AS date) >= sc.effective_start_dt
    AND CAST(g.event_dt AS date) <= ISNULL(sc.effective_end_dt, '9999-12-31')

WHERE g.quality_flag = 0

GROUP BY
    g.site_id,
    CAST(g.event_dt AS date),
    g.line_id,
    g.filler_id,
    s.sku_code,
    s.sku_description,
    s.nominal_net_grams,
    sc.cost_per_lb;
GO


-- ============================================================
-- VIEW: MONTHLY
-- ============================================================

CREATE OR ALTER VIEW dbo.vw_giveaway_monthly
AS
SELECT
    g.site_id,
    DATEFROMPARTS(YEAR(g.event_dt), MONTH(g.event_dt), 1) AS production_month,
    g.line_id,
    g.filler_id,

    s.sku_code,
    s.sku_description,

    SUM(g.delta_target_grams)   AS target_grams,
    SUM(g.delta_actual_grams)   AS actual_grams,
    SUM(g.delta_giveaway_grams) AS giveaway_grams,

    SUM(g.delta_giveaway_grams) / NULLIF(453.59237, 0)                              AS giveaway_lbs,
    SUM(g.delta_actual_grams)   / NULLIF(s.nominal_net_grams, 0)                    AS packages_produced,
    SUM(g.delta_giveaway_grams) / NULLIF(SUM(g.delta_actual_grams), 0) * 100        AS giveaway_percent,

    SUM(g.delta_giveaway_grams)
        / NULLIF(SUM(g.delta_actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)     AS giveaway_per_package_grams,

    -- weighted avg cost
    SUM((g.delta_giveaway_grams / NULLIF(453.59237, 0)) * sc.cost_per_lb)
        / NULLIF(SUM(g.delta_giveaway_grams / NULLIF(453.59237, 0)), 0)             AS cost_per_lb,

    SUM((g.delta_giveaway_grams / NULLIF(453.59237, 0)) * sc.cost_per_lb)           AS giveaway_dollars,

    SUM((g.delta_giveaway_grams / NULLIF(453.59237, 0)) * sc.cost_per_lb)
        / NULLIF(SUM(g.delta_actual_grams) / NULLIF(s.nominal_net_grams, 0), 0)     AS giveaway_dollars_per_package

FROM dbo.giveaway g

LEFT JOIN dbo.sku_type s
    ON g.sku_id = s.sku_id

LEFT JOIN dbo.sku_cost sc
    ON  sc.site_id = g.site_id
    AND sc.sku_id  = g.sku_id
    AND CAST(g.event_dt AS date) >= sc.effective_start_dt
    AND CAST(g.event_dt AS date) <= ISNULL(sc.effective_end_dt, '9999-12-31')

WHERE g.quality_flag = 0

GROUP BY
    g.site_id,
    DATEFROMPARTS(YEAR(g.event_dt), MONTH(g.event_dt), 1),
    g.line_id,
    g.filler_id,
    s.sku_code,
    s.sku_description,
    s.nominal_net_grams;
GO


-- ============================================================
-- VIEW: DAILY TOTAL
-- ============================================================

CREATE OR ALTER VIEW dbo.vw_giveaway_daily_total
AS
SELECT
    g.site_id,
    CAST(g.event_dt AS date) AS production_date,

    SUM(g.delta_target_grams)   AS target_grams,
    SUM(g.delta_actual_grams)   AS actual_grams,
    SUM(g.delta_giveaway_grams) AS giveaway_grams,

    SUM(g.delta_giveaway_grams) / 453.59237 AS giveaway_lbs,

    SUM(g.delta_giveaway_grams)
        / NULLIF(SUM(g.delta_actual_grams),0) * 100 AS giveaway_percent,

    SUM((g.delta_giveaway_grams / 453.59237) * sc.cost_per_lb) AS giveaway_dollars,

    SUM((g.delta_giveaway_grams / 453.59237) * sc.cost_per_lb)
        / NULLIF(SUM(g.delta_giveaway_grams / 453.59237),0) AS cost_per_lb

FROM dbo.giveaway g

LEFT JOIN dbo.sku_cost sc
    ON  sc.site_id = g.site_id
    AND sc.sku_id  = g.sku_id
    AND CAST(g.event_dt AS date) >= sc.effective_start_dt
    AND CAST(g.event_dt AS date) <= ISNULL(sc.effective_end_dt,'9999-12-31')

WHERE g.quality_flag = 0

GROUP BY
    g.site_id,
    CAST(g.event_dt AS date);
GO


-- ============================================================
-- VIEW: MONTHLY TOTAL
-- ============================================================

CREATE OR ALTER VIEW dbo.vw_giveaway_monthly_total
AS
SELECT
    g.site_id,
    DATEFROMPARTS(YEAR(g.event_dt), MONTH(g.event_dt), 1) AS production_month,

    SUM(g.delta_target_grams)   AS target_grams,
    SUM(g.delta_actual_grams)   AS actual_grams,
    SUM(g.delta_giveaway_grams) AS giveaway_grams,

    SUM(g.delta_giveaway_grams) / 453.59237 AS giveaway_lbs,

    SUM(g.delta_giveaway_grams)
        / NULLIF(SUM(g.delta_actual_grams),0) * 100 AS giveaway_percent,

    SUM((g.delta_giveaway_grams / 453.59237) * sc.cost_per_lb) AS giveaway_dollars,

    SUM((g.delta_giveaway_grams / 453.59237) * sc.cost_per_lb)
        / NULLIF(SUM(g.delta_giveaway_grams / 453.59237),0) AS cost_per_lb

FROM dbo.giveaway g

LEFT JOIN dbo.sku_cost sc
    ON  sc.site_id = g.site_id
    AND sc.sku_id  = g.sku_id
    AND CAST(g.event_dt AS date) >= sc.effective_start_dt
    AND CAST(g.event_dt AS date) <= ISNULL(sc.effective_end_dt,'9999-12-31')

WHERE g.quality_flag = 0

GROUP BY
    g.site_id,
    DATEFROMPARTS(YEAR(g.event_dt), MONTH(g.event_dt), 1);
GO
-- ============================================================
-- VERSION SEED
-- ============================================================

INSERT INTO dbo.versions (version_number, install_dt)
SELECT 1.08, GETDATE()
WHERE NOT EXISTS (SELECT 1 FROM dbo.versions WHERE version_number = 1.08);
GO