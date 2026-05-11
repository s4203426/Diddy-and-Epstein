import pyhtml
import navbar
import footer

PER_PAGE = 30

def get_page_numbers(current, total):
    if total <= 7:
        return list(range(1, total + 1))
    pages = sorted({1, total, current,
                    max(1, current - 1), min(total, current + 1)})
    result = []
    prev = 0
    for p in pages:
        if p - prev > 1:
            result.append('...')
        result.append(p)
        prev = p
    return result

def get_page_html(form_data):
    print("About to return Minh_Page_2")

    # --- Query dropdown data ---
    antigen_rows = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT AntigenID, name FROM Antigen ORDER BY name"
    )
    year_rows = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT DISTINCT year FROM Vaccination ORDER BY year DESC"
    )

    # --- Get form values ---
    var_antigen  = form_data.get('var_antigen')
    var_year     = form_data.get('var_year')
    var_min_rate = form_data.get('var_min_rate')
    var_sort     = form_data.get('var_sort')
    var_page     = form_data.get('var_page')

    sel_antigen  = var_antigen[0]  if var_antigen  else None
    sel_year     = var_year[0]     if var_year     else None
    sel_min_rate = var_min_rate[0] if var_min_rate else ''
    sel_sort     = var_sort[0]     if var_sort     else 'coverage_desc'
    sel_page     = int(var_page[0]) if var_page else 1

    # --- Build base URL for header sort links (no sort, no page param) ---
    base_params = []
    if sel_antigen:  base_params.append('var_antigen='  + sel_antigen)
    if sel_year:     base_params.append('var_year='     + sel_year)
    if sel_min_rate: base_params.append('var_min_rate=' + sel_min_rate)
    base_url = '/Minh_page_2?' + '&'.join(base_params) + ('&' if base_params else '')

    # --- Build page base URL for pagination links (preserves sort) ---
    page_base_url = base_url + 'var_sort=' + sel_sort + '&var_page='

    # --- Build results ---
    results      = []
    page_results = []
    total_pages  = 1

    if sel_antigen and sel_year:
        try:
            min_rate_val = float(sel_min_rate) if sel_min_rate else 0
        except ValueError:
            min_rate_val = 0

        query = """SELECT c.name, a.name, v.year, r.region, CAST(v.coverage AS REAL)
        FROM Vaccination v
        JOIN Country c ON v.country = c.CountryID
        JOIN Region r ON c.region = r.RegionID
        JOIN Antigen a ON v.antigen = a.AntigenID
        WHERE v.antigen = '""" + sel_antigen + """'
        AND v.year = """ + sel_year + """
        AND v.coverage != ''
        AND CAST(v.coverage AS REAL) >= """ + str(min_rate_val) + """
        ORDER BY CAST(v.coverage AS REAL) DESC"""

        raw    = pyhtml.get_results_from_query("database/immunisation.db", query)
        ranked = [(i + 1, row[0], row[1], row[2], row[3], row[4]) for i, row in enumerate(raw)]

        sort_funcs = {
            'coverage_desc': (lambda r: r[5], True),
            'coverage_asc':  (lambda r: r[5], False),
            'nation_asc':    (lambda r: str(r[1]), False),
            'nation_desc':   (lambda r: str(r[1]), True),
            'antigen_asc':   (lambda r: str(r[2]), False),
            'antigen_desc':  (lambda r: str(r[2]), True),
            'year_asc':      (lambda r: r[3], False),
            'year_desc':     (lambda r: r[3], True),
            'region_asc':    (lambda r: str(r[4]), False),
            'region_desc':   (lambda r: str(r[4]), True),
        }
        key_func, reverse = sort_funcs.get(sel_sort, (lambda r: r[5], True))
        ranked.sort(key=key_func, reverse=reverse)
        results = ranked

        total_pages = max(1, (len(results) + PER_PAGE - 1) // PER_PAGE)
        sel_page    = max(1, min(sel_page, total_pages))
        start_idx   = (sel_page - 1) * PER_PAGE
        page_results = results[start_idx:start_idx + PER_PAGE]

    # --- Build HTML ---
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Data - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_2.css">
    <link rel="stylesheet" href="footer.css">
</head>
<body>

    {navbar.get_navbar()}

    <!-- PAGE HEADER -->
    <section class="page-header">
        <h1 class="page-title">Data Visualization of Vaccination Rate</h1>
        <div class="page-intro">
            <p class="page-description">
                Identify the top countries with the largest improvement in vaccination
                rates between two selected years for a specific antigen type.
            </p>
            <div class="help-box">
                <div class="help-box-title">How the page works</div>
                <p class="help-box-text">
                    Select an Antigen, Year and Minimum Rate to see the
                    Number of Countries Meeting Vaccination Rate Threshold
                    and Countries Meeting Vaccination Rate Threshold
                    By Region - X Antigen.
                </p>
            </div>
        </div>
    </section>

    <!-- FILTER + RESULTS -->
    <section class="filter-section">
        <form action="/Minh_page_2" method="GET">

            <!-- FILTER BOX -->
            <div class="filter-box">
                <h2 class="filter-title">Select Filters</h2>
                <div class="filter-row">

                    <div class="filter-field">
                        <label class="filter-label">Antigen</label>
                        <select name="var_antigen" class="filter-select">
                            <option value="">--None--</option>"""

    for row in antigen_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_antigen == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[1]) + '</option>'

    page_html += """
                        </select>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Year</label>
                        <select name="var_year" class="filter-select">
                            <option value="">--None--</option>"""

    for row in year_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_year == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[0]) + '</option>'

    page_html += f"""
                        </select>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Minimum Rate (X%)</label>
                        <input type="number" name="var_min_rate" class="filter-input"
                               placeholder="e.g. 80" min="0" max="200"
                               value="{sel_min_rate}">
                    </div>

                    <div class="filter-buttons">
                        <button type="submit" class="btn-apply">Apply Filters</button>
                        <a href="/Minh_page_2" class="btn-clear">&#x21BB; Clear All</a>
                    </div>

                </div>
            </div>

            <!-- RESULTS BOX -->
            <div class="results-box">
                <div class="results-header">
                    <h2 class="results-title">Results</h2>
                    <div class="sort-row">
                        <label class="sort-label">Sort by</label>
                        <select name="var_sort" class="sort-select" onchange="this.form.submit()">
                            <option value="coverage_desc" {"selected" if sel_sort == "coverage_desc" else ""}>Vaccination Rate &#8595;</option>
                            <option value="coverage_asc"  {"selected" if sel_sort == "coverage_asc"  else ""}>Vaccination Rate &#8593;</option>
                            <option value="nation_asc"    {"selected" if sel_sort == "nation_asc"    else ""}>Nation A&#8209;Z</option>
                            <option value="region_asc"    {"selected" if sel_sort == "region_asc"    else ""}>Region A&#8209;Z</option>
                        </select>
                    </div>
                </div>

                <h3 class="results-subtitle">Number of Countries Meeting Vaccination Rate Threshold</h3>

                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Nation <a class="sort-btn" href="{base_url}var_sort=nation_asc">&#8593;</a><a class="sort-btn" href="{base_url}var_sort=nation_desc">&#8595;</a></th>
                            <th>Antigen <a class="sort-btn" href="{base_url}var_sort=antigen_asc">&#8593;</a><a class="sort-btn" href="{base_url}var_sort=antigen_desc">&#8595;</a></th>
                            <th>Year <a class="sort-btn" href="{base_url}var_sort=year_asc">&#8593;</a><a class="sort-btn" href="{base_url}var_sort=year_desc">&#8595;</a></th>
                            <th>Region <a class="sort-btn" href="{base_url}var_sort=region_asc">&#8593;</a><a class="sort-btn" href="{base_url}var_sort=region_desc">&#8595;</a></th>
                            <th>Vaccination Rate <a class="sort-btn" href="{base_url}var_sort=coverage_asc">&#8593;</a><a class="sort-btn" href="{base_url}var_sort=coverage_desc">&#8595;</a></th>
                        </tr>
                    </thead>
                    <tbody>"""

    if page_results:
        for row in page_results:
            page_html += '<tr>'
            page_html += '<td>' + str(row[0]) + '</td>'
            page_html += '<td>' + str(row[1]) + '</td>'
            page_html += '<td>' + str(row[2]) + '</td>'
            page_html += '<td>' + str(row[3]) + '</td>'
            page_html += '<td>' + str(row[4]) + '</td>'
            page_html += '<td>' + str(round(row[5], 1)) + '%</td>'
            page_html += '</tr>'
    else:
        page_html += '<tr><td colspan="6" class="no-results">Select filters above and click Apply Filters to see results.</td></tr>'

    page_html += """
                    </tbody>
                </table>"""

    # --- Pagination bar ---
    if total_pages > 1:
        page_nums = get_page_numbers(sel_page, total_pages)

        prev_url = page_base_url + str(max(1, sel_page - 1))
        next_url = page_base_url + str(min(total_pages, sel_page + 1))

        page_html += f"""
                <div class="pagination">
                    <span class="pagination-info">Showing {sel_page} of {total_pages} pages</span>
                    <div class="pagination-controls">
                        <a class="page-btn {"page-btn-disabled" if sel_page == 1 else ""}" href="{prev_url}">&#8249;</a>"""

        for p in page_nums:
            if p == '...':
                page_html += '<span class="page-ellipsis">...</span>'
            else:
                active = 'page-btn-active' if p == sel_page else ''
                page_html += '<a class="page-btn ' + active + '" href="' + page_base_url + str(p) + '">' + str(p) + '</a>'

        page_html += f"""
                        <a class="page-btn {"page-btn-disabled" if sel_page == total_pages else ""}" href="{next_url}">&#8250;</a>
                    </div>
                </div>"""

    page_html += f"""
            </div>

        </form>
    </section>

    {footer.get_footer()}

</body>
</html>
"""
    return page_html
