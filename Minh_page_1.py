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

</body>
</html>
"""
    return page_html
