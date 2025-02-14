## Instructions Assistant Assistant

Instructions Assistant is a web application that helps users follow assembly instructions by analyzing images from a PDF manual and a webcam feed. It provides step-by-step guidance for assembling products.

## Features

- Upload a PDF instruction manual
- Capture images from a webcam
- Analyze the current assembly state and provide the next step
- Uses OpenAI's API for image analysis

## Purpose

This project was developed for a robotics team to assist new members with understanding and following complex build instructions. It simplifies the process of assembling intricate hardware by providing clear, step-by-step guidance, ensuring that even those unfamiliar with the components can successfully complete the builds.

## Prerequisites

- Python 3.7+
- [Poppler](https://poppler.freedesktop.org/) (for `pdf2image` to work)
  - On Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - On macOS: `brew install poppler`
  - On Windows: [Download and install poppler binaries](http://blog.alivate.com.au/poppler-windows/)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dicerollcodes/instructions-assistant.git
   cd instructions-assistant
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the root directory:
     ```text
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

1. **Run the application:**
   ```bash
   python app.py
   ```

2. **Open your browser and go to:**
   ```
   http://127.0.0.1:5000
   ```

3. **Upload a PDF and capture an image:**
   - Upload your instruction manual in PDF format.
   - Use your webcam to capture the current state of your assembly.

4. **Get instructions:**
   - The application will analyze the images and provide the next step in the assembly process.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [OpenAI](https://openai.com/)
- [pdf2image](https://github.com/Belval/pdf2image)
- [Pillow](https://python-pillow.org/)
