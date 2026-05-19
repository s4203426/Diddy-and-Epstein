import pyhtml
import navbar
import footer
import pagination_bar
import breadcrumb

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
    var_view     = form_data.get('var_view')
    sel_view     = var_view[0] if var_view else 'nation'
    if sel_view not in ('nation', 'region'):
        sel_view = 'nation'

    region_lock = 'style="width:110px"'
    nation_lock = 'style="width:110px"'
    filtered_nation_rows = nation_rows

    # Validate: if both a specific region and a specific nation are chosen,
    # check that the nation actually belongs to that region
    invalid_nation_region = False
    if (sel_region and sel_region not in ('', 'ALL') and
            sel_nation and sel_nation not in ('', 'ALL')):
        nation_region = next((str(row[2]) for row in nation_rows if str(row[0]) == sel_nation), None)
        if nation_region != sel_region:
            invalid_nation_region = True

    # --- Build base URLs ---
    base_params = []
    if sel_antigen:  base_params.append('var_antigen='  + sel_antigen)
    if sel_year:     base_params.append('var_year='     + sel_year)
    if sel_region:   base_params.append('var_region='   + sel_region)
    if sel_nation:   base_params.append('var_nation='   + sel_nation)
    if sel_min_rate: base_params.append('var_min_rate=' + sel_min_rate)
    filter_str = '&'.join(base_params) + ('&' if base_params else '')

    # Sort links for table 1 headers (preserves sort2 and view)
    sort1_base    = '/Minh_page_2?' + filter_str + 'var_sort2=' + sel_sort2 + '&var_view=' + sel_view + '&'
    # Sort links for table 2 headers (preserves sort1 and view)
    sort2_base    = '/Minh_page_2?' + filter_str + 'var_sort='  + sel_sort  + '&var_view=' + sel_view + '&'
    # Pagination for table 1 (preserves both sorts and view)
    page_base_url = '/Minh_page_2?' + filter_str + 'var_sort=' + sel_sort + '&var_sort2=' + sel_sort2 + '&var_view=' + sel_view + '&var_page='
    # View toggle URLs
    nation_view_url = '/Minh_page_2?' + filter_str + 'var_sort=' + sel_sort + '&var_sort2=' + sel_sort2 + '&var_view=nation'
    region_view_url = '/Minh_page_2?' + filter_str + 'var_sort=' + sel_sort + '&var_sort2=' + sel_sort2 + '&var_view=region'
    # Button active classes
    nation_cls = 'vbtn vbtn-filled btn-active' if sel_view == 'nation' else 'vbtn vbtn-filled'
    region_cls  = 'vbtn vbtn-outline btn-active' if sel_view == 'region' else 'vbtn vbtn-outline'

    # --- Build results ---
    page_results  = []
    total_pages   = 1
    region_results = []

    if sel_antigen and sel_year and not invalid_nation_region:
        try:
            min_rate_val = float(sel_min_rate) if sel_min_rate else 0
        except ValueError:
            min_rate_val = 0

        antigen_name = next((row[1] for row in antigen_rows if str(row[0]) == sel_antigen), sel_antigen)

        # Table 1: per-country — ROW_NUMBER() for rank, IN subquery for nation filter, SQL ORDER BY + LIMIT/OFFSET
        order_map = {
            'coverage_desc': 'coverage DESC',
            'coverage_asc':  'coverage ASC',
            'nation_asc':    'nation ASC',
            'nation_desc':   'nation DESC',
            'antigen_asc':   'antigen ASC',
            'antigen_desc':  'antigen DESC',
            'year_asc':      'year ASC',
            'year_desc':     'year DESC',
            'region_asc':    'region ASC',
            'region_desc':   'region DESC',
        }
        order_by = order_map.get(sel_sort, 'coverage DESC')

        inner_sql = (
            "SELECT"
            " ROW_NUMBER() OVER (ORDER BY CAST(v.coverage AS REAL) DESC) AS rank,"
            " c.name AS nation,"
            " a.name AS antigen,"
            " v.year AS year,"
            " r.region AS region,"
            " CAST(v.coverage AS REAL) AS coverage"
            " FROM Vaccination v"
            " JOIN Country c ON v.country = c.CountryID"
            " JOIN Region r ON c.region = r.RegionID"
            " JOIN Antigen a ON v.antigen = a.AntigenID"
            " WHERE v.antigen = '" + sel_antigen + "'"
            " AND v.year = " + sel_year +
            " AND v.coverage != ''"
            " AND CAST(v.coverage AS REAL) >= " + str(min_rate_val)
        )
        if sel_region and sel_region != 'ALL':
            inner_sql += " AND r.RegionID = '" + sel_region + "'"
        if sel_nation and sel_nation != 'ALL':
            inner_sql += (" AND c.CountryID IN"
                          " (SELECT CountryID FROM Country WHERE CountryID = '" + sel_nation + "')")

        count_raw = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT COUNT(*) FROM (" + inner_sql + ")"
        )
        total_count = count_raw[0][0] if count_raw else 0
        total_pages  = max(1, (total_count + PER_PAGE - 1) // PER_PAGE)
        sel_page     = max(1, min(sel_page, total_pages))
        offset       = (sel_page - 1) * PER_PAGE

        page_results = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT rank, nation, antigen, year, region, coverage"
            " FROM (" + inner_sql + ")"
            " ORDER BY " + order_by +
            " LIMIT " + str(PER_PAGE) + " OFFSET " + str(offset)
        )

        # Table 2: per-region — LEFT JOIN to include regions with 0 nations, ROW_NUMBER() + SQL ORDER BY
        order_map2 = {
            'nations_desc': 'nation_count DESC',
            'nations_asc':  'nation_count ASC',
            'region_asc':   'region ASC',
            'region_desc':  'region DESC',
            'antigen_asc':  'antigen_name ASC',
            'antigen_desc': 'antigen_name DESC',
            'year_asc':     'sel_year ASC',
            'year_desc':    'sel_year DESC',
        }
        order_by2 = order_map2.get(sel_sort2, 'nation_count DESC')
        antigen_name_sql = antigen_name.replace("'", "''")

        region_results = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT"
            " ROW_NUMBER() OVER (ORDER BY COUNT(DISTINCT v.country) DESC) AS rank,"
            " r.region,"
            " '" + sel_year + "' AS sel_year,"
            " '" + antigen_name_sql + "' AS antigen_name,"
            " COUNT(DISTINCT v.country) AS nation_count"
            " FROM Region r"
            " LEFT JOIN Country c ON c.region = r.RegionID"
            " LEFT JOIN Vaccination v ON v.country = c.CountryID"
            "  AND v.antigen = '" + sel_antigen + "'"
            "  AND v.year = " + sel_year +
            "  AND v.coverage != ''"
            "  AND CAST(v.coverage AS REAL) >= " + str(min_rate_val) +
            " GROUP BY r.RegionID"
            " ORDER BY " + order_by2
        )

    no_filters = not (sel_antigen and sel_year)

    # --- Build HTML ---
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Data - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="breadcrumb.css">
    <link rel="stylesheet" href="Minh_page_2.css?v=9">
    <link rel="stylesheet" href="pagination_bar.css">
    <link rel="stylesheet" href="footer.css">
