FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install requests python-binance coinbase
CMD ["python", "trade.py", "BCCBTC"]
