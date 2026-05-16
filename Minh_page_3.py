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

        order_map = {
            'improvement_desc':  'improvement DESC',
            'improvement_asc':   'improvement ASC',
            'nation_asc':        'nation ASC',
            'nation_desc':       'nation DESC',
            'antigen_asc':       'antigen ASC',
            'antigen_desc':      'antigen DESC',
            'start_year_asc':    'start_year ASC',
            'start_year_desc':   'start_year DESC',
            'end_year_asc':      'end_year ASC',
            'end_year_desc':     'end_year DESC',
        }
        order_by = order_map.get(sel_sort, 'improvement DESC')

        # Subquery: countries that have vaccination data in BOTH start and end year (IN + INTERSECT)
        subquery = (
            "SELECT country FROM Vaccination"
            " WHERE antigen = '" + sel_antigen + "' AND year = " + sel_start_year + " AND coverage != ''"
            " INTERSECT"
            " SELECT country FROM Vaccination"
            " WHERE antigen = '" + sel_antigen + "' AND year = " + sel_end_year + " AND coverage != ''"
        )

        inner_sql = (
            "SELECT"
            " ROW_NUMBER() OVER (ORDER BY CAST(v_end.coverage AS REAL) - CAST(v_start.coverage AS REAL) DESC) AS rank,"
            " c.name AS nation,"
            " a.name AS antigen,"
            " v_start.year AS start_year,"
            " v_end.year AS end_year,"
            " CAST(v_end.coverage AS REAL) - CAST(v_start.coverage AS REAL) AS improvement"
            " FROM Country c"
            " JOIN Antigen a ON a.AntigenID = '" + sel_antigen + "'"
            " JOIN Vaccination v_start ON v_start.country = c.CountryID"
            "  AND v_start.antigen = '" + sel_antigen + "'"
            "  AND v_start.year = " + sel_start_year +
            "  AND v_start.coverage != ''"
            " JOIN Vaccination v_end ON v_end.country = c.CountryID"
            "  AND v_end.antigen = '" + sel_antigen + "'"
            "  AND v_end.year = " + sel_end_year +
            "  AND v_end.coverage != ''"
            " WHERE CAST(v_end.coverage AS REAL) > CAST(v_start.coverage AS REAL)"
            " AND c.CountryID IN (" + subquery + ")"
        )

        count_raw   = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT COUNT(*) FROM (" + inner_sql + ") WHERE rank <= " + str(top_n)
        )
        total_count = count_raw[0][0] if count_raw else 0
        total_pages = max(1, (total_count + PER_PAGE - 1) // PER_PAGE)
        sel_page    = max(1, min(sel_page, total_pages))
        offset      = (sel_page - 1) * PER_PAGE

        results = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT rank, nation, antigen, start_year, end_year, improvement"
            " FROM (" + inner_sql + ") WHERE rank <= " + str(top_n) +
            " ORDER BY " + order_by +
            " LIMIT " + str(PER_PAGE) + " OFFSET " + str(offset)
        )

    no_filters = not (sel_antigen and sel_start_year and sel_end_year)

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Improvement - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_3.css?v=5">
    <link rel="stylesheet" href="pagination_bar.css">
    <link rel="stylesheet" href="footer.css">
</head>
<body>

    {navbar.get_navbar()}

    <div class="lp2-wrapper">

        <!-- HEADER -->
        <div class="lp2-header">
            <div class="lp2-header-left">
                <h1 class="lp2-title">Improvement Of Vaccination Rate In Specific Nation</h1>
                <p class="lp2-desc">
                    Identify the top countries with the largest improvement in vaccination
                    rates between two selected years for a specific antigen type.
                </p>
            </div>
            <div class="hiw-box">
                <div class="hiw-heading">&#9432; How the page works</div>
                <p>Select an Antigen, Starting Year, Ending Year and Top Nation to see the
                Line Chart For Top Nations That Have Vaccination Rate Improvement and
                Table Summary For Line Chart.</p>
                <div class="hiw-steps">
                    <p class="hiw-steps-title">Step-by-step guide</p>
                    <div class="hiw-steps-row">
                        <div class="hiw-step">
                            <div class="hiw-step-icon">&#9776;</div>
                            <div class="hiw-step-label">Choose Antigen</div>
                        </div>
                        <span class="hiw-step-arrow">&#8594;</span>
                        <div class="hiw-step">
                            <div class="hiw-step-icon"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"><circle cx="10" cy="10" r="7"/><line x1="15.5" y1="15.5" x2="21" y2="21"/></svg></div>
                            <div class="hiw-step-label">Set Filters</div>
                        </div>
                        <span class="hiw-step-arrow">&#8594;</span>
                        <div class="hiw-step">
                            <div class="hiw-step-icon">&#10003;</div>
                            <div class="hiw-step-label">Apply Filters</div>
                        </div>
                        <span class="hiw-step-arrow">&#8594;</span>
                        <div class="hiw-step">
                            <div class="hiw-step-icon"><svg viewBox="0 0 24 24" width="20" height="20" fill="white"><rect x="2" y="13" width="5" height="8" rx="1"/><rect x="9.5" y="8" width="5" height="13" rx="1"/><rect x="17" y="4" width="5" height="17" rx="1"/></svg></div>
                            <div class="hiw-step-label">Explore Data</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FILTER + RESULTS -->
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
                        <div class="filter-field-tooltip">Select an antigen type.<br>Required to display results.</div>
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
                        <div class="filter-field-tooltip">Select the starting year for comparison.<br>Must be earlier than Ending Year.</div>
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
                        <div class="filter-field-tooltip">Select the ending year for comparison.<br>Must be later than Starting Year.</div>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Top Nation</label>
                        <input type="number" name="var_top_n" class="filter-input"
                               placeholder="e.g. 90" min="1" max="200"
                               value="{sel_top_n}">
                        <div class="filter-field-tooltip">Number of top nations to display.<br>Default is 10 if left empty.</div>
                    </div>

                    <div class="filter-buttons">
                        <button type="submit" class="btn-apply">Apply Filters</button>
                        <a href="/Minh_page_3" class="btn-clear">&#x21BB; Clear All</a>
                    </div>

                </div>
            </div>

            <!-- RESULTS TABLE -->
            <div class="results-box">
                <h2 class="results-title">Top Nations That Have Vaccination Rate Improvement</h2>"""

    if no_filters:
        page_html += """
                <div class="filter-placeholder">
                    <div class="fp-icon">&#128269;</div>
                    <p class="fp-title">No filters selected yet</p>
                    <p class="fp-desc">Select an Antigen, Starting Year and Ending Year above, then click <strong>Apply Filters</strong> to view results.</p>
                </div>"""
    else:
        page_html += f"""
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
            page_html += '<tr><td colspan="6" class="no-results">No results found. Try adjusting your filters.</td></tr>'

    if not no_filters:
        page_html += """
                    </tbody>
                </table>
            """
        page_html += pagination_bar.get_pagination_bar(sel_page, total_pages, page_base_url)
    page_html += """
            </div>

        </form>

    </div>

    """ + footer.get_footer() + """

</body>
</html>
"""
    return page_html