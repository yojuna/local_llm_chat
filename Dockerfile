# The builder image, used to build the virtual environment
FROM python:3.11-buster as builder

RUN apt-get update && apt-get install -y git

# A directory to have app data 
WORKDIR /app

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./ ./app

CMD ["streamlit", "run", "hackmining_recommender_chatbot.py", "--server.port", "8051"]