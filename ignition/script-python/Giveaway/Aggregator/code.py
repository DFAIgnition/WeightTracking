import system
import sys

LOGGER_NAME = "Weight_Giveaway"


# ============================================================
# Helper Logging Wrapper
# ============================================================

def logDebug(msg):
    CORE_P.Utils.logger(LOGGER_NAME, msg, level='Debug', active=True)

def logInfo(msg):
    CORE_P.Utils.logger(LOGGER_NAME, msg, level='Info', active=True)

def logWarn(msg):
    CORE_P.Utils.logger(LOGGER_NAME, msg, level='Warn', active=True)

def logError(msg):
    CORE_P.Utils.logger(LOGGER_NAME, msg, level='Error', active=True)


# ============================================================
# 1) Get Enabled Giveaway Configurations
# ============================================================

def getEnabledGiveawayConfigs():

    logDebug("Loading giveaway configurations")

    ds = system.db.runNamedQuery("Weight_Q/Giveaway/getGiveawayConfigs", {})

    if ds is None or ds.getRowCount() == 0:
        logWarn("No giveaway configurations found")
        return []

    configs = []

    for i in range(ds.getRowCount()):

        cfg = {
            "giveaway_config_id": ds.getValueAt(i, "giveaway_config_id"),
            "site_id":            ds.getValueAt(i, "site_id"),
            "line_id":            ds.getValueAt(i, "line_id"),
            "filler_id":          ds.getValueAt(i, "filler_id"),
            "use_campaign_id":    ds.getValueAt(i, "use_campaign_id"),

            "jobid_tag":          ds.getValueAt(i, "jobid_tag"),
            "recipe_tag":         ds.getValueAt(i, "recipe_tag"),
            "weight_target_tag":  ds.getValueAt(i, "weight_target_tag"),
            "weight_actual_tag":  ds.getValueAt(i, "weight_actual_tag"),

            "max_delta_grams":    ds.getValueAt(i, "max_delta_grams"),
        }

        cfg["fq_job_tag"]    = CORE_P.Tags.getFullyQualifiedTagName(cfg["jobid_tag"])
        cfg["fq_recipe_tag"] = CORE_P.Tags.getFullyQualifiedTagName(cfg["recipe_tag"])
        cfg["fq_target_tag"] = CORE_P.Tags.getFullyQualifiedTagName(cfg["weight_target_tag"])
        cfg["fq_actual_tag"] = CORE_P.Tags.getFullyQualifiedTagName(cfg["weight_actual_tag"])

        cfg["recipe_col"] = cfg["recipe_tag"].split("]", 1)[-1]
        cfg["target_col"] = cfg["weight_target_tag"].split("]", 1)[-1]
        cfg["actual_col"] = cfg["weight_actual_tag"].split("]", 1)[-1]

        configs.append(cfg)

    logDebug("Loaded %s giveaway configurations" % len(configs))

    return configs


# ============================================================
# 2) Query Tag History
# ============================================================

def getHistoryForConfig(config, start_dt, end_dt, interval_seconds=60):

    start_dt = CORE_P.Time.adjustTimestamp(start_dt, rounding='minutedown')
    end_dt   = CORE_P.Time.adjustTimestamp(end_dt,   rounding='minutedown')

    logDebug(
        "Query history line=%s filler=%s start=%s end=%s"
        % (config["line_id"], config["filler_id"], start_dt, end_dt)
    )

    return system.tag.queryTagHistory(
        paths=[
            config["fq_job_tag"],
            config["fq_recipe_tag"],
            config["fq_target_tag"],
            config["fq_actual_tag"]
        ],
        startDate=start_dt,
        endDate=end_dt,
        intervalSeconds=interval_seconds,
        aggregationMode="LastValue",
        returnFormat="Wide",
        ignoreBadQuality=True,
        includeBoundingValues=True,
        noInterpolation=False
    )


# ============================================================
# 3) Process History
# ============================================================

