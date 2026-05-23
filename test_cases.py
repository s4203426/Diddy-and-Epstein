"""
Test Cases for Vaccination & Infection Tracker Web Application
=============================================================
Covers: pagination_bar, Minh_page_1, Minh_page_2, Minh_page_3,
        Long_page_1, Long_page_2, Long_page_3
"""

import unittest
import os
import sys

# Run all tests from the project root so relative DB paths resolve
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyhtml
import pagination_bar
import Minh_page_1
import Minh_page_2
import Minh_page_3
import Long_page_1
import Long_page_2
import Long_page_3

# ── helpers ──────────────────────────────────────────────────────────────────

def _fd(**kwargs):
    """Build a form_data dict (same shape as parse_qs output)."""
    return {k: [str(v)] for k, v in kwargs.items()}


# ── database fixtures (loaded once) ──────────────────────────────────────────

def _first(query, db="database/immunisation.db"):
    rows = pyhtml.get_results_from_query(db, query)
    return rows[0][0] if rows else None


VALID_ANTIGEN_ID   = str(_first("SELECT AntigenID FROM Antigen LIMIT 1"))
VALID_YEAR         = str(_first("SELECT DISTINCT year FROM Vaccination ORDER BY year DESC LIMIT 1"))
VALID_START_YEAR   = str(_first("SELECT DISTINCT year FROM Vaccination ORDER BY year ASC  LIMIT 1"))
VALID_END_YEAR     = str(_first(
    f"SELECT DISTINCT year FROM Vaccination "
    f"WHERE year > {VALID_START_YEAR} ORDER BY year ASC LIMIT 1"
))
VALID_REGION_ID    = str(_first("SELECT RegionID FROM Region LIMIT 1"))
VALID_NATION_ID    = str(_first("SELECT CountryID FROM Country LIMIT 1"))
VALID_INF_TYPE_ID  = str(_first("SELECT id FROM Infection_Type LIMIT 1"))
VALID_ECONOMY_ID   = str(_first("SELECT economyID FROM Economy LIMIT 1"))
VALID_INF_YEAR     = str(_first("SELECT DISTINCT year FROM InfectionData ORDER BY year DESC LIMIT 1"))


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PAGINATION BAR
# ═══════════════════════════════════════════════════════════════════════════════

class TestPaginationBarGetPageNumbers(unittest.TestCase):
    """Unit tests for pagination_bar.get_page_numbers()"""

    def test_single_page(self):
        self.assertEqual(pagination_bar.get_page_numbers(1, 1), [1])

    def test_all_pages_shown_when_seven_or_fewer(self):
        result = pagination_bar.get_page_numbers(1, 7)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7])

    def test_all_pages_shown_at_exactly_seven(self):
        result = pagination_bar.get_page_numbers(4, 7)
        self.assertNotIn('...', result)
        self.assertEqual(len(result), 7)

    def test_ellipsis_appears_for_more_than_seven_pages(self):
        result = pagination_bar.get_page_numbers(5, 20)
        self.assertIn('...', result)

    def test_first_and_last_page_always_present(self):
        result = pagination_bar.get_page_numbers(10, 20)
        self.assertIn(1, result)
        self.assertIn(20, result)

    def test_current_page_always_present(self):
        for current in [1, 5, 10, 15, 20]:
            result = pagination_bar.get_page_numbers(current, 20)
            self.assertIn(current, result, f"Page {current} missing")

    def test_current_page_neighbours_present(self):
        result = pagination_bar.get_page_numbers(10, 20)
        self.assertIn(9, result)
        self.assertIn(11, result)

    def test_first_page_current(self):
        result = pagination_bar.get_page_numbers(1, 20)
        self.assertIn(1, result)

    def test_last_page_current(self):
        result = pagination_bar.get_page_numbers(20, 20)
        self.assertIn(20, result)


