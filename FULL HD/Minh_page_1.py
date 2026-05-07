def get_page_html(form_data):
    print("About to return page home page...")
    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaccination Dashboard</title>
    <link rel="stylesheet" href="/minh_page_1.css">
</head>
<body>

<!-- ---------------------------- THIS IS THE NAVIGATION BAR-------------------- -->
    <nav class="navbar">
        <!-- Logo (click returns to landing page) -->
        <div class="navbar-logo">
            <a href="/"><img src="/images/Logo.png" alt="Logo"></a>
        </div>

        <!-- Nav Links -->
        <ul class="navbar-links">
            <li><a href="/">Home</a></li>

            <li><a href="/Long_page_1">Mission</a></li>

            <li class="dropdown">
                <a href="#">Vaccination Data &#9660;</a>
                <div class="dropdown-content">
                    <a href="/Minh_page_2">Vaccination Page 2</a>
                    <a href="/Minh_page_3">Vaccination Page 3</a>
                </div>
            </li>
            
            <li class="dropdown">
                <a href="#">Infection Data &#9660;</a>
                <div class="dropdown-content">
                    <a href="/Long_page_2">Infection Page 2</a>
                    <a href="/Long_page_3">Infection Page 3</a>
                </div>
            </li>
        </ul>

        <!-- Contact Button -->
        <div class="navbar-contact">
            <a href="/Long_page_1">Contact</a>
        </div>
    </nav>
    <p> hello</p>    
    </body>
    </html>
    """
    return page_html