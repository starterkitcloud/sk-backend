FROM python:3
WORKDIR /webapp/app/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ADD ./ /webapp/
