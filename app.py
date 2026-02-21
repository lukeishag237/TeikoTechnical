from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd

DB = "cell-count.db"

app = Flask(__name__)

def query_db(sql, params=()):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

@app.route("/")
def summary_page():
    return render_template("summary.html")

@app.route("/api/summary")
def api_summary():
    sql = """
    SELECT
        Samples.sample_code,
        Subjects.subject_code,
        Samples.b_cell,
        Samples.cd4_t_cell,
        Samples.cd8_t_cell,
        Samples.nk_cell,
        Samples.monocyte
    FROM Samples
    JOIN Subjects ON Samples.subject_id = Subjects.subject_id;
    """

    df = query_db(sql)

    # Compute total count per sample
    df["total_count"] = (
        df["b_cell"] +
        df["cd4_t_cell"] +
        df["cd8_t_cell"] +
        df["nk_cell"] +
        df["monocyte"]
    )

    # Melt into long format
    long_df = df.melt(
        id_vars=["sample_code", "subject_code", "total_count"],
        value_vars=["b_cell", "cd4_t_cell", "cd8_t_cell", "nk_cell", "monocyte"],
        var_name="population",
        value_name="count"
    )

    # Compute percentage
    long_df["percentage"] = (long_df["count"] / long_df["total_count"]) * 100

    return long_df.to_dict(orient="records")


@app.route("/stats")
def stats_page():
    return render_template("stats.html")

@app.route("/api/stats")
def api_stats():
    sql = """
    SELECT 
        Samples.sample_code,
        Samples.sample_type,
        Samples.response,
        Samples.b_cell,
        Samples.cd8_t_cell,
        Samples.cd4_t_cell,
        Samples.nk_cell,
        Samples.monocyte,
        Treatments.treatment_name,
        Conditions.condition_name
    FROM Samples
    JOIN Subjects ON Samples.subject_id = Subjects.subject_id
    JOIN Treatments ON Subjects.treatment_id = Treatments.treatment_id
    JOIN Conditions ON Subjects.condition_id = Conditions.condition_id
    """
    df = query_db(sql)

    # Filter PBMC + melanoma + miraclib + valid response
    df = df[df["sample_type"] == "PBMC"]
    df["response"] = df["response"].astype(str).str.strip().str.lower()
    df = df[df["response"].isin(["yes", "no"])]
    df = df[df["condition_name"].str.lower() == "melanoma"]
    df = df[df["treatment_name"].str.lower() == "miraclib"]

    # Melt + compute percentages
    long_df = df.melt(
        id_vars=["sample_code", "response"],
        value_vars=["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"],
        var_name="population",
        value_name="count"
    )
    totals = long_df.groupby("sample_code")["count"].sum().reset_index()
    totals = totals.rename(columns={"count": "total_count"})
    merged = long_df.merge(totals, on="sample_code")
    merged["percentage"] = merged["count"] / merged["total_count"] * 100

    return merged.to_json(orient="records")


@app.route("/search")
def search_page():
    return render_template("search.html")

@app.route("/api/search_options")
def api_search_options():
    sql = """
    SELECT DISTINCT
        Projects.project_name AS project,
        Subjects.subject_code AS subject,
        Conditions.condition_name AS condition,
        Subjects.age,
        Subjects.sex,
        Treatments.treatment_name AS treatment,
        Samples.response,
        Samples.sample_code AS sample,
        Samples.sample_type,
        Samples.time_from_start AS time_from_treatment_start
    FROM Samples
    JOIN Subjects ON Samples.subject_id = Subjects.subject_id
    JOIN Projects ON Subjects.project_id = Projects.project_id
    JOIN Treatments ON Subjects.treatment_id = Treatments.treatment_id
    JOIN Conditions ON Subjects.condition_id = Conditions.condition_id
    """

    df = query_db(sql)

    return {
        "projects": sorted(df["project"].dropna().unique().tolist()),
        "conditions": sorted(df["condition"].dropna().unique().tolist()),
        "ages": sorted(df["age"].dropna().unique().tolist()),
        "sexes": sorted(df["sex"].dropna().unique().tolist()),
        "treatments": sorted(df["treatment"].dropna().unique().tolist()),
        "responses": sorted(df["response"].dropna().unique().tolist()),
        "sample_types": sorted(df["sample_type"].dropna().unique().tolist()),
        "times": sorted(df["time_from_treatment_start"].dropna().unique().tolist())
    }


@app.route("/queries")
def queries_page():
    return render_template("queries.html")

@app.route("/api/baseline_melanoma")
def api_baseline_melanoma():
    sql = """
    SELECT 
        Projects.project_name,
        Subjects.subject_id,
        Subjects.sex,
        Samples.sample_code,
        Samples.response,
        Samples.time_from_start
    FROM Samples
    JOIN Subjects ON Samples.subject_id = Subjects.subject_id
    JOIN Treatments ON Subjects.treatment_id = Treatments.treatment_id
    JOIN Conditions ON Subjects.condition_id = Conditions.condition_id
    JOIN Projects ON Subjects.project_id = Projects.project_id
    WHERE 
        Conditions.condition_name = 'melanoma'
        AND Treatments.treatment_name = 'miraclib'
        AND Samples.sample_type = 'PBMC'
        AND Samples.time_from_start = 0
    """
    df = query_db(sql)

    # Compute aggregates
    result = {
        "samples_per_project": df.groupby("project_name")["sample_code"].count().to_dict(),
        "responders_vs_non": df.groupby("response")["subject_id"].nunique().to_dict(),
        "sex_counts": df.groupby("sex")["subject_id"].nunique().to_dict(),
        "raw": df.to_dict(orient="records")
    }

    return jsonify(result)

@app.route("/api/custom_query")
def api_custom_query():
    import flask
    args = flask.request.args

    # Build WHERE clauses dynamically
    conditions = []
    params = []

    for field in ["project", "subject", "condition", "age", "sex",
                  "treatment", "response", "sample", "sample_type",
                  "time_from_treatment_start"]:
        if args.get(field):
            conditions.append(f"{field} = ?")
            params.append(args.get(field))

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    sql = f"""
    SELECT *
    FROM raw_csv_view
    {where_clause}
    """

    df = query_db(sql, params)
    return df.to_json(orient="records")

@app.route("/api/subset_summary")
def api_subset_summary():
    sql = """
    SELECT
        Projects.project_name AS project,
        Subjects.subject_code AS subject,
        Subjects.sex,
        Samples.response,
        Samples.sample_code
    FROM Samples
    JOIN Subjects ON Samples.subject_id = Subjects.subject_id
    JOIN Projects ON Subjects.project_id = Projects.project_id
    JOIN Treatments ON Subjects.treatment_id = Treatments.treatment_id
    JOIN Conditions ON Subjects.condition_id = Conditions.condition_id
    WHERE
        Conditions.condition_name = 'melanoma'
        AND Samples.sample_type = 'PBMC'
        AND Treatments.treatment_name = 'miraclib'
        AND Samples.time_from_start = 0
    """

    df = query_db(sql)

    # Compute summaries
    samples_per_project = df.groupby("project")["sample_code"].nunique().to_dict()
    responders = df[df["response"] == "yes"]["subject"].nunique()
    nonresponders = df[df["response"] == "no"]["subject"].nunique()
    males = df[df["sex"] == "M"]["subject"].nunique()
    females = df[df["sex"] == "F"]["subject"].nunique()

    return {
        "samples_per_project": samples_per_project,
        "responders": responders,
        "nonresponders": nonresponders,
        "males": males,
        "females": females
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
