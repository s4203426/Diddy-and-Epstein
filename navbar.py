def get_navbar():
    return """
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
    """