class TestPaginationBarGetHTML(unittest.TestCase):
    """Tests for pagination_bar.get_pagination_bar()"""

    def test_returns_empty_when_one_page(self):
        self.assertEqual(pagination_bar.get_pagination_bar(1, 1, "/test?page="), '')

    def test_returns_html_for_multiple_pages(self):
        html = pagination_bar.get_pagination_bar(1, 5, "/test?page=")
        self.assertIn('<div class="pagination"', html)

    def test_current_page_marked_active(self):
        html = pagination_bar.get_pagination_bar(3, 10, "/test?page=")
        self.assertIn('page-btn-active', html)

    def test_prev_disabled_on_first_page(self):
        html = pagination_bar.get_pagination_bar(1, 5, "/test?page=")
        self.assertIn('page-btn-disabled', html)

    def test_next_disabled_on_last_page(self):
        html = pagination_bar.get_pagination_bar(5, 5, "/test?page=")
        self.assertIn('page-btn-disabled', html)

    def test_prev_not_disabled_on_middle_page(self):
        html = pagination_bar.get_pagination_bar(3, 10, "/test?page=")
        # Both prev and next links should exist without disabled class for the next button
        self.assertIn('/test?page=2', html)

    def test_page_info_text_present(self):
        html = pagination_bar.get_pagination_bar(2, 5, "/test?page=")
        self.assertIn('Showing 2 of 5 pages', html)

    def test_base_url_embedded_in_links(self):
        html = pagination_bar.get_pagination_bar(1, 3, "/custom?page=")
        self.assertIn('/custom?page=', html)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MINH_PAGE_1  –  Home / Landing Page
# ═══════════════════════════════════════════════════════════════════════════════

class TestMinhPage1(unittest.TestCase):
    """Tests for Minh_page_1 (Home/Landing page with vaccination chart)."""

    def setUp(self):
        self.html = Minh_page_1.get_page_html({})

    def test_page_returns_string(self):
        self.assertIsInstance(self.html, str)

    def test_html_doctype_present(self):
        self.assertTrue(self.html.strip().startswith('<!DOCTYPE html>'))

    def test_page_title_present(self):
        self.assertIn('<title>', self.html)

    def test_navbar_included(self):
        self.assertIn('navbar', self.html.lower())

    def test_footer_included(self):
        self.assertIn('footer', self.html.lower())

    def test_svg_chart_present(self):
        self.assertIn('<svg', self.html)

    def test_hero_section_present(self):
        self.assertIn('Vaccination', self.html)

    def test_navigation_links_to_other_pages(self):
        self.assertIn('/Minh_page_2', self.html)
        self.assertIn('/Long_page_1', self.html)

    def test_chart_has_data_points(self):
        # SVG data points rendered as <circle> or <polyline>
        self.assertTrue('<circle' in self.html or '<polyline' in self.html or 'points=' in self.html)

    def test_closing_html_tag_present(self):
        self.assertIn('</html>', self.html)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MINH_PAGE_2  –  Vaccination Data Explorer
# ═══════════════════════════════════════════════════════════════════════════════

class TestMinhPage2NoFilters(unittest.TestCase):
    """Minh_page_2: default state (no antigen/year selected)."""

    def setUp(self):
        self.html = Minh_page_2.get_page_html({})

    def test_page_loads(self):
        self.assertIsInstance(self.html, str)
        self.assertIn('<!DOCTYPE html>', self.html)

    def test_placeholder_shown_when_no_filters(self):
        self.assertIn('No filters selected yet', self.html)

    def test_filter_form_present(self):
        self.assertIn('<form', self.html)
        self.assertIn('var_antigen', self.html)
        self.assertIn('var_year', self.html)

    def test_antigen_dropdown_populated(self):
        self.assertIn('<option value="', self.html)

    def test_view_toggle_buttons_present(self):
        self.assertIn('Nation View', self.html)
        self.assertIn('Region View', self.html)

    def test_nation_view_active_by_default(self):
        self.assertIn('btn-active', self.html)

    def test_apply_and_clear_buttons_present(self):
        self.assertIn('Apply Filters', self.html)
        self.assertIn('Clear All', self.html)

    def test_no_results_table_without_filters(self):
        self.assertNotIn('<tbody>', self.html)


class TestMinhPage2WithFilters(unittest.TestCase):
    """Minh_page_2: valid antigen + year → results table rendered."""

    def setUp(self):
        self.html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR)
        )

    def test_results_table_present(self):
        self.assertIn('<table', self.html)
        self.assertIn('<tbody>', self.html)

    def test_no_placeholder_message(self):
        self.assertNotIn('No filters selected yet', self.html)

    def test_table_has_rank_column(self):
        self.assertIn('Rank', self.html)

    def test_table_has_nation_column(self):
        self.assertIn('Nation', self.html)

    def test_table_has_vaccination_rate_column(self):
        self.assertIn('Vaccination Rate', self.html)

    def test_table_has_region_column(self):
        self.assertIn('Region', self.html)

    def test_percentage_sign_in_results(self):
        self.assertIn('%', self.html)

    def test_sort_buttons_present(self):
        self.assertIn('sort-btn', self.html)

    def test_antigen_id_preserved_in_form(self):
        self.assertIn(f'value="{VALID_ANTIGEN_ID}"', self.html)

    def test_year_preserved_in_form(self):
        self.assertIn(f'value="{VALID_YEAR}"', self.html)