def processHistoryDataset(config, ds):

    if ds is None or ds.getRowCount() == 0:
        return []

    recipe_col = config["recipe_col"]
    target_col = config["target_col"]
    actual_col = config["actual_col"]

    time_col = "t_stamp"
    try:
        ds.getValueAt(0, time_col)
    except:
        time_col = "timestamp"

    max_delta = float(config["max_delta_grams"])

    rows = []

    last_target        = None
    last_actual        = None
    last_recipe        = None
    last_ts            = None
    last_booked_target = None
    last_booked_actual = None

    rc = ds.getRowCount()

    for r in range(rc):

        ts = ds.getValueAt(r, time_col)

        # Skip duplicate timestamps
        if last_ts is not None and ts == last_ts:
            continue
        last_ts = ts

        recipe     = ds.getValueAt(r, recipe_col)
        target_val = ds.getValueAt(r, target_col)
        actual_val = ds.getValueAt(r, actual_col)

        # Treat recipe=0 as no active job
        if recipe is not None and int(recipe) == 0:
            recipe = None

        # ------------------------------------------------
        # Job end / counter reset detected
        # Emit unbooked remainder before clearing state
        # ------------------------------------------------
        if recipe is None or target_val is None or actual_val is None:

            if last_target is not None and last_recipe is not None:

                booked_target    = last_booked_target if last_booked_target is not None else 0.0
                booked_actual    = last_booked_actual if last_booked_actual is not None else 0.0
                remainder_target = last_target - booked_target
                remainder_actual = last_actual - booked_actual

                if remainder_target > 0 or remainder_actual > 0:
                    rows.append({
                        "t_stamp":      last_ts,
                        "recipe":       last_recipe,
                        "delta_target": round(remainder_target, 3),
                        "delta_actual": round(remainder_actual, 3),
                        "quality_flag": 1
                    })
                    logDebug(
                        "Rollover remainder emitted ts=%s line=%s recipe=%s target=%s actual=%s"
                        % (last_ts, config["line_id"], last_recipe, remainder_target, remainder_actual)
                    )
                else:
                    logDebug(
                        "Job end/reset detected ts=%s line=%s recipe=%s – nothing unbooked"
                        % (ts, config["line_id"], last_recipe)
                    )

            last_target        = None
            last_actual        = None
            last_recipe        = None
            last_booked_target = None
            last_booked_actual = None
            continue

        try:
            cur_target = float(target_val)
            cur_actual = float(actual_val)
        except:
            continue

        # Seed baseline on first valid row
        if last_target is None:
            last_target        = cur_target
            last_actual        = cur_actual
            last_recipe        = recipe
            last_booked_target = cur_target
            last_booked_actual = cur_actual
            continue

        quality_flag = 0

        # ------------------------------------------------
        # Recipe change mid-stream
        # Emit unbooked remainder for old recipe, seed new
        # ------------------------------------------------
        if recipe != last_recipe:

            booked_target    = last_booked_target if last_booked_target is not None else 0.0
            booked_actual    = last_booked_actual if last_booked_actual is not None else 0.0
            remainder_target = last_target - booked_target
            remainder_actual = last_actual - booked_actual

            if remainder_target > 0 or remainder_actual > 0:
                rows.append({
                    "t_stamp":      last_ts,
                    "recipe":       last_recipe,
                    "delta_target": round(remainder_target, 3),
                    "delta_actual": round(remainder_actual, 3),
                    "quality_flag": 1
                })
                logDebug(
                    "Recipe change remainder ts=%s line=%s recipe=%s->%s target=%s actual=%s"
                    % (last_ts, config["line_id"], last_recipe, recipe, remainder_target, remainder_actual)
                )

            last_target        = cur_target
            last_actual        = cur_actual
            last_recipe        = recipe
            last_booked_target = cur_target
            last_booked_actual = cur_actual
            continue

        # ------------------------------------------------
        # TARGET: any drop = rollover
        # ------------------------------------------------
        if cur_target < last_target:
            delta_target = cur_target
            quality_flag = max(quality_flag, 1)
        else:
            delta_target = cur_target - last_target

        # ------------------------------------------------
        # ACTUAL: any drop = rollover
        # ------------------------------------------------
        if cur_actual < last_actual:
            delta_actual = cur_actual
            quality_flag = max(quality_flag, 1)
        else:
            delta_actual = cur_actual - last_actual

        # ------------------------------------------------
        # Spike guard — positive jumps only, never rollovers
        # ------------------------------------------------
        if quality_flag != 1:
            if delta_target > max_delta or delta_actual > max_delta:
                logWarn(
                    "Spike ts=%s line=%s target_delta=%s actual_delta=%s – zeroed"
                    % (ts, config["line_id"], delta_target, delta_actual)
                )
                delta_target = 0.0
                delta_actual = 0.0
                quality_flag = 2

        # ------------------------------------------------
        # Dead target tag — target=0 but actual ran
        # PLC was not writing target values; exclude from
        # giveaway calculations by flagging as bad data.
        # ------------------------------------------------
        if quality_flag != 1:
            if delta_target == 0 and delta_actual > 0:
                #logWarn(
                #    "Dead target tag ts=%s line=%s actual=%s – flagged bad"
                #    % (ts, config["line_id"], delta_actual)
                #)
                quality_flag = 2

        # Skip idle minutes — nothing moved at all
        if delta_target == 0 and delta_actual == 0:
            last_target = cur_target
            last_actual = cur_actual
            continue

        rows.append({
            "t_stamp":      ts,
            "recipe":       recipe,
            "delta_target": round(delta_target, 3),
            "delta_actual": round(delta_actual, 3),
            "quality_flag": quality_flag
        })

        # Always track last booked position
        last_booked_target = cur_target
        last_booked_actual = cur_actual
        last_target        = cur_target
        last_actual        = cur_actual
        last_recipe        = recipe

    return rows


