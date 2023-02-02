import os

import pdfkit


def generate_html_table(columns, values):
    """Generates a HTML table with columns as headers and values"""

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MARKS SHEET USING HTML TABLES</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="Keywords" content="html, css, html tables, table">
        <meta name="Description" content="Fynd Academy 2023">
        <!-- add icon -->
        <link rel="icon" href="/favicon.ico" type="image/x-icon">
        <link href='http://fonts.googleapis.com/css?family=Lato:400,700' rel='stylesheet' type='text/css'>
        <style type="text/css">
            body{
            background-color: #c5cae9;
            padding: 25px;
            }
            .container{
            width: 720px;
            height: 440px;
            margin: 0 auto;
            padding-left: 32px;
            padding-right: 32px;
            padding-top: 40px;
            border-radius: 12px;
            background-color: #90a4ae;
            font-family: Lato;
            }
            .container h2{
            text-align: center;
            }
            table{
            margin: 0 auto;
            }
            td, th {
            padding: 12px;
            border: 2px dotted;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Fynd Academy 2023</h2>
            <table>
                <thead>
                <tr>
    """

    for column in columns:
        html += f"<th>{column}</th>"

    html += """
               <tr>  
            </thead>
            <tbody>
               <tr>
    """

    for value in values:
        html += f"<td>{value}</td>"

    html += """
                </tr>
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    return html


def generate_pdf(filepath, columns, values):
    """
    Generates a HTML Table and converts stores it to a file,
    generates a pdf from that HTML file and returns the pdf_filepath
    """

    html_table = generate_html_table(columns, values)

    with open(filepath, "w") as file_handler:
        file_handler.write(html_table)

    pdf_filepath = os.path.splitext(filepath)[0] + ".pdf"
    pdfkit.from_file(filepath, pdf_filepath)

    return pdf_filepath
