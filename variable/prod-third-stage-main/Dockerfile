FROM python

COPY . .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "-m", "travel_agent"]
