import pyhtml
import navbar
import footer
import pagination_bar

PER_PAGE = 30

def get_page_html(form_data):
    print("About to return Minh_Page_3")

    # Query dropdown data
    antigen_rows = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT AntigenID, name FROM Antigen ORDER BY name"
    )
    year_rows = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT DISTINCT year FROM Vaccination ORDER BY year ASC"
    )

    # Get form values
    var_antigen    = form_data.get('var_antigen')
    var_start_year = form_data.get('var_start_year')
    var_end_year   = form_data.get('var_end_year')
    var_top_n      = form_data.get('var_top_n')
    var_sort       = form_data.get('var_sort')
    var_page       = form_data.get('var_page')

    sel_antigen    = var_antigen[0]    if var_antigen    else None
    sel_start_year = var_start_year[0] if var_start_year else None
    sel_end_year   = var_end_year[0]   if var_end_year   else None
    sel_top_n      = var_top_n[0]      if var_top_n      else ''
    sel_sort       = var_sort[0]       if var_sort       else 'improvement_desc'
    sel_page       = int(var_page[0])  if var_page       else 1

    # Build base URLs
    base_params = []
    if sel_antigen:    base_params.append('var_antigen='    + sel_antigen)
    if sel_start_year: base_params.append('var_start_year=' + sel_start_year)
    if sel_end_year:   base_params.append('var_end_year='   + sel_end_year)
    if sel_top_n:      base_params.append('var_top_n='      + sel_top_n)
    filter_str    = '&'.join(base_params) + ('&' if base_params else '')
    sort_base     = '/Minh_page_3?' + filter_str
    page_base_url = '/Minh_page_3?' + filter_str + 'var_sort=' + sel_sort + '&var_page='

    # Query results
    results     = []
    total_pages = 1
    if sel_antigen and sel_start_year and sel_end_year:
        try:
            top_n = int(sel_top_n) if sel_top_n else 10
        except ValueError:
            top_n = 10

        antigen_name = next((row[1] for row in antigen_rows if str(row[0]) == sel_antigen), sel_antigen)

        raw = pyhtml.get_results_from_query(
            "database/immunisation.db",
            """SELECT c.name, a.name,
                      CAST(v_start.coverage AS REAL) as start_cov,
                      CAST(v_end.coverage AS REAL)   as end_cov,
                      CAST(v_end.coverage AS REAL) - CAST(v_start.coverage AS REAL) as improvement
               FROM Country c
               JOIN Antigen a ON a.AntigenID = '""" + sel_antigen + """'
               JOIN Vaccination v_start ON v_start.country = c.CountryID
                   AND v_start.antigen = '""" + sel_antigen + """'
                   AND v_start.year = """ + sel_start_year + """
                   AND v_start.coverage != ''
               JOIN Vaccination v_end ON v_end.country = c.CountryID
                   AND v_end.antigen = '""" + sel_antigen + """'
                   AND v_end.year = """ + sel_end_year + """
                   AND v_end.coverage != ''
               WHERE CAST(v_end.coverage AS REAL) > CAST(v_start.coverage AS REAL)
               ORDER BY improvement DESC"""
        )
        ranked = [(i + 1, row[0], row[1], sel_start_year, sel_end_year, row[4])
                  for i, row in enumerate(raw)]

        # Slice top N first (raw is ordered by improvement DESC), then sort within
        top_ranked = ranked[:top_n]

        sort_funcs = {
            'improvement_desc': (lambda r: r[5], True),
            'improvement_asc':  (lambda r: r[5], False),
            'nation_asc':       (lambda r: str(r[1]), False),
            'nation_desc':      (lambda r: str(r[1]), True),
            'antigen_asc':      (lambda r: str(r[2]), False),
            'antigen_desc':     (lambda r: str(r[2]), True),
        }
        key_func, reverse = sort_funcs.get(sel_sort, (lambda r: r[5], True))
        top_ranked.sort(key=key_func, reverse=reverse)

        total_pages = max(1, (len(top_ranked) + PER_PAGE - 1) // PER_PAGE)
        sel_page    = max(1, min(sel_page, total_pages))
        results     = top_ranked[(sel_page - 1) * PER_PAGE : sel_page * PER_PAGE]

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Improvement - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_3.css">
    <link rel="stylesheet" href="pagination_bar.css">
    <link rel="stylesheet" href="footer.css">
</head>
<body>

    {navbar.get_navbar()}

    <!-- PAGE HEADER -->
    <section class="page-header">
        <h1 class="page-title">Improvement Of Vaccination Rate In Specific Nation</h1>
        <div class="page-intro">
            <p class="page-description">
                Identify the top countries with the largest improvement in vaccination
                rates between two selected years for a specific antigen type.
            </p>
            <div class="help-box">
                <div class="help-box-title">How the page works</div>
                <p class="help-box-text">
                    Select an Antigen, Starting Year, Ending Year and Top Nation to see the
                    Line Chart For Top Nations That Have Vaccination Rate Improvement and
                    Table Summary For Line Chart.
                </p>
            </div>
        </div>
    </section>

    <!-- FILTER SECTION -->
    <section class="filter-section">
        <form action="/Minh_page_3" method="GET">

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
                        <label class="filter-label">Starting Year</label>
                        <select name="var_start_year" class="filter-select">
                            <option value="">--None--</option>"""

    for row in year_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_start_year == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[0]) + '</option>'

    page_html += """
                        </select>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Ending Year</label>
                        <select name="var_end_year" class="filter-select">
                            <option value="">--None--</option>"""

    for row in year_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_end_year == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[0]) + '</option>'

    page_html += f"""
                        </select>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Top Nation</label>
                        <input type="number" name="var_top_n" class="filter-input"
                               placeholder="e.g. 90" min="1" max="200"
                               value="{sel_top_n}">
                    </div>

                    <div class="filter-buttons">
                        <button type="submit" class="btn-apply">Apply Filters</button>
                        <a href="/Minh_page_3" class="btn-clear">&#x21BB; Clear All</a>
                    </div>

                </div>
            </div>

            <!-- RESULTS TABLE -->
            <div class="results-box">
                <div class="results-header">
                    <h2 class="results-title">Results</h2>
                    <div class="sort-row">
                        <label class="sort-label">Sort by</label>
                        <select name="var_sort" class="sort-select" onchange="this.form.submit()">
                            <option value="improvement_desc" {"selected" if sel_sort == "improvement_desc" else ""}>Increasement &#8595;</option>
                            <option value="improvement_asc"  {"selected" if sel_sort == "improvement_asc"  else ""}>Increasement &#8593;</option>
                            <option value="nation_asc"       {"selected" if sel_sort == "nation_asc"       else ""}>Nation A&#8209;Z</option>
                            <option value="nation_desc"      {"selected" if sel_sort == "nation_desc"      else ""}>Nation Z&#8209;A</option>
                        </select>
                    </div>
                </div>

                <h3 class="results-subtitle">Top Nations That Have Vaccination Rate Improvement</h3>

                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Nation <a class="sort-btn" href="{sort_base}var_sort=nation_asc">&#8593;</a><a class="sort-btn" href="{sort_base}var_sort=nation_desc">&#8595;</a></th>
                            <th>Antigen <a class="sort-btn" href="{sort_base}var_sort=antigen_asc">&#8593;</a><a class="sort-btn" href="{sort_base}var_sort=antigen_desc">&#8595;</a></th>
                            <th>Starting Year</th>
                            <th>Ending Year</th>
                            <th>Increasement <a class="sort-btn" href="{sort_base}var_sort=improvement_asc">&#8593;</a><a class="sort-btn" href="{sort_base}var_sort=improvement_desc">&#8595;</a></th>
                        </tr>
                    </thead>
                    <tbody>"""

    if results:
        for row in results:
            page_html += '<tr>'
            page_html += '<td>' + str(row[0]) + '</td>'
            page_html += '<td>' + str(row[1]) + '</td>'
            page_html += '<td>' + str(row[2]) + '</td>'
            page_html += '<td>' + str(row[3]) + '</td>'
            page_html += '<td>' + str(row[4]) + '</td>'
            page_html += '<td>+' + str(round(row[5], 1)) + '%</td>'
            page_html += '</tr>'
    else:
        page_html += '<tr><td colspan="6" class="no-results">Select filters above and click Apply Filters to see results.</td></tr>'

    page_html += """
                    </tbody>
                </table>
            """
    page_html += pagination_bar.get_pagination_bar(sel_page, total_pages, page_base_url)
    page_html += """
            </div>

        </form>
    </section>

    """ + footer.get_footer() + """

</body>
</html>
"""
    return page_html