import pyhtml
import navbar
import footer

def get_page_html(form_data):
    print("About to return Minh_Page_3")

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

    {footer.get_footer()}

</body>
</html>
"""
    return page_html