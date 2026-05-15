import pyhtml
import navbar

def get_page_html(form_data):
    print("About to return Long_page_1 (Mission Statement)")

    personas = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT name, description, image FROM Personas"
    )

    team_members = pyhtml.get_results_from_query(
        "database/immunisation.db",
        "SELECT name, student_number, image FROM TeamMembers"
    )

    personas_html = ""
    for name, description, image in personas:
        personas_html += f"""
        <div class="persona-block">
            <h3 class="persona-type">{name}</h3>
            <p class="persona-desc">{description}</p>
            <div class="persona-card">
                <img src="{image}" alt="{name}" class="persona-img">
                <div class="persona-card-right">
                    <div class="persona-name-banner">{name}</div>
                    <p class="persona-card-desc">{description}</p>
                </div>
            </div>
        </div>
        """

    team_html = ""
    for name, student_number, image in team_members:
        team_html += f"""
        <div class="team-card">
            <div class="team-photo-wrap">
                <img src="{image}" alt="{name}">
            </div>
            <p class="team-name">{name}</p>
            <p class="team-id">{student_number}</p>
        </div>
        """

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mission Statement - Vaccination & Infection Tracker</title>
    <link rel="stylesheet" href="navbar.css">
    <link rel="stylesheet" href="Minh_page_1.css">
    <link rel="stylesheet" href="Long_page_1.css">
</head>
<body>

    {navbar.get_navbar()}

    <!-- MISSION BANNER -->
    <div class="mission-banner">
        <h1>Mission Statement</h1>
    </div>

    <!-- PAGE WRAPPER -->
    <div class="page-wrapper">

        <!-- LEFT: Main content -->
        <main class="mission-content">

            <section id="our-purpose">
                <h2>Our Purpose</h2>
                <p>We built this website to make immunisation and preventable disease data easier for real people to understand. Public health data is often hard to read because it is spread across many tables, countries, years, diseases, and economic groups. Our goal is to bring this information together in one clear place so people can explore it without needing to be a data expert.</p>
                <p>This website does not try to push one opinion. Instead, it helps people see the data clearly, compare patterns, and better understand how vaccination and infection trends affect communities around the world.</p>
            </section>

            <section id="how-it-helps">
                <h2>How This Website Helps</h2>
                <p>This website helps users turn complex immunisation data into useful information. Users can explore infection rates, vaccination coverage, countries, regions, years, and economic status through simple filters and organised results.</p>
                <p>For example, users can check how infection cases differ between countries, compare disease trends across economic groups, or identify countries where infection rates are higher than the global average. This can support people who need quick facts, deeper analysis, or trustworthy information for reporting, learning, and public awareness.</p>
            </section>

            <section id="how-to-use">
                <h2>How to Use This Website</h2>
                <p>Start by choosing the type of information you want to explore. You can select a year, disease type, country, region, or economic status depending on the page you are using.</p>
                <p>After selecting your options, the website will show the relevant data in a clear table or summary. You can use these results to compare countries, understand trends, and identify areas where preventable diseases remain a concern.</p>
                <p>The website is designed for both quick viewing and deeper investigation, so users can either get a simple overview or explore more detailed data when needed.</p>
            </section>

            <section id="who-its-for">
                <h2>Who This Website Is For</h2>
                {personas_html}
            </section>

            <section id="our-team">
                <h2>Our Team</h2>
                <div class="team-grid">
                    {team_html}
                </div>
            </section>

        </main>

        <!-- RIGHT: Table of Contents -->
        <div class="toc">
            <h3>Table of Contents</h3>
            <ol>
                <li><a href="#our-purpose">Our Purpose</a></li>
                <li><a href="#how-it-helps">How This Website Helps</a></li>
                <li><a href="#how-to-use">How to Use This Website</a></li>
                <li><a href="#who-its-for">Who This Website Is For</a>
                    <ol>
                        <li><a href="#who-its-for">Journalists and Data Reporters</a></li>
                        <li><a href="#who-its-for">Policy Makers</a></li>
                    </ol>
                </li>
                <li><a href="#our-team">Our Team</a></li>
            </ol>
        </div>

    </div>

</body>
</html>"""
    return page_html
