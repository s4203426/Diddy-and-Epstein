import pyhtml
import navbar
import footer

def get_page_html(form_data):
    print("About to return landing page (Minh_page_1)...")

    rows = pyhtml.get_results_from_query(
        "database/immunisation.db",
        """SELECT year, ROUND(AVG(coverage), 1)
           FROM Vaccination
           WHERE antigen = 'RCV1'
           AND year BETWEEN 2004 AND 2024
           AND coverage IS NOT NULL
           GROUP BY year ORDER BY year"""
    )

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_1.css">
    <link rel="stylesheet" href="footer.css">
</head>
<body>

    {navbar.get_navbar()}

    <!-- HERO SECTION -->
    <section class="hero">
        <div class="hero-left">
            <p class="hero-text">Explore 25 years of WHO immunization data across 217 countries – turning complex global health statistics into clear, actionable insights.</p>
            <a href="/Long_page_1" class="about-btn">About us</a>
        </div>
        <div class="hero-right">
            <img src="images\img_background.jpg" alt="Dashboard">
        </div>
    </section>

    <!-- FEATURES SECTION -->
    <section class="features">
        <div class="features-grid">

            <div class="feature-card">
                <h3 class="feature-title">Infection Data Across Different Economic Phases</h3>
                <p class="feature-desc">Explore how preventable disease cases vary across countries grouped by economic status – from developed to least developed nations – covering 25 years of WHO records (2000–2024).</p>
            </div>

            <div class="feature-card">
                <h3 class="feature-title">Global Infection Rates and Country Comparisons</h3>
                <p class="feature-desc">Discover the global infection rate per 100,000 people and identify countries whose rates exceed the global average – for any infection type and year.</p>
            </div>

            <div class="feature-card">
                <h3 class="feature-title">Compare Vaccination Rates by Country &amp; Region</h3>
                <p class="feature-desc">Build instant side-by-side comparisons of immunization coverage across any countries or WHO regions – visualize disparities between high-coverage and underserved areas at a glance.</p>
            </div>

            <div class="feature-card">
                <h3 class="feature-title">Track Vaccination Improvements Over 25 Years</h3>
                <p class="feature-desc">Discover which countries have made the biggest jumps in vaccination rates – from any starting year to any ending year between 2000 and 2024. Celebrate progress, learn from success stories.</p>
            </div>

        </div>
    </section>

    <!-- CHART SECTION -->
    <section class="chart-section">
        <h2 class="chart-title">Data show the Vaccine Coverage Rate in the world of Rubella (2004&#8211;2024)</h2>
        <div class="chart-container">
"""

    # --- Build SVG chart from rows ---
    svg_w, svg_h = 900, 400
    lp, tp, rp, bp = 60, 40, 30, 50          # left/top/right/bottom padding
    cw = svg_w - lp - rp                      # chart area width
    ch = svg_h - tp - bp                      # chart area height
    n  = len(rows)

    coords = []
    for i, (year, value) in enumerate(rows):
        x = lp + (i / (n - 1)) * cw
        y = tp + (1 - value / 100) * ch
        coords.append((round(x, 1), round(y, 1), year, value))

    area_d = f"M {coords[0][0]},{coords[0][1]} "
    area_d += " ".join(f"L {x},{y}" for x, y, _, _ in coords[1:])
    area_d += f" L {coords[-1][0]},{tp+ch} L {coords[0][0]},{tp+ch} Z"

    line_d = f"M {coords[0][0]},{coords[0][1]} "
    line_d += " ".join(f"L {x},{y}" for x, y, _, _ in coords[1:])

    page_html += f'<svg viewBox="0 0 {svg_w} {svg_h}" style="width:100%;display:block">'

    # Grid lines + Y-axis labels
    for pct in [0, 20, 40, 60, 80, 100]:
        gy = tp + (1 - pct / 100) * ch
        page_html += f'<line x1="{lp}" y1="{gy}" x2="{lp+cw}" y2="{gy}" stroke="#e0e0e0" stroke-width="1"/>'
        page_html += f'<text x="{lp-6}" y="{gy+4}" text-anchor="end" font-size="11" fill="#666">{pct}%</text>'

    # Area fill + line
    page_html += f'<path d="{area_d}" fill="rgba(68,114,196,0.15)"/>'
    page_html += f'<path d="{line_d}" fill="none" stroke="#4472C4" stroke-width="2"/>'

    # Data points + labels + X-axis labels
    for x, y, year, value in coords:
        page_html += f'<circle cx="{x}" cy="{y}" r="4" fill="#4472C4"/>'
        page_html += f'<text x="{x}" y="{y-9}" text-anchor="middle" font-size="10" font-weight="bold" fill="#333">{value}%</text>'
        page_html += f'<text x="{x}" y="{tp+ch+18}" text-anchor="middle" font-size="10" fill="#666">{year}</text>'

    page_html += "</svg>"

    page_html += """
        </div>
    </section>

"""
    page_html += footer.get_footer()
    page_html += """
</body>
</html>
"""
    return page_html
