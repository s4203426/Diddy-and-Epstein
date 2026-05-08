import pyhtml

def get_page_html(form_data):
    print("About to return landing page (Minh_page_1)...")

    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="Minh_page_1.css">
</head>
<body>

    <!-- NAVIGATION BAR -->
    <nav class="navbar">

        <!-- Logo (click to return to landing page) -->
        <div class="navbar-logo">
            <a href="/">
                <img src="images\Logo.png" alt="Logo">
            </a>
        </div>

        <!-- Navigation Links -->
        <ul class="navbar-links">

            <li><a href="/">Home</a></li>

            <li><a href="/Long_page_1">Mission</a></li>

            <!-- Vaccination Data dropdown -->
            <li class="dropdown">
                <a href="#">Vaccination Data</a>
                <div class="dropdown-content">
                    <a href="/Minh_page_2">Vaccination Data 1</a>
                    <a href="/Minh_page_3">Vaccination Data 2</a>
                </div>
            </li>

            <!-- Infection Data dropdown -->
            <li class="dropdown">
                <a href="#">Infection Data</a>
                <div class="dropdown-content">
                    <a href="/Long_page_2">Infection Data 1</a>
                    <a href="/Long_page_3">Infection Data 2</a>
                </div>
            </li>

            <li><a href="/Long_page_1" class="contact-btn">Contact</a></li>

        </ul>
    </nav>

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