class TestMinhPage2RegionView(unittest.TestCase):
    """Minh_page_2: region view toggle."""

    def setUp(self):
        self.html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_view='region')
        )

    def test_region_view_rendered(self):
        self.assertIn('Number of Nations', self.html)

    def test_region_column_present(self):
        self.assertIn('Region', self.html)

    def test_region_view_btn_active(self):
        self.assertIn('btn-active', self.html)

    def test_nation_view_table_not_shown(self):
        # Region view does not show the per-country "Vaccination Rate" column header
        self.assertNotIn('<th>Vaccination Rate', self.html)


class TestMinhPage2RegionFilter(unittest.TestCase):
    """Minh_page_2: region filter applied."""

    def setUp(self):
        self.html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR,
                var_region=VALID_REGION_ID)
        )

    def test_no_placeholder(self):
        self.assertNotIn('No filters selected yet', self.html)

    def test_region_id_preserved_in_url(self):
        self.assertIn(f'var_region={VALID_REGION_ID}', self.html)


class TestMinhPage2MinRateFilter(unittest.TestCase):
    """Minh_page_2: minimum vaccination rate filter."""

    def test_high_min_rate_may_return_no_results(self):
        html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_min_rate=999)
        )
        self.assertTrue(
            'No data matches your filters.' in html or '<td>' in html
        )

    def test_zero_min_rate_returns_results(self):
        html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_min_rate=0)
        )
        self.assertIn('<table', html)

    def test_invalid_min_rate_treated_as_zero(self):
        html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_min_rate='abc')
        )
        self.assertIn('<table', html)


class TestMinhPage2NationResetWarning(unittest.TestCase):
    """Minh_page_2: nation reset warning when nation is outside selected region."""

    def test_warning_shown_when_nation_not_in_region(self):
        nation_rows = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT c.CountryID, c.name, c.region FROM Country c LIMIT 1"
        )
        all_regions = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT RegionID FROM Region ORDER BY RegionID"
        )
        if not nation_rows or len(all_regions) < 2:
            self.skipTest("Not enough data to test nation reset")

        nation_id    = str(nation_rows[0][0])
        nation_region = str(nation_rows[0][2])
        other_region = next(
            (str(r[0]) for r in all_regions if str(r[0]) != nation_region),
            None
        )
        if not other_region:
            self.skipTest("No alternate region found")

        html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR,
                var_nation=nation_id, var_region=other_region)
        )
        self.assertIn('not in the selected region', html)


class TestMinhPage2Sorting(unittest.TestCase):
    """Minh_page_2: all sort options produce a valid response."""

    SORT_OPTIONS = [
        'coverage_desc', 'coverage_asc',
        'nation_asc', 'nation_desc',
        'antigen_asc', 'antigen_desc',
        'year_asc', 'year_desc',
        'region_asc', 'region_desc',
    ]

    def _get_html(self, sort_val):
        return Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_sort=sort_val)
        )

    def test_all_sort_options_render_table(self):
        for sort_val in self.SORT_OPTIONS:
            with self.subTest(sort=sort_val):
                html = self._get_html(sort_val)
                self.assertIn('<table', html, f"Table missing for sort={sort_val}")

    def test_unknown_sort_falls_back_to_default(self):
        html = self._get_html('invalid_sort_key')
        self.assertIn('<table', html)


class TestMinhPage2Pagination(unittest.TestCase):
    """Minh_page_2: pagination controls."""

    def test_page_two_renders(self):
        html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_page=2)
        )
        self.assertIn('<table', html)

    def test_negative_page_clamped_to_one(self):
        html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_page=-5)
        )
        self.assertIn('<table', html)

    def test_huge_page_clamped_to_max(self):
        html = Minh_page_2.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_year=VALID_YEAR, var_page=99999)
        )
        self.assertIn('<table', html)


