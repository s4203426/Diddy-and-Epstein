import pyhtml
import navbar
import footer

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

    sel_antigen  = var_antigen[0]  if var_antigen  else None
    sel_year     = var_year[0]     if var_year     else None
    sel_min_rate = var_min_rate[0] if var_min_rate else ''
    sel_sort     = var_sort[0]     if var_sort     else 'coverage_desc'

    # --- Build results query if filters applied ---
    results = []
    if sel_antigen and sel_year:
        try:
            min_rate_val = float(sel_min_rate) if sel_min_rate else 0
        except ValueError:
            min_rate_val = 0

        sort_map = {
            'coverage_desc': 'CAST(v.coverage AS REAL) DESC',
            'coverage_asc':  'CAST(v.coverage AS REAL) ASC',
            'nation_asc':    'c.name ASC',
            'region_asc':    'r.region ASC'
        }
        order_by = sort_map.get(sel_sort, 'CAST(v.coverage AS REAL) DESC')

        query = """SELECT c.name, a.name, v.year, r.region, CAST(v.coverage AS REAL)
        FROM Vaccination v
        JOIN Country c ON v.country = c.CountryID
        JOIN Region r ON c.region = r.RegionID
        JOIN Antigen a ON v.antigen = a.AntigenID
        WHERE v.antigen = '""" + sel_antigen + """'
        AND v.year = """ + sel_year + """
        AND v.coverage != ''
        AND CAST(v.coverage AS REAL) >= """ + str(min_rate_val) + """
        ORDER BY """ + order_by

        results = pyhtml.get_results_from_query("database/immunisation.db", query)

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
                        <select name="var_sort" class="sort-select">
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
                            <th>Nation</th>
                            <th>Antigen</th>
                            <th>Year</th>
                            <th>Region</th>
                            <th>Vaccination Rate</th>
                        </tr>
                    </thead>
                    <tbody>"""

    if results:
        for i, row in enumerate(results):
            page_html += '<tr>'
            page_html += '<td>' + str(i + 1) + '</td>'
            page_html += '<td>' + str(row[0]) + '</td>'
            page_html += '<td>' + str(row[1]) + '</td>'
            page_html += '<td>' + str(row[2]) + '</td>'
            page_html += '<td>' + str(row[3]) + '</td>'
            page_html += '<td>' + str(round(row[4], 1)) + '%</td>'
            page_html += '</tr>'
    else:
        page_html += '<tr><td colspan="6" class="no-results">Select filters above and click Apply Filters to see results.</td></tr>'

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