# ============================================================
# 4) SKU Map
# ============================================================

def getSkuMapForRecipes(site_id, line_id, recipes):

    if not recipes:
        return {}

    recipes = list(recipes)

    placeholders = ",".join(["?"] * len(recipes))

    sql = """
    SELECT recipe_no, sku_id
    FROM weight.dbo.sku_map
    WHERE site_id = ?
      AND line_id = ?
      AND recipe_no IN ({})
      AND is_active = 1
    """.format(placeholders)

    args = [site_id, line_id] + recipes

    ds = system.db.runPrepQuery(sql, args)

    sku_map = {}

    for i in range(ds.getRowCount()):
        sku_map[ds.getValueAt(i, "recipe_no")] = ds.getValueAt(i, "sku_id")

    return sku_map


# ============================================================
# 5) Build Rows
# ============================================================

def buildRowsForInsert(config, processed_rows, sku_map):

    if not processed_rows:
        return []

    site_id   = config["site_id"]
    line_id   = config["line_id"]
    filler_id = config["filler_id"]

    rows = []

    for r in processed_rows:

        sku_id = sku_map.get(r["recipe"])
        if sku_id is None:
            logWarn(
                "No SKU mapping for recipe=%s line=%s – row skipped"
                % (r["recipe"], line_id)
            )
            continue

        rows.append({
            "event_dt":     r["t_stamp"],
            "site_id":      site_id,
            "line_id":      line_id,
            "filler_id":    filler_id,
            "sku_id":       sku_id,
            "campaign_id":  None,
            "delta_target": r["delta_target"],
            "delta_actual": r["delta_actual"],
            "quality_flag": r["quality_flag"]
        })

    return rows


# ============================================================
# 6) Deduplicate rows
# ============================================================

def deduplicateRows(rows):

    if not rows:
        return rows

    dedup   = {}
    removed = 0

    for r in rows:

        key = (
            r["event_dt"],
            r["line_id"],
            r["filler_id"],
            r["sku_id"],
            r["campaign_id"] or ""
        )

        if key in dedup:
            removed += 1

        dedup[key] = r

    if removed > 0:
        logWarn("Removed %s duplicate rows before MERGE" % removed)

    return list(dedup.values())


# ============================================================
# 7) Upsert Giveaway Rows
# ============================================================