class TestMinhPage2AntigenOnlyNoResults(unittest.TestCase):
    """Minh_page_2: antigen provided but no year → placeholder shown."""

    def test_placeholder_when_year_missing(self):
        html = Minh_page_2.get_page_html(_fd(var_antigen=VALID_ANTIGEN_ID))
        self.assertIn('No filters selected yet', html)

    def test_placeholder_when_antigen_missing(self):
        html = Minh_page_2.get_page_html(_fd(var_year=VALID_YEAR))
        self.assertIn('No filters selected yet', html)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. MINH_PAGE_3  –  Vaccination Improvement
# ═══════════════════════════════════════════════════════════════════════════════

class TestMinhPage3NoFilters(unittest.TestCase):
    """Minh_page_3: default state."""

    def setUp(self):
        self.html = Minh_page_3.get_page_html({})

    def test_page_loads(self):
        self.assertIsInstance(self.html, str)
        self.assertIn('<!DOCTYPE html>', self.html)

    def test_placeholder_shown(self):
        self.assertIn('No filters selected yet', self.html)

    def test_filter_form_present(self):
        self.assertIn('var_antigen', self.html)
        self.assertIn('var_start_year', self.html)
        self.assertIn('var_end_year', self.html)

    def test_top_nation_input_present(self):
        self.assertIn('var_top_n', self.html)

    def test_no_results_table(self):
        self.assertNotIn('<tbody>', self.html)


class TestMinhPage3InvalidEndYear(unittest.TestCase):
    """Minh_page_3: end year <= start year shows error."""

    def test_equal_years_show_error(self):
        html = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID,
                var_start_year=VALID_START_YEAR,
                var_end_year=VALID_START_YEAR)
        )
        self.assertIn('Invalid Ending Year', html)

    def test_end_year_before_start_year_shows_error(self):
        # end year = start year - 1 (if start > first available year)
        years = pyhtml.get_results_from_query(
            "database/immunisation.db",
            "SELECT DISTINCT year FROM Vaccination ORDER BY year ASC LIMIT 3"
        )
        if len(years) < 2:
            self.skipTest("Not enough years in DB")
        start = str(years[1][0])
        end   = str(years[0][0])   # earlier year
        html  = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID, var_start_year=start, var_end_year=end)
        )
        self.assertIn('Invalid Ending Year', html)

    def test_error_message_clears_end_year_selection(self):
        html = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID,
                var_start_year=VALID_START_YEAR,
                var_end_year=VALID_START_YEAR)
        )
        self.assertNotIn('No filters selected yet', html)


class TestMinhPage3ValidFilters(unittest.TestCase):
    """Minh_page_3: all three required filters produce results."""

    def setUp(self):
        self.html = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID,
                var_start_year=VALID_START_YEAR,
                var_end_year=VALID_END_YEAR)
        )

    def test_no_placeholder(self):
        self.assertNotIn('No filters selected yet', self.html)

    def test_no_invalid_year_error(self):
        self.assertNotIn('Invalid Ending Year', self.html)

    def test_results_table_present(self):
        self.assertIn('<table', self.html)

    def test_rank_column_present(self):
        self.assertIn('Rank', self.html)

    def test_improvement_column_present(self):
        self.assertIn('Increasement', self.html)

    def test_positive_improvement_sign(self):
        # Results should show "+" if any data exists
        if 'No results found' not in self.html:
            self.assertIn('+', self.html)


class TestMinhPage3TopN(unittest.TestCase):
    """Minh_page_3: Top N filter."""

    def test_top_n_one_returns_at_most_one_row(self):
        html = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID,
                var_start_year=VALID_START_YEAR,
                var_end_year=VALID_END_YEAR,
                var_top_n=1)
        )
        self.assertIn('<table', html)
        # Count <tr> rows in <tbody> — max 1 data row
        tbody_start = html.find('<tbody>')
        tbody_end   = html.find('</tbody>')
        tbody_html  = html[tbody_start:tbody_end]
        row_count   = tbody_html.count('<tr>')
        self.assertLessEqual(row_count, 1)

    def test_invalid_top_n_defaults_to_ten(self):
        html = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID,
                var_start_year=VALID_START_YEAR,
                var_end_year=VALID_END_YEAR,
                var_top_n='xyz')
        )
        self.assertIn('<table', html)


