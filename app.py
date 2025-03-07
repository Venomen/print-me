import subprocess
import io
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectField, SubmitField
from wtforms.validators import DataRequired

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change to a secure key

# Paper sizes and print quality options
PAPER_SIZES = ['A4', 'Letter', 'Legal']
PRINT_QUALITIES = ['draft', 'normal', 'high']

# Form for file upload and print settings
class PrintForm(FlaskForm):
    files = MultipleFileField('Select files', validators=[DataRequired()])
    paper_size = SelectField('Paper size', choices=[(p, p) for p in PAPER_SIZES], default='A4')
    print_quality = SelectField('Print quality', choices=[(q, q) for q in PRINT_QUALITIES], default='normal')
    submit = SubmitField('Print')

# Function to send file directly to `lp` (without saving it locally)
def print_file(file_stream, paper_size, print_quality):
    """Prints a file directly from memory without saving it to disk."""
    try:
        process = subprocess.Popen(
            ["lp", "-o", f"media={paper_size}", "-o", f"print-quality={print_quality}"],
            stdin=subprocess.PIPE
        )
        process.communicate(input=file_stream.read())  # Send binary data to printer
        return "Printed"
    except subprocess.CalledProcessError:
        return "Error"

# Home page - File upload
@app.route("/", methods=["GET", "POST"])
def upload():
    form = PrintForm()
    if form.validate_on_submit():
        for file in form.files.data:
            if file:
                file_stream = io.BytesIO(file.read())  # Read file into memory
                status = print_file(file_stream, form.paper_size.data, form.print_quality.data)
                file_stream.close()
                if status == "Error":
                    flash(f"Error printing {file.filename}", "danger")

        flash("Files have been sent to the printer!", "success")
        return redirect(url_for("job_list"))

    return render_template("upload.html", form=form)

# Print job list page
@app.route("/jobs")
def job_list():
    """Displays the list of pending print jobs."""
    result = subprocess.run(["lpstat", "-o"], capture_output=True, text=True)
    jobs = result.stdout.split("\n") if result.stdout else []
    return render_template("job_list.html", jobs=jobs)

# Start the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
