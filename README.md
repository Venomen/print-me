# Print Me – Web Print Server

A web application that allows you to send files for printing via your browser. Supports PDF, Word, and Excel files, and lets you choose print quality, paper size, and page range for each file.

## Features

- Upload multiple files for printing via a web form
- Supports PDF, DOC, DOCX, XLS, XLSX files (Word/Excel are converted to PDF)
- Select paper size (A4, Letter, Legal)
- Select print quality (draft, normal, high)
- Specify page range for each file
- View the print job queue

## Requirements

### Python Dependencies

- Python 3.7+
- Flask
- Flask-WTF
- WTForms
- Werkzeug

Install Python dependencies:
```sh
pip install -r requirements.txt
```

### System Dependencies

- **LibreOffice** – for converting Word/Excel files to PDF
- **CUPS** (lp, lpstat) – for printing and managing the print queue

#### Installation on macOS (Homebrew):

```sh
brew install --cask libreoffice
brew install cups
```

#### Installation on Ubuntu/Debian:

```sh
sudo apt update
sudo apt install libreoffice cups
```

## Running the Application

1. Install Python dependencies:
    ```sh
    pip install -r requirements.txt
    ```
2. Install LibreOffice and CUPS (see above).
3. Start the application:
    ```sh
    python app.py
    ```
4. Open your browser and go to [http://localhost:8000](http://localhost:8000)

## Project Structure

```
print-me/
├── app.py
├── requirements.txt
└── templates/
    ├── upload.html
    └── job_list.html
```

## Security

- The default `SECRET_KEY` is set to a test value – change it before deploying to production.
- The application does not have authentication – do not run it in a public environment without additional security.

## License

MIT