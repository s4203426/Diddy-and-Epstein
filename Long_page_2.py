import pyhtml
import navbar
import footer
import breadcrumb

def get_page_html(form_data):
    print("About to return Long_page_2 (Infection Data by Economic Status)")

    # ── Sanitise inputs ──────────────────────────────────────────────
    def safe_int(val):
        try: return str(int(val))
        except: return ""

    def safe_str(val):
        return ''.join(c for c in str(val) if c.isalnum())

    economy   = safe_int(form_data.get("economy",   [""])[0])
    inf_type  = safe_str(form_data.get("inf_type",  [""])[0])
    year      = safe_int(form_data.get("year",      [""])[0])
    view_type = form_data.get("view_type", ["country"])[0]
    display   = form_data.get("display",   ["table"])[0]
    if view_type not in ("country", "summary"): view_type = "country"
    if display   not in ("table",   "graph"):   display   = "table"

    default_sort = "economy" if view_type == "summary" else "metric"
    default_dir  = "asc"    if view_type == "summary" else "desc"
    sort = form_data.get("sort", [default_sort])[0]
    dir_ = form_data.get("dir",  [default_dir])[0]
    if dir_ not in ("asc", "desc"): dir_ = default_dir
    economy_rank = ("CASE e.phase "
                    "WHEN 'Low Income' THEN 1 "
                    "WHEN 'Lower Middle Income' THEN 2 "
                    "WHEN 'Upper Middle Income' THEN 3 "
                    "WHEN 'High Income' THEN 4 ELSE 5 END")
    lp2_sort_country = {"inf_type": "it.description", "country": "c.name",
                        "economy": economy_rank, "year": "id.year", "metric": "metric"}
    lp2_sort_summary = {"economy": economy_rank, "inf_type": "it.description",
                        "year": "id.year", "countries": "countries", "metric": "metric"}
    sort_map = lp2_sort_summary if view_type == "summary" else lp2_sort_country
    if sort not in sort_map: sort = "metric"
    order_by = f"ORDER BY {sort_map[sort]} {dir_.upper()}"

    try:    page = max(1, int(form_data.get("page", ["1"])[0]))
    except: page = 1
    per_page = 20
    offset   = (page - 1) * per_page

    # ── Dropdown options ─────────────────────────────────────────────
    economies = pyhtml.get_results_from_query("database/immunisation.db",
        "SELECT economyID, phase FROM Economy ORDER BY economyID")
    inf_types = pyhtml.get_results_from_query("database/immunisation.db",
        "SELECT id, description FROM Infection_Type ORDER BY description")
    years     = pyhtml.get_results_from_query("database/immunisation.db",
        "SELECT YearID FROM YearDate ORDER BY YearID DESC")

    # ── WHERE clause ─────────────────────────────────────────────────
    conds = []
    if economy:  conds.append(f"e.economyID = {economy}")
    if inf_type: conds.append(f"id.inf_type = '{inf_type}'")
    if year:     conds.append(f"id.year = {year}")
    where = ("WHERE " + " AND ".join(conds)) if conds else ""

    joins = """FROM InfectionData id
        JOIN Country c  ON id.country  = c.CountryID
        JOIN Economy e  ON c.economy   = e.economyID
        JOIN Infection_Type it ON id.inf_type = it.id
        LEFT JOIN CountryPopulation cp
            ON id.country = cp.country AND id.year = cp.year"""

    # ── Queries ──────────────────────────────────────────────────────
    if view_type == "summary":
        main_q = f"""
            SELECT e.phase, it.description, id.year,
                   COUNT(DISTINCT id.country) AS countries,
                   ROUND(AVG(CAST(id.cases AS FLOAT)
                         / NULLIF(cp.population,0) * 100000), 2) AS metric
            {joins} {where}
            GROUP BY e.economyID, id.inf_type, id.year
            {order_by}
            LIMIT {per_page} OFFSET {offset}"""
        count_q = f"""
            SELECT COUNT(*) FROM (
                SELECT e.economyID {joins} {where}
                GROUP BY e.economyID, id.inf_type, id.year)"""
        graph_axis_label = "Avg cases per 100,000 people"
    else:
        main_q = f"""
            SELECT it.description, c.name, e.phase, id.year,
                   ROUND(CAST(id.cases AS FLOAT)
                         / NULLIF(cp.population,0) * 100000, 2) AS metric
            {joins} {where}
            {order_by}
            LIMIT {per_page} OFFSET {offset}"""
        count_q = f"""
            SELECT COUNT(*)
            FROM InfectionData id
            JOIN Country c  ON id.country = c.CountryID
            JOIN Economy e  ON c.economy  = e.economyID
            JOIN Infection_Type it ON id.inf_type = it.id
            {where}"""
        graph_axis_label = "Cases per 100,000 people"

    no_filters = not form_data.get("applied", [""])[0]

    if no_filters:
        results    = []
        graph_data = []
        total      = 0
    else:
        results   = pyhtml.get_results_from_query("database/immunisation.db", main_q)
        count_res = pyhtml.get_results_from_query("database/immunisation.db", count_q)

        if display == "graph":
            if view_type == "summary":
                graph_all_q = f"""
                    SELECT e.phase, it.description, id.year,
                           COUNT(DISTINCT id.country) AS countries,
                           ROUND(AVG(CAST(id.cases AS FLOAT)
                                 / NULLIF(cp.population,0) * 100000), 2) AS metric
                    {joins} {where}
                    GROUP BY e.economyID, id.inf_type, id.year
                    {order_by}"""
            else:
                graph_all_q = f"""
                    SELECT it.description, c.name, e.phase, id.year,
                           ROUND(CAST(id.cases AS FLOAT)
                                 / NULLIF(cp.population,0) * 100000, 2) AS metric
                    {joins} {where}
                    {order_by}"""
            graph_all = pyhtml.get_results_from_query("database/immunisation.db", graph_all_q)
            graph_data = [(r[0], r[4]) for r in graph_all] if view_type == "summary" else [(r[1], r[4]) for r in graph_all]
        else:
            graph_data = []

        total = count_res[0][0] if count_res else 0

    total_pages = max(1, (total + per_page - 1) // per_page)

    # ── URL builder (all navigation is plain links — no JS) ──────────
    def url(vt=view_type, dp=display, p=1, eco=economy, it=inf_type, yr=year, s=sort, d=dir_):
        parts = []
        if eco: parts.append(f"economy={eco}")
        if it:  parts.append(f"inf_type={it}")
        if yr:  parts.append(f"year={yr}")
        parts += [f"view_type={vt}", f"display={dp}", f"page={p}", f"sort={s}", f"dir={d}", "applied=1"]
        return "/Long_page_2?" + "&".join(parts) + "#lp-anchor"

    def sort_hdr(label, col):
        return (f'<th>{label} '
                f'<a class="sort-btn" href="{url(p=1, s=col, d="asc")}">&#8593;</a>'
                f'<a class="sort-btn" href="{url(p=1, s=col, d="desc")}">&#8595;</a>'
                f'</th>')

    # ── Select options ───────────────────────────────────────────────
    def opt(val, label, current):
        sel = "selected" if str(val) == str(current) else ""
        return f'<option value="{val}" {sel}>{label}</option>'

    eco_opts = '<option value="">All Economic Phases</option>' + \
               "".join(opt(i, p, economy)  for i, p in economies)
    it_opts  = '<option value="">All Infection Types</option>'  + \
               "".join(opt(i, d, inf_type) for i, d in inf_types)
    yr_opts  = '<option value="">All Years</option>'            + \
               "".join(opt(y[0], y[0], year) for y in years)

    # ── Table ────────────────────────────────────────────────────────
    if view_type == "summary":
        thead = (f"<tr>{sort_hdr('Economic phase', 'economy')}{sort_hdr('Preventable disease', 'inf_type')}"
                 f"{sort_hdr('Year', 'year')}{sort_hdr('Countries', 'countries')}{sort_hdr('Avg cases per 100,000', 'metric')}</tr>")
        tbody = "".join(
            f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td>"
            f"<td>{r[3]}</td><td>{'N/A' if r[4] is None else f'{r[4]:.2f}'}</td></tr>"
            for r in results
        ) or '<tr><td colspan="5" class="no-data">No data — try adjusting your filters.</td></tr>'
    else:
        thead = (f"<tr>{sort_hdr('Preventable disease', 'inf_type')}{sort_hdr('Country', 'country')}"
                 f"{sort_hdr('Economic phase', 'economy')}{sort_hdr('Year', 'year')}{sort_hdr('Cases per 100,000 people', 'metric')}</tr>")
        tbody = "".join(
            f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td>"
            f"<td>{r[3]}</td><td>{'N/A' if r[4] is None else f'{r[4]:.2f}'}</td></tr>"
            for r in results
        ) or '<tr><td colspan="5" class="no-data">No data — try adjusting your filters.</td></tr>'

    table_html = (f'<table class="results-table">'
                  f'<thead>{thead}</thead><tbody>{tbody}</tbody></table>')

    # ── Pure HTML/CSS horizontal bar chart (no JS) ───────────────────
    def build_bar_chart(data, axis_label):
        if not data:
            return '<p class="no-data">No data to display.</p>'
        max_val = max((r[1] for r in data if r[1] is not None), default=1) or 1
        bars = ""
        for row in data:
            name = str(row[0])
            val  = round(row[1], 2) if row[1] is not None else 0
            pct  = round((val / max_val) * 100, 1)
            short = (name[:28] + "…") if len(name) > 28 else name
            bars += f"""
            <div class="bar-row">
                <span class="bar-label" title="{name}">{short}</span>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{pct}%"></div>
                </div>
                <span class="bar-value">{val:.2f}</span>
            </div>"""
        return (f'<p class="chart-axis-label">{axis_label}</p>'
                f'<div class="bar-chart">{bars}</div>')

    graph_html = build_bar_chart(graph_data, graph_axis_label)

    # ── Pagination (plain links) ──────────────────────────────────────
    start_n = offset + 1
    end_n   = min(offset + per_page, total)
    noun    = "records" if view_type == "summary" else "countries"

    def pbtn(p, text, active=False, disabled=False):
        if disabled: return f'<span class="page-btn disabled">{text}</span>'
        if active:   return f'<span class="page-btn active">{text}</span>'
        return f'<a href="{url(p=p)}" class="page-btn">{text}</a>'

    pg = pbtn(page - 1, "&#9664;", disabled=(page <= 1))
    if total_pages <= 7:
        for p in range(1, total_pages + 1):
            pg += pbtn(p, p, active=(p == page))
    else:
        for p in [1, 2]:
            pg += pbtn(p, p, active=(p == page))
        if page > 4:
            pg += '<span class="page-ellipsis">…</span>'
        for p in range(max(3, page - 1), min(total_pages - 1, page + 2)):
            pg += pbtn(p, p, active=(p == page))
        if page < total_pages - 3:
            pg += '<span class="page-ellipsis">…</span>'
        pg += pbtn(total_pages, total_pages, active=(page == total_pages))
    pg += pbtn(page + 1, "&#9654;", disabled=(page >= total_pages))

    pagination = (f'<div class="pagination">'
                  f'<span class="pg-info">Showing {start_n} to {end_n} of {total} {noun}</span>'
                  f'<div class="pg-btns">{pg}</div></div>') if display == "table" and not no_filters else ""

    # ── Button active states ──────────────────────────────────────────
    c_cls = "vbtn-filled btn-active" if view_type == "country" else "vbtn-filled"
    s_cls = "vbtn-outline btn-active" if view_type == "summary" else "vbtn-outline"
    t_cls = "tog-btn btn-active"      if display   == "table"   else "tog-btn"
    g_cls = "tog-btn btn-active"      if display   == "graph"   else "tog-btn"

    tname = ("Country-level Infection Data" if view_type == "country"
             else "Infection Summary by Economic Phase")

    if no_filters:
        results_block = """
        <div class="filter-placeholder">
            <div class="fp-icon">&#128269;</div>
            <p class="fp-title">No filters selected yet</p>
            <p class="fp-desc">Use the filters above to narrow the results, or just click
            <strong>Apply Filters</strong> to view all data.</p>
        </div>"""
    else:
        results_block = table_html if display == "table" else graph_html

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infection Data by Economic Status</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="breadcrumb.css">
    <link rel="stylesheet" href="Minh_page_1.css">
    <link rel="stylesheet" href="Long_page_2.css">
    <link rel="stylesheet" href="footer.css">
</head>
<body>

    {navbar.get_navbar()}

    <div class="lp2-wrapper">

        {breadcrumb.get_breadcrumb([("Home", "/"), ("Infection Data", "/Long_page_2"), ("Infection Data by Economic Status", "/Long_page_2")])}

        <!-- HEADER -->
        <div class="lp2-header">
            <div class="lp2-header-left">
                <h1 class="lp2-title">Infection Data by Economic Status</h1>
                <p class="lp2-desc">Explore infection cases of preventable diseases across countries
                by economic status. See which countries have higher or lower rates of diseases like
                measles, rubella, and polio, and compare trends between Low Income, Lower and Upper Middle Income, and
                High Income nations.</p>
            </div>
            <div class="hiw-box">
                <div class="hiw-heading">&#9432; How the page works</div>
                <p>Select an economic status, infection type and year to view infection data.
                Use filters and sorting to organize results or summarize by economic phase.</p>
                <div class="hiw-steps">
                    <p class="hiw-steps-title">Step-by-step guide</p>
                    <div class="hiw-steps-row">
                        <div class="hiw-step">
                            <div class="hiw-step-icon">&#9776;</div>
                            <div class="hiw-step-label">Choose View</div>
                        </div>
                        <span class="hiw-step-arrow">&#8594;</span>
                        <div class="hiw-step">
                            <div class="hiw-step-icon">
                                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"><circle cx="10" cy="10" r="7"/><line x1="15.5" y1="15.5" x2="21" y2="21"/></svg>
                            </div>
                            <div class="hiw-step-label">Set Filters</div>
                        </div>
                        <span class="hiw-step-arrow">&#8594;</span>
                        <div class="hiw-step">
                            <div class="hiw-step-icon">&#10003;</div>
                            <div class="hiw-step-label">Apply Filters</div>
                        </div>
                        <span class="hiw-step-arrow">&#8594;</span>
                        <div class="hiw-step">
                            <div class="hiw-step-icon">
                                <svg viewBox="0 0 24 24" width="20" height="20" fill="white"><rect x="2" y="13" width="5" height="8" rx="1"/><rect x="9.5" y="8" width="5" height="13" rx="1"/><rect x="17" y="4" width="5" height="17" rx="1"/></svg>
                            </div>
                            <div class="hiw-step-label">Explore Data</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- VIEW TYPE — plain links, styled as buttons -->
        <div class="view-type-row" id="lp-anchor">
            <div class="tooltip-wrap">
                <a href="{url(vt='country')}" class="vbtn {c_cls}">Country-level View</a>
                <div class="vbtn-tooltip">Choose <strong>"Country-level View"</strong> to see data for each country separately.</div>
            </div>
            <div class="tooltip-wrap">
                <a href="{url(vt='summary', eco='')}" class="vbtn {s_cls}">Summary View</a>
                <div class="vbtn-tooltip">Choose <strong>"Summary View"</strong> to see infection data summarised by economic phase.</div>
            </div>
        </div>

        <!-- FILTER BOX -->
        <form method="GET" action="/Long_page_2" class="filter-box">

            <!-- preserve current view/display when applying new filters -->
            <input type="hidden" name="view_type" value="{view_type}">
            <input type="hidden" name="display"   value="{display}">
            <input type="hidden" name="page"      value="1">
            <input type="hidden" name="applied"   value="1">

            <div class="filter-top">
                <h2 class="filter-title">Select Filters</h2>
            </div>

            <div class="filter-row">
                {'<div class="filter-group"><div class="filter-group-tooltip">Select an economic phase. Leave as <strong>All Economic Phases</strong> to include all.</div><label>Economic Phases</label><select name="economy">' + eco_opts + '</select></div>' if view_type == "country" else ''}
                <div class="filter-group">
                    <div class="filter-group-tooltip">Select an infection type. Leave as <strong>All Infection Types</strong> to include all.</div>
                    <label>Infection Type</label>
                    <select name="inf_type">{it_opts}</select>
                </div>
                <div class="filter-group">
                    <div class="filter-group-tooltip">Select a year. Leave as <strong>All Years</strong> to include all.</div>
                    <label>Year</label>
                    <select name="year">{yr_opts}</select>
                </div>
                <div class="filter-actions">
                    <button type="submit" class="apply-btn">Apply Filters</button>
                    <a href="/Long_page_2?view_type={view_type}#lp-anchor" class="clear-btn"><span class="clear-icon">&#8635;</span> Clear All</a>
                </div>
            </div>

        </form>

        <!-- RESULTS BOX -->
        <div class="results-box">
            <div class="results-top">
                <h2 class="results-title">{tname}</h2>
            </div>
            <!-- Display toggle — plain links -->
            {'<div class="display-toggle" style="margin-bottom:14px;"><a href="' + url(dp="table") + '" class="' + t_cls + '">&#9776; Table View</a><a href="' + url(dp="graph") + '" class="' + g_cls + '">&#9638; Graph View</a></div>' if not no_filters else ''}

            <div class="results-content">
                {results_block}
            </div>

            {pagination}
        </div>

    </div>

    {footer.get_footer()}

</body>
</html>"""
    return page_html