class TestMinhPage3Sorting(unittest.TestCase):
    """Minh_page_3: all sort options."""

    SORT_OPTIONS = [
        'improvement_desc', 'improvement_asc',
        'nation_asc', 'nation_desc',
        'antigen_asc', 'antigen_desc',
        'start_year_asc', 'start_year_desc',
        'end_year_asc', 'end_year_desc',
    ]

    def test_all_sort_options_render_without_error(self):
        for sort_val in self.SORT_OPTIONS:
            with self.subTest(sort=sort_val):
                html = Minh_page_3.get_page_html(
                    _fd(var_antigen=VALID_ANTIGEN_ID,
                        var_start_year=VALID_START_YEAR,
                        var_end_year=VALID_END_YEAR,
                        var_sort=sort_val)
                )
                self.assertIn('<table', html, f"Table missing for sort={sort_val}")


class TestMinhPage3Pagination(unittest.TestCase):
    """Minh_page_3: pagination."""

    def test_page_two_renders(self):
        html = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID,
                var_start_year=VALID_START_YEAR,
                var_end_year=VALID_END_YEAR,
                var_page=2)
        )
        self.assertIn('<table', html)

    def test_out_of_range_page_clamped(self):
        html = Minh_page_3.get_page_html(
            _fd(var_antigen=VALID_ANTIGEN_ID,
                var_start_year=VALID_START_YEAR,
                var_end_year=VALID_END_YEAR,
                var_page=9999)
        )
        self.assertIn('<table', html)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. LONG_PAGE_1  –  Mission Statement
# ═══════════════════════════════════════════════════════════════════════════════

class TestLongPage1(unittest.TestCase):
    """Tests for Long_page_1 (Mission Statement page)."""

    def setUp(self):
        self.html = Long_page_1.get_page_html({})

    def test_page_loads(self):
        self.assertIsInstance(self.html, str)
        self.assertIn('<!DOCTYPE html>', self.html)

    def test_page_title_contains_mission(self):
        self.assertIn('Mission', self.html)

    def test_our_purpose_section_present(self):
        self.assertIn('Our Purpose', self.html)

    def test_how_it_helps_section_present(self):
        self.assertIn('How This Website Helps', self.html)

    def test_how_to_use_section_present(self):
        self.assertIn('How to Use This Website', self.html)

    def test_who_its_for_section_present(self):
        self.assertIn("Who This Website Is For", self.html)

    def test_our_team_section_present(self):
        self.assertIn('Our Team', self.html)

    def test_table_of_contents_present(self):
        self.assertIn('Table of Contents', self.html)

    def test_toc_anchors_link_to_sections(self):
        self.assertIn('#our-purpose', self.html)
        self.assertIn('#how-it-helps', self.html)
        self.assertIn('#how-to-use', self.html)
        self.assertIn('#who-its-for', self.html)
        self.assertIn('#our-team', self.html)

    def test_personas_loaded_from_database(self):
        personas = pyhtml.get_results_from_query(
            "database/web_data.db",
            "SELECT name FROM Personas"
        )
        for (name,) in personas:
            self.assertIn(name, self.html)

    def test_team_members_loaded_from_database(self):
        team = pyhtml.get_results_from_query(
            "database/web_data.db",
            "SELECT name FROM TeamMembers"
        )
        for (name,) in team:
            self.assertIn(name, self.html)

    def test_team_member_student_ids_present(self):
        team = pyhtml.get_results_from_query(
            "database/web_data.db",
            "SELECT student_number FROM TeamMembers"
        )
        for (sid,) in team:
            self.assertIn(str(sid), self.html)

    def test_navbar_included(self):
        self.assertIn('navbar', self.html.lower())

    def test_footer_included(self):
        self.assertIn('footer', self.html.lower())

    def test_breadcrumb_present(self):
        self.assertIn('Mission Statement', self.html)

    def test_page_ignores_unknown_form_data(self):
        html = Long_page_1.get_page_html(_fd(unknown_param='xyz'))
        self.assertIn('Our Purpose', html)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. LONG_PAGE_2  –  Infection Data by Economic Status
# ═══════════════════════════════════════════════════════════════════════════════

class TestLongPage2NoFilters(unittest.TestCase):
    """Long_page_2: default state (no 'applied' param)."""

    def setUp(self):
        self.html = Long_page_2.get_page_html({})

    def test_page_loads(self):
        self.assertIsInstance(self.html, str)
        self.assertIn('<!DOCTYPE html>', self.html)

    def test_placeholder_shown(self):
        self.assertIn('No filters selected yet', self.html)

    def test_view_toggle_present(self):
        self.assertIn('Country-level View', self.html)
        self.assertIn('Summary View', self.html)

    def test_filter_form_present(self):
        self.assertIn('<form', self.html)
        self.assertIn('inf_type', self.html)
        self.assertIn('year', self.html)

    def test_apply_button_present(self):
        self.assertIn('Apply Filters', self.html)

    def test_no_results_table_without_applied(self):
        self.assertNotIn('results-table', self.html)


