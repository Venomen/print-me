import os
import io
import tempfile
import subprocess
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectField, SubmitField, StringField
from wtforms.validators import DataRequired, Optional, Regexp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this for production security

# Paper sizes, print quality, and default page range
PAPER_SIZES = ['A4', 'Letter', 'Legal']
PRINT_QUALITIES = ['draft', 'normal', 'high']
DEFAULT_PAGE_RANGE = "all"

# Form for file upload and print settings
class PrintForm(FlaskForm):
    files = MultipleFileField('Select files', validators=[DataRequired()])
    paper_size = SelectField('Paper size', choices=[(p, p) for p in PAPER_SIZES], default='A4')
    print_quality = SelectField('Print quality', choices=[(q, q) for q in PRINT_QUALITIES], default='normal')
    submit = SubmitField('Print')

def convert_to_pdf(file_stream, file_extension):
    """Converts a Word (.doc, .docx) or Excel (.xls, .xlsx) file to PDF using LibreOffice."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(file_stream.read())
        temp_file_path = temp_file.name

    temp_pdf_path = temp_file_path.replace(f".{file_extension}", ".pdf")

    try:
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", temp_file_path, "--outdir", os.path.dirname(temp_file_path)],
            check=True
        )
        return temp_pdf_path
    except subprocess.CalledProcessError:
        return None
    finally:
        os.unlink(temp_file_path)  # Remove the temporary input file

def print_file(file_stream, file_name, paper_size, print_quality, page_range):
    """Prints a file directly from memory, converting it if necessary."""
    file_extension = file_name.lower().split(".")[-1]

    # Convert Word and Excel files to PDF before printing
    if file_extension in ["xlsx", "xls", "doc", "docx"]:
        pdf_path = convert_to_pdf(file_stream, file_extension)
        if pdf_path:
            print_pdf(pdf_path, paper_size, print_quality, page_range)
            os.unlink(pdf_path)  # Delete the temporary PDF after printing
            return "Printed"
        else:
            return "Error converting file to PDF"

    process = subprocess.Popen(
        ["lp", "-o", f"media={paper_size}", "-o", f"print-quality={print_quality}"],
        stdin=subprocess.PIPE
    )
    process.communicate(input=file_stream.read())
    return "Printed"

def print_pdf(pdf_path, paper_size, print_quality, page_range):
    """Prints a PDF with optional page range."""
    lp_command = ["lp", "-o", f"media={paper_size}", "-o", f"print-quality={print_quality}"]

    # If user specified a page range, add it to the command
    if page_range and page_range.lower() != "all":
        lp_command.extend(["-o", f"page-ranges={page_range}"])

    lp_command.append(pdf_path)
    subprocess.run(lp_command, check=True)

@app.route("/", methods=["GET", "POST"])
def upload():
    """Handles file upload and printing."""
    form = PrintForm()
    if form.validate_on_submit():
        page_ranges = request.form.getlist("page_ranges[]")  # getting page ranges from the form

        for index, file in enumerate(form.files.data):
            if file:
                file_stream = io.BytesIO(file.read())
                page_range = page_ranges[index] if index < len(page_ranges) else "all"
                status = print_file(file_stream, file.filename, form.paper_size.data, form.print_quality.data, page_range)
                file_stream.close()
                if status == "Error":
                    flash(f"Error printing {file.filename}", "danger")

        flash("Files have been sent to the printer!", "success")
        return redirect(url_for("job_list"))

    return render_template("upload.html", form=form)

@app.route("/jobs")
def job_list():
    """Displays the list of pending print jobs."""
    result = subprocess.run(["lpstat", "-o"], capture_output=True, text=True)
    jobs = result.stdout.split("\n") if result.stdout else []
    return render_template("job_list.html", jobs=jobs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
