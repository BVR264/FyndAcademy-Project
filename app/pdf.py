import pdfkit
import os


def generate_html_table(columns, values):

    html = """
    <table border="1" class="dataframe">
    <thead>
    <tr style="text-align: right;">
    """

    for column in columns:
        html += f"<th>{column}</th>"

    html += """
        </tr>
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
    """

    return html


def generate_pdf(filepath, columns, values):

    html_table = generate_html_table(columns, values)

    with open(filepath, "w") as file_handler:
        file_handler.write(html_table)

    pdf_filepath = os.path.splitext(filepath)[0] + ".pdf"
    pdfkit.from_file(filepath, pdf_filepath)

    return pdf_filepath
