FROM python

WORKDIR /bot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 5050

COPY . .

CMD [ "python3", "main.py"]