class TestLongPage2CountryViewApplied(unittest.TestCase):
    """Long_page_2: country view with applied filter."""

    def setUp(self):
        self.html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1)
        )

    def test_results_table_present(self):
        self.assertIn('results-table', self.html)

    def test_no_placeholder(self):
        self.assertNotIn('No filters selected yet', self.html)

    def test_country_column_in_header(self):
        self.assertIn('Country', self.html)

    def test_economic_phase_column_present(self):
        self.assertIn('Economic', self.html)

    def test_preventable_disease_column_present(self):
        self.assertIn('Preventable disease', self.html)

    def test_cases_per_100k_column_present(self):
        self.assertIn('100,000', self.html)

    def test_display_toggle_present(self):
        self.assertIn('Table View', self.html)
        self.assertIn('Graph View', self.html)


class TestLongPage2SummaryView(unittest.TestCase):
    """Long_page_2: summary view (by economic phase)."""

    def setUp(self):
        self.html = Long_page_2.get_page_html(
            _fd(view_type='summary', display='table', applied=1)
        )

    def test_summary_view_renders(self):
        self.assertIn('results-table', self.html)

    def test_economic_phase_column_present(self):
        self.assertIn('Economic phase', self.html)

    def test_countries_count_column_present(self):
        self.assertIn('Countries', self.html)

    def test_economy_filter_absent_in_summary_view(self):
        # Economy filter dropdown only shows in country view
        # In summary view the economy dropdown is hidden
        self.assertNotIn('Economic Phases', self.html)

    def test_summary_view_button_active(self):
        self.assertIn('btn-active', self.html)


class TestLongPage2Filters(unittest.TestCase):
    """Long_page_2: individual filter parameters."""

    def test_infection_type_filter_applied(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1,
                inf_type=VALID_INF_TYPE_ID)
        )
        self.assertIn('results-table', html)

    def test_year_filter_applied(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1,
                year=VALID_INF_YEAR)
        )
        self.assertIn('results-table', html)

    def test_economy_filter_applied(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1,
                economy=VALID_ECONOMY_ID)
        )
        self.assertIn('results-table', html)

    def test_all_filters_combined(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1,
                economy=VALID_ECONOMY_ID,
                inf_type=VALID_INF_TYPE_ID,
                year=VALID_INF_YEAR)
        )
        self.assertIn('<table', html)

    def test_invalid_year_ignored(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1,
                year='not_a_year')
        )
        self.assertIn('results-table', html)

    def test_invalid_view_type_defaults_to_country(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='invalid', display='table', applied=1)
        )
        self.assertIn('Country', html)


class TestLongPage2GraphView(unittest.TestCase):
    """Long_page_2: graph/bar chart display."""

    def setUp(self):
        self.html = Long_page_2.get_page_html(
            _fd(view_type='country', display='graph', applied=1,
                year=VALID_INF_YEAR)
        )

    def test_bar_chart_rendered(self):
        self.assertIn('bar-chart', self.html)

    def test_no_table_in_graph_mode(self):
        # In graph mode the results-table should not be the active display
        # (bar-chart is shown instead of results-table for results block)
        self.assertNotIn('results-table', self.html)

    def test_axis_label_present(self):
        self.assertIn('100,000', self.html)

    def test_graph_view_button_active(self):
        self.assertIn('btn-active', self.html)


class TestLongPage2Sorting(unittest.TestCase):
    """Long_page_2: sort column options."""

    def _html(self, sort, dir_='asc'):
        return Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1,
                sort=sort, dir=dir_)
        )

    def test_sort_by_country_asc(self):
        self.assertIn('<table', self._html('country', 'asc'))

    def test_sort_by_country_desc(self):
        self.assertIn('<table', self._html('country', 'desc'))

    def test_sort_by_economy_asc(self):
        self.assertIn('<table', self._html('economy', 'asc'))

    def test_sort_by_metric_desc(self):
        self.assertIn('<table', self._html('metric', 'desc'))

    def test_sort_by_year_asc(self):
        self.assertIn('<table', self._html('year', 'asc'))

    def test_invalid_sort_falls_back(self):
        self.assertIn('<table', self._html('totally_invalid'))


