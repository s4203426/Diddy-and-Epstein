import pyhtml
import os

def get_page_html(form_data):
    print("About to return landing page (Minh_page_1)...")

    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Minh_page_1.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Vaccination & Infection Tracker</title>
    <style>{css_content}</style>
</head>
<body>

    <!-- NAVIGATION BAR -->
    <nav class="navbar">

        <!-- Logo (click to return to landing page) -->
        <div class="navbar-logo">
            <a href="/">
                <img src="images/Logo.png" alt="Logo">
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
        <div class="hero-overlay">
            <h1 class="hero-title">Vaccination &amp; Infection Tracker</h1>
            <p class="hero-subtitle">
                Explore real-time data on vaccination rates and infection trends
                to stay informed and help protect your community.
            </p>
        </div>
    </section>

</body>
</html>
"""
    return page_html