def upsertGiveawayRows(rows, tx):

    if not rows:
        return 0

    logDebug("Upserting %s rows" % len(rows))

    sql = """
    MERGE weight.dbo.giveaway AS tgt
    USING (VALUES {}) AS src (
        event_dt, site_id, line_id, filler_id, sku_id, campaign_id,
        delta_target_grams, delta_actual_grams, quality_flag
    )
    ON  tgt.event_dt     = src.event_dt
    AND tgt.line_id      = src.line_id
    AND tgt.filler_key   = ISNULL(src.filler_id, -1)
    AND tgt.sku_id       = src.sku_id
    AND tgt.campaign_key = ISNULL(src.campaign_id, N'')

    WHEN MATCHED THEN
        UPDATE SET
            site_id            = src.site_id,
            campaign_id        = src.campaign_id,
            delta_target_grams = src.delta_target_grams,
            delta_actual_grams = src.delta_actual_grams,
            quality_flag       = src.quality_flag

    WHEN NOT MATCHED THEN
        INSERT (
            event_dt, site_id, line_id, filler_id, sku_id,
            campaign_id, delta_target_grams, delta_actual_grams, quality_flag
        )
        VALUES (
            src.event_dt, src.site_id, src.line_id, src.filler_id,
            src.sku_id, src.campaign_id,
            src.delta_target_grams, src.delta_actual_grams, src.quality_flag
        );
    """

    tpl = (
        "(CAST(? AS datetime2), CAST(? AS int), CAST(? AS int), CAST(? AS int),"
        " CAST(? AS int), CAST(? AS nvarchar(80)),"
        " CAST(? AS decimal(18,3)), CAST(? AS decimal(18,3)), CAST(? AS tinyint))"
    )

    placeholders = ",".join([tpl] * len(rows))

    args = []

    for r in rows:
        args.extend([
            r["event_dt"], r["site_id"], r["line_id"], r["filler_id"],
            r["sku_id"],   r["campaign_id"],
            r["delta_target"], r["delta_actual"], r["quality_flag"]
        ])

    system.db.runPrepUpdate(sql.format(placeholders), args, tx=tx)

    return len(rows)


# ============================================================
# Runtime Driver
# ============================================================

def runtimeGiveawayHistory(interval_seconds=60, batch_size=200, max_lookback_days=5, db="system"):

    start_time = system.date.now()

    logDebug("Giveaway runtime started")

    configs = getEnabledGiveawayConfigs()

    if not configs:
        logWarn("Runtime aborted: no giveaway configurations found")
        return {"rows_written": 0, "configs": 0}

    now           = system.date.now()
    min_start     = system.date.addDays(now, -max_lookback_days)
    total_written = 0

    tx = system.db.beginTransaction(database=db)

    try:

        for config in configs:

            line_id   = config["line_id"]
            filler_id = config["filler_id"]

            logDebug("Processing line=%s filler=%s" % (line_id, filler_id))

            state = system.db.runPrepQuery(
                """
                SELECT MAX(last_event_dt) AS last_event_dt
                FROM weight.dbo.giveaway_tag_state
                WHERE line_id  = ?
                  AND (filler_id = ? OR (filler_id IS NULL AND ? IS NULL))
                """,
                [line_id, filler_id, filler_id],
                tx=tx
            )

            start_dt = state.getValueAt(0, "last_event_dt")

            if start_dt is None:
                start_dt = min_start
            else:
                start_dt = system.date.addMinutes(start_dt, -1)

            warmup_start = system.date.addMinutes(start_dt, -5)

            history = getHistoryForConfig(config, warmup_start, now, interval_seconds)

            processed = processHistoryDataset(config, history)

            processed = [r for r in processed if r["t_stamp"] >= start_dt]

            if not processed:
                logDebug("No new rows for line=%s filler=%s" % (line_id, filler_id))
                continue

            recipes = {r["recipe"] for r in processed if r["recipe"]}

            sku_map = getSkuMapForRecipes(config["site_id"], line_id, recipes)

            rows = buildRowsForInsert(config, processed, sku_map)

            rows = deduplicateRows(rows)

            if not rows:
                continue

            for i in range(0, len(rows), batch_size):
                chunk   = rows[i:i + batch_size]
                written = upsertGiveawayRows(chunk, tx)
                total_written += written

            logDebug(
                "Line %s filler %s wrote %s rows"
                % (line_id, filler_id, len(rows))
            )

        system.db.commitTransaction(tx)

        duration = system.date.secondsBetween(start_time, system.date.now())

        logInfo(
            "Giveaway runtime completed | rows_written=%s configs=%s duration=%ss"
            % (total_written, len(configs), duration)
        )

    except Exception:

        logError("Runtime giveaway processing failed")
        system.db.rollbackTransaction(tx)
        raise

    finally:

        system.db.closeTransaction(tx)

    return {"rows_written": total_written, "configs": len(configs)}