</head>
<body>

    {navbar.get_navbar()}

    <div class="lp2-wrapper">

        {breadcrumb.get_breadcrumb([("Home", "/"), ("Vaccination Data", "/Minh_page_2"), ("Vaccination Rate by Country &amp; Region", "/Minh_page_2")])}

        <!-- HEADER -->
        <div class="lp2-header">
            <div class="lp2-header-left">
                <h1 class="lp2-title">Data Visualization of Vaccination Rate</h1>
                <p class="lp2-desc">
                    Identify the top countries with the largest improvement in vaccination
                    rates between two selected years for a specific antigen type.
                </p>
            </div>
        </div>

        <!-- VIEW TOGGLE -->
        <div class="view-type-row">
            <div class="tooltip-wrap">
                <a href="{nation_view_url}" class="{nation_cls}">Nation View</a>
                <div class="vbtn-tooltip">Choose <strong>"Nation View"</strong> to see vaccination data for each country.</div>
            </div>
            <div class="tooltip-wrap">
                <a href="{region_view_url}" class="{region_cls}">Region View</a>
                <div class="vbtn-tooltip">Choose <strong>"Region View"</strong> to see vaccination data summarised by region.</div>
            </div>
        </div>

        <!-- FILTER + RESULTS -->
        <form action="/Minh_page_2" method="GET">
            <input type="hidden" name="var_view" value="{sel_view}">

            <!-- FILTER BOX -->
            <div class="filter-box">
                <div class="hiw-box">
                    <img src="images/i_icon.png" alt="Info" width="43" height="43">
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
                        <div class="filter-field-tooltip">Select a year.<br>Required to display results.</div>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Region</label>
                        <select id="region_select" name="var_region" class="filter-select" """ + region_lock + """>
                            <option value="ALL" """ + ('selected="selected"' if sel_region in (None, '', 'ALL') else '') + """>All Regions</option>"""

    for row in region_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_region == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[1]) + '</option>'

    page_html += """
                        </select>
                        <div class="filter-field-tooltip">Filter by region. Leave as <strong>All Regions</strong> to include all.<br>You can only select <strong>Region</strong> or <strong>Nation</strong>, not both.</div>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Nation</label>
                        <select id="nation_select" name="var_nation" class="filter-select" """ + nation_lock + """>
                            <option value="ALL" """ + ('selected="selected"' if sel_nation in (None, '', 'ALL') else '') + """>All Nations</option>"""

    for row in filtered_nation_rows:
        page_html += '<option value="' + str(row[0]) + '"'
        if sel_nation == str(row[0]):
            page_html += ' selected="selected"'
        page_html += '>' + str(row[1]) + '</option>'

    page_html += f"""
                        </select>
                        <div class="filter-field-tooltip">Filter by nation. Leave as <strong>All Nations</strong> to include all.<br>You can only select <strong>Region</strong> or <strong>Nation</strong>, not both.</div>
                    </div>

                    <div class="filter-field">
                        <label class="filter-label">Minimum Rate (X%)</label>
                        <input type="number" name="var_min_rate" class="filter-input"
                               placeholder="e.g. 80" min="0" max="200"
                               value="{sel_min_rate}">
                        <div class="filter-field-tooltip">Only show countries with vaccination rate<br>at or above this percentage (0–200).</div>
                    </div>

                    <div class="filter-buttons">
                        <button type="submit" class="btn-apply">Apply Filters</button>
                        <a href="/Minh_page_2" class="btn-clear"><span class="clear-icon">&#x21BB;</span> Clear All</a>
                    </div>

                </div>
            </div>"""

    if sel_view == 'nation':
        page_html += f"""
            <div class="results-box">
                <h2 class="results-title">Number of Countries Meeting Vaccination Rate Threshold</h2>"""
        if invalid_nation_region:
            page_html += """
                <div class="filter-placeholder filter-error">
                    <div class="fp-icon">&#9888;</div>
                    <p class="fp-title">Nation does not belong to the selected Region</p>
                    <p class="fp-desc">The nation you selected is not part of the chosen region.<br>
                    Please go back and select a nation that belongs to the selected region, or choose <strong>All Nations</strong> to include all.</p>
                </div>"""
        elif no_filters:
            page_html += """
                <div class="filter-placeholder">
                    <div class="fp-icon">&#128269;</div>
                    <p class="fp-title">No filters selected yet</p>
                    <p class="fp-desc">Select an Antigen and Year above, then click <strong>Apply Filters</strong> to view results.</p>
                </div>"""
        else:
            page_html += f"""
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Rank <a class="sort-btn" href="{sort1_base}var_sort=coverage_desc">&#8593;</a><a class="sort-btn" href="{sort1_base}var_sort=coverage_asc">&#8595;</a></th>
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
                page_html += '<tr><td colspan="6" class="no-results">No data matches your filters.</td></tr>'
            page_html += '</tbody></table>'
            page_html += pagination_bar.get_pagination_bar(sel_page, total_pages, page_base_url)
        page_html += '</div>'

    # TABLE 2: REGION VIEW
    if sel_view == 'region':
        page_html += f"""
            <div class="results-box">
                <h2 class="results-title">Countries Meeting Vaccination Rate Threshold By Region</h2>"""
        if invalid_nation_region:
            page_html += """
                <div class="filter-placeholder filter-error">
                    <div class="fp-icon">&#9888;</div>
                    <p class="fp-title">Nation does not belong to the selected Region</p>
                    <p class="fp-desc">The nation you selected is not part of the chosen region.<br>
                    Please go back and select a nation that belongs to the selected region, or choose <strong>All Nations</strong> to include all.</p>
                </div>"""
        elif no_filters:
            page_html += """
                <div class="filter-placeholder">
                    <div class="fp-icon">&#128269;</div>
                    <p class="fp-title">No filters selected yet</p>
                    <p class="fp-desc">Select an Antigen and Year above, then click <strong>Apply Filters</strong> to view results.</p>
                </div>"""
        else:
            page_html += f"""
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Rank <a class="sort-btn" href="{sort2_base}var_sort2=nations_desc">&#8593;</a><a class="sort-btn" href="{sort2_base}var_sort2=nations_asc">&#8595;</a></th>
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
                page_html += '<tr><td colspan="5" class="no-results">No data matches your filters.</td></tr>'
            page_html += '</tbody></table>'
        page_html += '</div>'

    page_html += f"""
        </form>
    </div>

{footer.get_footer()}

</body>
</html>
"""
    return page_html
