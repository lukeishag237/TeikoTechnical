## To Run:
First run
    python load_data.py
to create the .db file
Then run 
    python app.py
which launches a server on your local machine. To access the application, go
to any browser app (tested in google chrome) and access http://127.0.0.1:5000

## Requirements
- Python 3.10+
- Flask
- Pandas
- SQLite3 (built‑in)
- Plotly (for boxplots)
- Chart.js (for bar charts)


## Answers for requested questions:
The first page you will see has the summary table as described by part 2.
Aside from the summary table, the menu bar at the top of the page has tabs for the following:
Statistical Analysis (part 3): Bar plot and associated significance stats
Data Subset Analysis (part 4): the associated sums requested by part 4 of the analysis
Subset Search: a page with fields for all associated variables included in each sample line.
    Ex. if we select, Condition: melanoma, Treatment:miraclib, Sample Type: PBMC, Time From Treatment Start: 0
    you will get the table view of the subset of patients that corresponds to part 4 for inspection or export.


## schema.sql
5 tables organized in 3 'levels', creating a trident like shape: Project, Treatment 
and Condition -> Subject -> Sample, where each level maps to the level below
(Each subject is in one project, has one condition, and received one treatment, each 
sample maps to a subject id)

Project - Maps project strings to integer identifiers. This will save space
and time when querying or filtering by project name.

Treatment - Maps treatments to integers, saving time and space; good for querying 
by treatment.

Condition - Maps conditions to integers, saving time and space; good for querying 
by condition.

Subject - Maps subject 'codes' (string) to an integer identifier, along with 
all of their specific data. Saves space and time when querying by subject or
by subject level identifiers (age,sex,etc.)

Sample - Maps each sample to an integer for increased query speed and stores all
sample level data (response, cell counts, etc.).

Project, Treatment, and Condition tables help scalability. They are rather useless for small 
datasets but will improve funcionality as data grows.

## load_data.py
hard coded to pull all the data from cell-count.csv and create a cell-count.db file

## app.py
The main script for this task.
Runs the Flask backend for the dashboard. It loads the SQLite database, provides a helper 
function for running SQL queries, defines all API endpoints used by the frontend, and serves
the HTML templates for each page (templates located in /templates/). The file handles three 
main tasks: connecting to the database, exposing JSON endpoints for summaries and custom queries,
and rendering the dashboard pages (/, /stats, /queries, /search). It depends on Flask for routing, 
SQLite3 for storage, and Pandas for filtering and summarizing query results.

## Analytics Rationale
The Mann–Whitney U test is used because immune cell percentages are not guaranteed
to be normally distributed.
