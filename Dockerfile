FROM python:3.14

WORKDIR /PythonLrUnitTest
COPY . .
RUN pip install fastapi uvicorn sqlalchemy pydantic
CMD ["python", "-m", "uvicorn", "apif:app", "--host", "0.0.0.0", "--port", "8000"]