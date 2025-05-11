FROM python:3.11.12

WORKDIR /work
COPY requirements.txt /work
RUN pip install -r requirements.txt

ENTRYPOINT exec streamlit run src/main.py --server.port 8080
