FROM python

WORKDIR /bot

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 80

COPY . .

CMD [ "python3", "main.py"]