import pyhtml
def get_page_html(form_data):
    print("About to return page 2")
    
    page_html=f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Reading from a .db file</title>
    <style>
    table {{
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    }}

    td, th {{
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
    }}

    tr:nth-child(even) {{
    background-color: #dddddd;
    }}
    </style>
    </head>
    <body>
        <h1>Example of retrieving data from a .db file...</h1>
    """
    sql_query = "select * from movie;"
    page_html+= f"<h2>Result from \"{sql_query}\"</h2>"
    
    #Run the query in sql_query and get the results
    results = pyhtml.get_results_from_query("database/movies.db",sql_query)
    
    #Adding results to the web page without any beautification. Try turning it into a nice table!
    page_html+="""
    <table>
    <tr>
        <th>MVNUMB</th>
        <th>MVTITLE</th>
        <th>YRMDE</th>
        <th>MVTYPE</th>
        <th>CRIT</th>
        <th>MPAA</th>
        <th>NOMS</th>
        <th>AWRD</th>
        <th>DIRNUMB</th>
    </tr>
    """

    for row in results:
        page_html+="<tr>"
        for value in row:
            page_html+=f"<td>{value}</td>"
        page_html+="<tr>"   

    page_html+="</table>"     

    
    
    page_html+="""
        <p><a href="/">Go back to home page</a></p>
    </body>
    </html>
    """
    return page_html