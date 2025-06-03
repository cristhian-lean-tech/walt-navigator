# FastAPI Chroma App

## Overview

The FastAPI Chroma App is a web application built using FastAPI that integrates Chroma DB for managing embeddings. This project provides a clean architecture with clearly separated concerns, making it easy to maintain and extend.

## Project Structure

```
fastapi-chroma-app
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── api
│   │   ├── __init__.py
│   │   └── endpoints
│   │       └── embeddings.py
│   ├── core
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db
│   │   ├── __init__.py
│   │   └── chroma.py
│   └── models
│       ├── __init__.py
│       └── embedding.py
├── requirements.txt
└── README.md
```

## Installation

To get started with the FastAPI Chroma App, follow these steps:

1. Clone the repository:

   ```
   git clone <repository-url>
   cd fastapi-chroma-app
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

**To run the FastAPI application, execute the following command:**

```
uvicorn app.main:app --reload
```

This will start the server at `http://127.0.0.1:8000`.

**Using docker:**
build the image:

```
docker build -t walt-path .
```

run the container:

```
docker run --rm --name walt-path -p 8000:8000 -v .:/app walt-path
```

## API Endpoints

The application exposes several API endpoints for managing embeddings. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
