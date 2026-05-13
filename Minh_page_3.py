import pyhtml
import navbar
import footer

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

    sel_antigen    = var_antigen[0]    if var_antigen    else None
    sel_start_year = var_start_year[0] if var_start_year else None
    sel_end_year   = var_end_year[0]   if var_end_year   else None
    sel_top_n      = var_top_n[0]      if var_top_n      else ''

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Improvement - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_3.css">
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

        </form>
    </section>

    {footer.get_footer()}

</body>
</html>
"""
    return page_html