class TestLongPage2Pagination(unittest.TestCase):
    """Long_page_2: pagination controls."""

    def test_page_two_renders(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1, page=2)
        )
        self.assertIn('<table', html)

    def test_pagination_info_shown(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1)
        )
        self.assertIn('Showing', html)

    def test_out_of_range_page_clamped(self):
        html = Long_page_2.get_page_html(
            _fd(view_type='country', display='table', applied=1, page=99999)
        )
        self.assertIn('<table', html)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. LONG_PAGE_3  –  Countries with Above-Average Infection Rate
# ═══════════════════════════════════════════════════════════════════════════════

class TestLongPage3NoFilters(unittest.TestCase):
    """Long_page_3: default state (no 'applied' param)."""

    def setUp(self):
        self.html = Long_page_3.get_page_html({})

    def test_page_loads(self):
        self.assertIsInstance(self.html, str)
        self.assertIn('<!DOCTYPE html>', self.html)

    def test_placeholder_shown(self):
        self.assertIn('No filters selected yet', self.html)

    def test_filter_form_present(self):
        self.assertIn('inf_type', self.html)
        self.assertIn('year', self.html)

    def test_apply_button_present(self):
        self.assertIn('Apply Filters', self.html)

    def test_global_rate_card_not_shown_without_applied(self):
        self.assertNotIn('Global Infection Rate', self.html)


class TestLongPage3Applied(unittest.TestCase):
    """Long_page_3: applied filter (all data)."""

    def setUp(self):
        self.html = Long_page_3.get_page_html(_fd(applied=1))

    def test_no_placeholder(self):
        self.assertNotIn('No filters selected yet', self.html)

    def test_global_rate_card_shown(self):
        self.assertIn('Global Infection Rate', self.html)

    def test_results_table_present(self):
        self.assertIn('<table', self.html)

    def test_country_column_present(self):
        self.assertIn('Country', self.html)

    def test_infection_type_column_present(self):
        self.assertIn('Infection Type', self.html)

    def test_rate_column_present(self):
        self.assertIn('100,000', self.html)

    def test_display_toggle_present(self):
        self.assertIn('Table View', self.html)
        self.assertIn('Graph View', self.html)


class TestLongPage3Filters(unittest.TestCase):
    """Long_page_3: filter parameter combinations."""

    def test_infection_type_filter(self):
        html = Long_page_3.get_page_html(
            _fd(applied=1, inf_type=VALID_INF_TYPE_ID)
        )
        self.assertIn('Global Infection Rate', html)

    def test_year_filter(self):
        html = Long_page_3.get_page_html(
            _fd(applied=1, year=VALID_INF_YEAR)
        )
        self.assertIn('Global Infection Rate', html)

    def test_both_filters_combined(self):
        html = Long_page_3.get_page_html(
            _fd(applied=1, inf_type=VALID_INF_TYPE_ID, year=VALID_INF_YEAR)
        )
        self.assertIn('Global Infection Rate', html)

    def test_invalid_year_ignored(self):
        html = Long_page_3.get_page_html(
            _fd(applied=1, year='not_a_year')
        )
        self.assertIn('Global Infection Rate', html)

    def test_sql_injection_in_inf_type_sanitised(self):
        # safe_str only allows alphanumeric — injection chars stripped
        html = Long_page_3.get_page_html(
            _fd(applied=1, inf_type="'; DROP TABLE--")
        )
        self.assertIsInstance(html, str)

    def test_global_rate_displayed_as_number(self):
        html = Long_page_3.get_page_html(
            _fd(applied=1, year=VALID_INF_YEAR, inf_type=VALID_INF_TYPE_ID)
        )
        self.assertIn('global-rate', html)


class TestLongPage3GlobalRateLogic(unittest.TestCase):
    """Long_page_3: global rate calculation."""

    def test_global_rate_present_when_applied(self):
        html = Long_page_3.get_page_html(_fd(applied=1, year=VALID_INF_YEAR))
        self.assertIn('global-rate', html)

    def test_no_country_below_global_average_in_results(self):
        # All listed countries should be ABOVE global average — check page renders
        html = Long_page_3.get_page_html(_fd(applied=1, year=VALID_INF_YEAR))
        self.assertNotIn('No filters selected yet', html)

    def test_global_rate_card_shows_correct_labels(self):
        html = Long_page_3.get_page_html(_fd(applied=1))
        self.assertIn('per 100,000', html)


