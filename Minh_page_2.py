import pyhtml
import navbar
import footer
import pagination_bar

PER_PAGE = 30

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
    region_rows = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT RegionID, region FROM Region ORDER BY region"
    )
    nation_rows = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT CountryID, name, region FROM Country ORDER BY name"
    )

    # --- Get form values ---
    var_antigen  = form_data.get('var_antigen')
    var_year     = form_data.get('var_year')
    var_region   = form_data.get('var_region')
    var_nation   = form_data.get('var_nation')
    var_min_rate = form_data.get('var_min_rate')
    var_sort     = form_data.get('var_sort')
    var_page     = form_data.get('var_page')
    var_sort2    = form_data.get('var_sort2')

    sel_antigen  = var_antigen[0]  if var_antigen  else None
    sel_year     = var_year[0]     if var_year     else None
    sel_region   = var_region[0]   if var_region   else None
    sel_nation   = var_nation[0]   if var_nation   else None
    sel_min_rate = var_min_rate[0] if var_min_rate else ''
    sel_sort     = var_sort[0]     if var_sort     else 'coverage_desc'
    sel_page     = int(var_page[0]) if var_page    else 1
    sel_sort2    = var_sort2[0]    if var_sort2     else 'nations_desc'

    # Auto-detect region from nation if nation selected but no region
    if sel_nation and not sel_region:
        sel_region = next((str(row[2]) for row in nation_rows if str(row[0]) == sel_nation), None)

    # Filter nation list by selected region
    if sel_region:
        filtered_nation_rows = [row for row in nation_rows if str(row[2]) == sel_region]
    else:
        filtered_nation_rows = nation_rows

    # --- Build base URLs ---
    base_params = []
    if sel_antigen:  base_params.append('var_antigen='  + sel_antigen)
    if sel_year:     base_params.append('var_year='     + sel_year)
    if sel_region:   base_params.append('var_region='   + sel_region)
    if sel_nation:   base_params.append('var_nation='   + sel_nation)
    if sel_min_rate: base_params.append('var_min_rate=' + sel_min_rate)
    filter_str = '&'.join(base_params) + ('&' if base_params else '')

    # Sort links for table 1 headers (preserves sort2)
    sort1_base    = '/Minh_page_2?' + filter_str + 'var_sort2=' + sel_sort2 + '&'
    # Sort links for table 2 headers (preserves sort1)
    sort2_base    = '/Minh_page_2?' + filter_str + 'var_sort='  + sel_sort  + '&'
    # Pagination for table 1 (preserves both sorts)
    page_base_url = '/Minh_page_2?' + filter_str + 'var_sort=' + sel_sort + '&var_sort2=' + sel_sort2 + '&var_page='

    # --- Build results ---
    page_results  = []
    total_pages   = 1
    region_results = []

    if sel_antigen and sel_year:
        try:
            min_rate_val = float(sel_min_rate) if sel_min_rate else 0
        except ValueError:
            min_rate_val = 0

        where = ("v.antigen = '" + sel_antigen + "' AND v.year = " + sel_year +
                 " AND v.coverage != '' AND CAST(v.coverage AS REAL) >= " + str(min_rate_val))
        if sel_region:
            where += " AND r.RegionID = '" + sel_region + "'"
        if sel_nation:
            where += " AND c.CountryID = '" + sel_nation + "'"

        # Table 1: per-country
        raw = pyhtml.get_results_from_query(
            "database/immunisation.db",
            """SELECT c.name, a.name, v.year, r.region, CAST(v.coverage AS REAL)
            FROM Vaccination v
            JOIN Country c ON v.country = c.CountryID
            JOIN Region r ON c.region = r.RegionID
            JOIN Antigen a ON v.antigen = a.AntigenID
            WHERE """ + where + " ORDER BY CAST(v.coverage AS REAL) DESC"
        )
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

        total_pages  = max(1, (len(ranked) + PER_PAGE - 1) // PER_PAGE)
        sel_page     = max(1, min(sel_page, total_pages))
        page_results = ranked[(sel_page - 1) * PER_PAGE : sel_page * PER_PAGE]

        # Table 2: per-region — LEFT JOIN to include regions with 0 nations
        antigen_name = next((row[1] for row in antigen_rows if str(row[0]) == sel_antigen), sel_antigen)
        raw2 = pyhtml.get_results_from_query(
            "database/immunisation.db",
            """SELECT r.region, COUNT(DISTINCT v.country) as nation_count
            FROM Region r
            LEFT JOIN Country c ON c.region = r.RegionID
            LEFT JOIN Vaccination v ON v.country = c.CountryID
                AND v.antigen = '""" + sel_antigen + """'
                AND v.year = """ + sel_year + """
                AND v.coverage != ''
                AND CAST(v.coverage AS REAL) >= """ + str(min_rate_val) + """
            GROUP BY r.RegionID ORDER BY nation_count DESC"""
        )
        # (rank, region, year, antigen_name, nation_count)
        ranked2 = [(i + 1, row[0], sel_year, antigen_name, row[1]) for i, row in enumerate(raw2)]

        sort_funcs2 = {
            'nations_desc': (lambda r: r[4], True),
            'nations_asc':  (lambda r: r[4], False),
            'region_asc':   (lambda r: str(r[1]), False),
            'region_desc':  (lambda r: str(r[1]), True),
            'antigen_asc':  (lambda r: str(r[3]), False),
            'antigen_desc': (lambda r: str(r[3]), True),
            'year_asc':     (lambda r: r[2], False),
            'year_desc':    (lambda r: r[2], True),
        }
        key_func2, reverse2 = sort_funcs2.get(sel_sort2, (lambda r: r[4], True))
        ranked2.sort(key=key_func2, reverse=reverse2)
        region_results = ranked2

    # --- Build HTML ---
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Data - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_2.css">
    <link rel="stylesheet" href="pagination_bar.css">
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
                        <select name="var_year" class="filter-select filter-select-narrow">
                            <option value="">--None--</option>"""

    for row in year_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_year == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[0]) + '</option>'

    page_html += """
                        </select>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Region</label>
                        <select name="var_region" class="filter-select filter-select-medium">
                            <option value="">--All--</option>"""

    for row in region_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_region == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[1]) + '</option>'

    page_html += """
                        </select>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Nation</label>
                        <select name="var_nation" class="filter-select filter-select-medium">
                            <option value="">--All--</option>"""

    for row in filtered_nation_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_nation == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[1]) + '</option>'

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

            <!-- TABLE 1: PER-COUNTRY -->
            <div class="results-box">
                <div class="results-header">
                    <h2 class="results-title">Results</h2>
                    <div class="sort-row">
                        <label class="sort-label">Sort by</label>
                        <select name="var_sort" class="sort-select">
                            <option value="coverage_desc" {"selected" if sel_sort == "coverage_desc" else ""}>Vaccination Rate &#8595;</option>
                            <option value="coverage_asc"  {"selected" if sel_sort == "coverage_asc"  else ""}>Vaccination Rate &#8593;</option>
                            <option value="nation_asc"    {"selected" if sel_sort == "nation_asc"    else ""}>Nation A&#8209;Z</option>
                            <option value="region_asc"    {"selected" if sel_sort == "region_asc"    else ""}>Region A&#8209;Z</option>
                        </select>
                        <button type="submit" class="btn-apply">Sort</button>
                    </div>
                </div>

                <h3 class="results-subtitle">Number of Countries Meeting Vaccination Rate Threshold</h3>

                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Nation <a class="sort-btn" href="{sort1_base}var_sort=nation_asc">&#8593;</a><a class="sort-btn" href="{sort1_base}var_sort=nation_desc">&#8595;</a></th>
                            <th>Antigen <a class="sort-btn" href="{sort1_base}var_sort=antigen_asc">&#8593;</a><a class="sort-btn" href="{sort1_base}var_sort=antigen_desc">&#8595;</a></th>
                            <th>Year <a class="sort-btn" href="{sort1_base}var_sort=year_asc">&#8593;</a><a class="sort-btn" href="{sort1_base}var_sort=year_desc">&#8595;</a></th>
                            <th>Region <a class="sort-btn" href="{sort1_base}var_sort=region_asc">&#8593;</a><a class="sort-btn" href="{sort1_base}var_sort=region_desc">&#8595;</a></th>
                            <th>Vaccination Rate <a class="sort-btn" href="{sort1_base}var_sort=coverage_asc">&#8593;</a><a class="sort-btn" href="{sort1_base}var_sort=coverage_desc">&#8595;</a></th>
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

    page_html += '</tbody></table>'
    page_html += pagination_bar.get_pagination_bar(sel_page, total_pages, page_base_url)
    page_html += '</div>'

    # TABLE 2: PER-REGION
    page_html += f"""
            <div class="results-box">
                <div class="results-header">
                    <h2 class="results-title">Countries Meeting Vaccination Rate Threshold By Region</h2>
                    <div class="sort-row">
                        <label class="sort-label">Sort by</label>
                        <select name="var_sort2" class="sort-select">
                            <option value="nations_desc" {"selected" if sel_sort2 == "nations_desc" else ""}># Nations &#8595;</option>
                            <option value="nations_asc"  {"selected" if sel_sort2 == "nations_asc"  else ""}># Nations &#8593;</option>
                            <option value="region_asc"   {"selected" if sel_sort2 == "region_asc"   else ""}>Region A&#8209;Z</option>
                        </select>
                        <button type="submit" class="btn-apply">Sort</button>
                    </div>
                </div>

                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Region <a class="sort-btn" href="{sort2_base}var_sort2=region_asc">&#8593;</a><a class="sort-btn" href="{sort2_base}var_sort2=region_desc">&#8595;</a></th>
                            <th>Year <a class="sort-btn" href="{sort2_base}var_sort2=year_asc">&#8593;</a><a class="sort-btn" href="{sort2_base}var_sort2=year_desc">&#8595;</a></th>
                            <th>Antigen <a class="sort-btn" href="{sort2_base}var_sort2=antigen_asc">&#8593;</a><a class="sort-btn" href="{sort2_base}var_sort2=antigen_desc">&#8595;</a></th>
                            <th>Number of Nations <a class="sort-btn" href="{sort2_base}var_sort2=nations_asc">&#8593;</a><a class="sort-btn" href="{sort2_base}var_sort2=nations_desc">&#8595;</a></th>
                        </tr>
                    </thead>
                    <tbody>"""

    if region_results:
        for row in region_results:
            page_html += '<tr>'
            page_html += '<td>' + str(row[0]) + '</td>'
            page_html += '<td>' + str(row[1]) + '</td>'
            page_html += '<td>' + str(row[2]) + '</td>'
            page_html += '<td>' + str(row[3]) + '</td>'
            page_html += '<td>' + str(row[4]) + '</td>'
            page_html += '</tr>'
    else:
        page_html += '<tr><td colspan="5" class="no-results">Select filters above and click Apply Filters to see results.</td></tr>'

    page_html += f"""
                    </tbody>
                </table>
            </div>

        </form>
    </section>

    {footer.get_footer()}

</body>
</html>
"""
    return page_html
