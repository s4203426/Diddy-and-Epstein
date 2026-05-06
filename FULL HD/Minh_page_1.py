def get_page_html(form_data):
    print("About to return page home page...")
    page_html="""<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Database Web-App Demo</title>
    </head>
    <body>
        <h1>Welcome to Minh_page_1</h1>
        <p>This is the first dynamically generated page!</p>
        <p><a href="/Minh_page_2">Go to Minh Page 2</a></p>
        <p><a href="/Minh_page_3">Go to Minh Page 3</a></p>

        <p><a href="/Long_page_1">Go to Long Page 1</a></p>
        <p><a href="/Long_page_2">Go to Long Page 2</a></p>
        <p><a href="/Long_page_3">Go to Long Page 3</a></p>

        
        <p>hello </p>
        <h1>haha </h1>
        
    </body>
    </html>
    """
    return page_html