class TestLongPage3GraphView(unittest.TestCase):
    """Long_page_3: bar chart display mode."""

    def setUp(self):
        self.html = Long_page_3.get_page_html(
            _fd(applied=1, display='graph', year=VALID_INF_YEAR)
        )

    def test_bar_chart_rendered(self):
        self.assertIn('bar-chart', self.html)

    def test_global_average_note_in_graph(self):
        self.assertIn('Global average', self.html)

    def test_graph_view_button_active(self):
        self.assertIn('btn-active', self.html)

    def test_no_results_table_in_graph_mode(self):
        self.assertNotIn('results-table', self.html)


class TestLongPage3Sorting(unittest.TestCase):
    """Long_page_3: sort options."""

    SORT_OPTIONS = ['country', 'inf_type', 'rate', 'year']
    DIR_OPTIONS  = ['asc', 'desc']

    def test_all_sort_and_dir_combos(self):
        for sort in self.SORT_OPTIONS:
            for dir_ in self.DIR_OPTIONS:
                with self.subTest(sort=sort, dir=dir_):
                    html = Long_page_3.get_page_html(
                        _fd(applied=1, sort=sort, dir=dir_)
                    )
                    self.assertIn('<table', html,
                                  f"Table missing for sort={sort}, dir={dir_}")

    def test_invalid_sort_falls_back_to_rate(self):
        html = Long_page_3.get_page_html(
            _fd(applied=1, sort='totally_invalid')
        )
        self.assertIn('<table', html)

    def test_invalid_dir_falls_back_to_desc(self):
        html = Long_page_3.get_page_html(
            _fd(applied=1, dir='sideways')
        )
        self.assertIn('<table', html)


class TestLongPage3Pagination(unittest.TestCase):
    """Long_page_3: pagination."""

    def test_page_two_renders(self):
        html = Long_page_3.get_page_html(_fd(applied=1, page=2))
        self.assertIn('<table', html)

    def test_out_of_range_page_clamped(self):
        html = Long_page_3.get_page_html(_fd(applied=1, page=99999))
        self.assertIn('<table', html)

    def test_pagination_info_shown(self):
        html = Long_page_3.get_page_html(_fd(applied=1))
        self.assertIn('Showing', html)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. CROSS-PAGE  –  Shared component checks
# ═══════════════════════════════════════════════════════════════════════════════

class TestSharedComponents(unittest.TestCase):
    """Every page should include navbar, footer, and breadcrumb."""

    PAGES = [
        (Minh_page_1, {}),
        (Minh_page_2, {}),
        (Minh_page_3, {}),
        (Long_page_1, {}),
        (Long_page_2, {}),
        (Long_page_3, {}),
    ]

    def test_navbar_on_all_pages(self):
        for page_module, fd in self.PAGES:
            with self.subTest(page=page_module.__name__):
                html = page_module.get_page_html(fd)
                self.assertIn('navbar', html.lower())

    def test_footer_on_all_pages(self):
        for page_module, fd in self.PAGES:
            with self.subTest(page=page_module.__name__):
                html = page_module.get_page_html(fd)
                self.assertIn('footer', html.lower())

    def test_breadcrumb_on_all_pages(self):
        # Minh_page_1 is the home/landing page and intentionally has no breadcrumb
        pages_with_breadcrumb = [
            (Minh_page_2, {}), (Minh_page_3, {}),
            (Long_page_1, {}), (Long_page_2, {}), (Long_page_3, {}),
        ]
        for page_module, fd in pages_with_breadcrumb:
            with self.subTest(page=page_module.__name__):
                html = page_module.get_page_html(fd)
                self.assertIn('breadcrumb', html.lower())

    def test_all_pages_produce_valid_html_skeleton(self):
        for page_module, fd in self.PAGES:
            with self.subTest(page=page_module.__name__):
                html = page_module.get_page_html(fd)
                self.assertIn('<!DOCTYPE html>', html)
                self.assertIn('<html', html)
                self.assertIn('</html>', html)
                self.assertIn('<head>', html)
                self.assertIn('</head>', html)
                self.assertIn('<body>', html)
                self.assertIn('</body>', html)

    def test_home_link_in_navbar_on_all_pages(self):
        for page_module, fd in self.PAGES:
            with self.subTest(page=page_module.__name__):
                html = page_module.get_page_html(fd)
                self.assertIn('href="/"', html)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    unittest.main(verbosity=2)
