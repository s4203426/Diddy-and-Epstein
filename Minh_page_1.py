import pyhtml
import navbar

def get_page_html(form_data):
    print("About to return landing page (Minh_page_1)...")

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="Minh_page_1.css">
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

</body>
</html>
"""
    return page_html
