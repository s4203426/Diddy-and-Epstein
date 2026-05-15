import pyhtml
import navbar

def get_page_html(form_data):
    print("About to return Long_page_3 (Countries Above Average Infection Rate)")

    # ── Sanitise inputs ──────────────────────────────────────────────
    def safe_int(val):
        try: return str(int(val))
        except: return ""

    def safe_str(val):
        return ''.join(c for c in str(val) if c.isalnum())

    inf_type = safe_str(form_data.get("inf_type", [""])[0])
    year     = safe_int(form_data.get("year",     [""])[0])
    display  = form_data.get("display", ["table"])[0]
    if display not in ("table", "graph"): display = "table"

    sort = form_data.get("sort", ["rate"])[0]
    dir_ = form_data.get("dir",  ["desc"])[0]
    lp3_sort_map = {"country": "c.name", "inf_type": "it.description",
                    "rate": "rate", "year": "id.year"}
    if sort not in lp3_sort_map: sort = "rate"
    if dir_ not in ("asc", "desc"): dir_ = "desc"
    order_by = f"ORDER BY {lp3_sort_map[sort]} {dir_.upper()}"

    try:    page = max(1, int(form_data.get("page", ["1"])[0]))
    except: page = 1
    per_page = 10
    offset   = (page - 1) * per_page

    # ── Dropdown options ─────────────────────────────────────────────
    inf_types = pyhtml.get_results_from_query("database/immunisation.db",
        "SELECT id, description FROM Infection_Type ORDER BY description")
    years     = pyhtml.get_results_from_query("database/immunisation.db",
        "SELECT YearID FROM YearDate ORDER BY YearID DESC")

    # ── WHERE clause ─────────────────────────────────────────────────
    conds = []
    if inf_type: conds.append(f"id.inf_type = '{inf_type}'")
    if year:     conds.append(f"id.year = {year}")
    where = ("WHERE " + " AND ".join(conds)) if conds else ""

    base_joins = """FROM InfectionData id
        JOIN Country c ON id.country = c.CountryID
        JOIN Infection_Type it ON id.inf_type = it.id
        LEFT JOIN CountryPopulation cp
            ON id.country = cp.country AND id.year = cp.year"""

    # ── Global rate ──────────────────────────────────────────────────
    # Rebuild simpler where clause without Country/Infection_Type joins
    g_conds = []
    if inf_type: g_conds.append(f"id.inf_type = '{inf_type}'")
    if year:     g_conds.append(f"id.year = {year}")
    g_where = ("WHERE " + " AND ".join(g_conds)) if g_conds else ""

    global_rate_res = pyhtml.get_results_from_query("database/immunisation.db", f"""
        SELECT ROUND(
            CAST(SUM(id.cases) AS FLOAT) / NULLIF(SUM(cp.population), 0) * 100000, 2)
        FROM InfectionData id
        LEFT JOIN CountryPopulation cp ON id.country = cp.country AND id.year = cp.year
        {g_where}""")

    global_rate = global_rate_res[0][0] if global_rate_res and global_rate_res[0][0] else None

    # ── Countries above global average ───────────────────────────────
    if global_rate is not None:
        above_where_parts = list(conds) + [
            f"(CAST(id.cases AS FLOAT) / NULLIF(cp.population,0) * 100000) > {global_rate}"
        ]
        above_where = "WHERE " + " AND ".join(above_where_parts)
    else:
        above_where = where

    main_q = f"""
        SELECT c.name, it.description, id.year,
               ROUND(CAST(id.cases AS FLOAT) / NULLIF(cp.population,0) * 100000, 2) AS rate
        {base_joins}
        {above_where}
        {order_by}
        LIMIT {per_page} OFFSET {offset}"""

    count_q = f"""
        SELECT COUNT(*)
        {base_joins}
        {above_where}"""

    graph_q = f"""
        SELECT c.name,
               ROUND(CAST(id.cases AS FLOAT) / NULLIF(cp.population,0) * 100000, 2) AS rate
        {base_joins}
        {above_where}
        ORDER BY rate DESC LIMIT 15"""

    results    = pyhtml.get_results_from_query("database/immunisation.db", main_q)
    count_res  = pyhtml.get_results_from_query("database/immunisation.db", count_q)
    graph_data = pyhtml.get_results_from_query("database/immunisation.db", graph_q)

    total       = count_res[0][0] if count_res else 0
    total_pages = max(1, (total + per_page - 1) // per_page)

    # ── URL builder ──────────────────────────────────────────────────
    def url(dp=display, p=1, it=inf_type, yr=year, s=sort, d=dir_):
        parts = []
        if it: parts.append(f"inf_type={it}")
        if yr: parts.append(f"year={yr}")
        parts += [f"display={dp}", f"page={p}", f"sort={s}", f"dir={d}"]
        return "/Long_page_3?" + "&".join(parts)

    def sort_hdr(label, col):
        return (f'<th>{label} '
                f'<a class="sort-btn" href="{url(p=1, s=col, d="asc")}">&#8593;</a>'
                f'<a class="sort-btn" href="{url(p=1, s=col, d="desc")}">&#8595;</a>'
                f'</th>')

    # ── Select options ───────────────────────────────────────────────
    def opt(val, label, current):
        sel = "selected" if str(val) == str(current) else ""
        return f'<option value="{val}" {sel}>{label}</option>'

    it_opts = '<option value="">Select infection type</option>' + \
              "".join(opt(i, d, inf_type) for i, d in inf_types)
    yr_opts = '<option value="">Select year</option>' + \
              "".join(opt(y[0], y[0], year) for y in years)

    # ── Global rate card ─────────────────────────────────────────────
    it_label  = next((d for i, d in inf_types if i == inf_type), "...")
    yr_label  = year if year else "..."
    rate_disp = f"{global_rate:.2f}" if global_rate is not None else "—"

    global_card = f"""
    <div class="global-card">
        <div class="global-icon">&#127760;</div>
        <div class="global-info">
            <p class="global-heading">Global Infection Rate (per 100,000 people)</p>
            <p class="global-rate">{rate_disp}</p>
            <p class="global-meta">Infection type: {it_label} &nbsp;|&nbsp; Year: {yr_label}</p>
        </div>
    </div>"""

    # ── Table ────────────────────────────────────────────────────────
    thead = (f"<tr>{sort_hdr('Country', 'country')}{sort_hdr('Infection Type', 'inf_type')}"
             f"{sort_hdr('Infection per 100,000 people', 'rate')}{sort_hdr('Year', 'year')}</tr>")

    if results:
        tbody = "".join(
            f"<tr><td>{r[0]}</td><td>{r[1]}</td>"
            f"<td>{'N/A' if r[3] is None else f'{r[3]:.2f}'}</td>"
            f"<td>{r[2]}</td></tr>"
            for r in results)
    else:
        msg = ("Select an infection type and year, then click Apply Filters."
               if not inf_type and not year else
               "No countries exceed the global average for these filters.")
        tbody = f'<tr><td colspan="4" class="no-data">{msg}</td></tr>'

    table_html = (f'<table class="results-table">'
                  f'<thead>{thead}</thead><tbody>{tbody}</tbody></table>')

    # ── Pure CSS horizontal bar chart ────────────────────────────────
    def build_bar_chart(data, g_rate):
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
        avg_note = (f'<p class="chart-avg-note">Global average: <strong>{g_rate:.2f}</strong> per 100,000</p>'
                    if g_rate is not None else "")
        return (f'<p class="chart-axis-label">Infection per 100,000 people</p>'
                f'{avg_note}<div class="bar-chart">{bars}</div>')

    graph_html = build_bar_chart(graph_data, global_rate)

    # ── Pagination ───────────────────────────────────────────────────
    start_n = offset + 1
    end_n   = min(offset + per_page, total)

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
                  f'<span class="pg-info">Showing {start_n} to {end_n} of {total} countries</span>'
                  f'<div class="pg-btns">{pg}</div></div>') if total > 0 else ""

    # ── Toggle states ────────────────────────────────────────────────
    t_cls = "tog-btn btn-active" if display == "table" else "tog-btn"
    g_cls = "tog-btn btn-active" if display == "graph" else "tog-btn"
    results_block = table_html if display == "table" else graph_html

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Countries with Above Average Infection Rate</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_1.css">
    <link rel="stylesheet" href="Long_page_2.css">
    <link rel="stylesheet" href="Long_page_3.css">