# ============================================================
# Backfill Driver
# ============================================================

def backfillGiveawayHistory(start_dt, end_dt, interval_seconds=60, batch_size=200, db="system"):
    """
    Full flow:
      - configs
      - tag history (with 5-min warm-up window for baseline seeding)
      - deltas + rollover
      - bulk sku map
      - build rows
      - batch MERGE upsert

    Quality flags:
      0 = normal clean delta
      1 = rollover / job-end boundary remainder
      2 = bad data (spike, dead target tag, or unrecoverable read)
    """

    start_time = system.date.now()

    logDebug(
        "Giveaway backfill started | start=%s end=%s interval=%ss"
        % (start_dt, end_dt, interval_seconds)
    )

    configs = getEnabledGiveawayConfigs()

    if not configs:
        logWarn("Backfill aborted: no giveaway configurations found")
        return {"rows_written": 0, "configs": 0}

    total_written = 0
    total_configs = 0

    tx = system.db.beginTransaction(database=db)

    try:

        for config in configs:

            total_configs += 1

            line_id   = config["line_id"]
            filler_id = config["filler_id"]

            logDebug(
                "Backfill processing line=%s filler=%s"
                % (line_id, filler_id)
            )

            history_start = system.date.addMinutes(start_dt, -5)

            ds = getHistoryForConfig(config, history_start, end_dt, interval_seconds)

            if ds is None or ds.getRowCount() == 0:
                logDebug(
                    "No history returned for line=%s filler=%s"
                    % (line_id, filler_id)
                )
                continue

            logDebug(
                "History rows line=%s filler=%s rows=%s"
                % (line_id, filler_id, ds.getRowCount())
            )

            processed = processHistoryDataset(config, ds)

            if not processed:
                logDebug(
                    "No processed rows for line=%s filler=%s"
                    % (line_id, filler_id)
                )
                continue

            logDebug(
                "Processed rows line=%s filler=%s rows=%s"
                % (line_id, filler_id, len(processed))
            )

            processed = [r for r in processed if r["t_stamp"] >= start_dt]

            if not processed:
                logDebug(
                    "No rows after start filter line=%s filler=%s"
                    % (line_id, filler_id)
                )
                continue

            recipes = {r["recipe"] for r in processed if r["recipe"] is not None}

            sku_map = getSkuMapForRecipes(
                config["site_id"],
                config["line_id"],
                recipes
            )

            rows = buildRowsForInsert(config, processed, sku_map)

            rows = deduplicateRows(rows)

            if not rows:
                logDebug(
                    "No valid rows after SKU mapping line=%s filler=%s"
                    % (line_id, filler_id)
                )
                continue

            for i in range(0, len(rows), batch_size):
                chunk   = rows[i:i + batch_size]
                written = upsertGiveawayRows(chunk, tx)
                total_written += written

            logDebug(
                "Backfill line=%s filler=%s wrote %s rows"
                % (line_id, filler_id, len(rows))
            )

        system.db.commitTransaction(tx)

        duration = system.date.secondsBetween(start_time, system.date.now())

        logInfo(
            "Giveaway backfill completed | rows_written=%s configs=%s duration=%ss"
            % (total_written, total_configs, duration)
        )

    except Exception:

        logError("Giveaway backfill failed")
        system.db.rollbackTransaction(tx)
        raise

    finally:

        system.db.closeTransaction(tx)

    return {
        "rows_written": total_written,
        "configs":      total_configs
    }
    
# ============================================================
# Create SKU cost Each Month
# ============================================================

def CreateMonthlySKUCost():

	logger = system.util.getLogger("Giveaway.Aggregator")

	try:
		result = system.db.runNamedQuery("Weight_Q/Giveaway/CreateMonthlySKUCost")

		# Named Query should be type = Query and return rows_inserted
		rows_inserted = 0

		if result and len(result) > 0:
			rows_inserted = result[0].get("rows_inserted", 0)

		# Only log if something actually happened
		if rows_inserted > 0:
			logger.info(
				"SKU cost created for new month (rows={})".format(rows_inserted)
			)

	except Exception as e:
	    logger.error("Error in CreateMonthlySKUCost", e)