</head>
<body>

    {navbar.get_navbar()}

    <div class="lp2-wrapper">

        <!-- HEADER -->
        <div class="lp2-header">
            <div class="lp2-header-left">
                <h1 class="lp2-title">Country with Above Average Infection Rate</h1>
                <p class="lp2-desc">View the global infection rate per 100,000 people and the
                countries with the reported infection rates higher than the global average for a
                selected infection type per year.</p>
            </div>
            <div class="hiw-box">
                <div class="hiw-heading">&#9432; How the page works</div>
                <p>Select an infection type and year to see the global average infection rate
                and the list of countries exceeding that average.</p>
            </div>
        </div>

        <!-- FILTER BOX -->
        <form method="GET" action="/Long_page_3" class="filter-box">
            <input type="hidden" name="display" value="{display}">
            <input type="hidden" name="page"    value="1">

            <div class="filter-top">
                <h2 class="filter-title">Select Filters</h2>
            </div>

            <div class="filter-row">
                <div class="filter-group">
                    <label>Infection Type</label>
                    <select name="inf_type">{it_opts}</select>
                </div>
                <div class="filter-group">
                    <label>Year</label>
                    <select name="year">{yr_opts}</select>
                </div>
                <div class="filter-actions lp3-actions">
                    <button type="submit" class="apply-btn">Apply Filters</button>
                    <a href="/Long_page_3" class="clear-btn">&#8635; Clear All</a>
                </div>
            </div>
        </form>

        <!-- RESULTS BOX -->
        <div class="results-box">
            <h2 class="results-title">Results</h2>

            {global_card}

            <div class="results-top" style="margin-top:20px;">
                <div class="display-toggle">
                    <a href="{url(dp='table')}" class="{t_cls}">&#9776; Table View</a>
                    <a href="{url(dp='graph')}" class="{g_cls}">&#9638; Graph View</a>
                </div>
            </div>

            <p class="table-label">Countries with above-average infection rate</p>

            <div class="results-content">
                {results_block}
            </div>

            {pagination}
        </div>

    </div>

</body>
</html>"""
    return page_html
