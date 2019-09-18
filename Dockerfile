FROM python:3
ADD flask_dd_trace.py /
ADD db_config.py /
ADD requirements.txt /
# ENV DB_HOST <DB_HOST>
# ENV DB_USERNAME <DB_USERNAME>
# ENV DB_PASSWORD <DB_PASSWORD>
# ENV DB_NAME <DB_NAME>
RUN pip install -r requirements.txt
CMD [ "DATADOG_SERVICE_NAME=kikeyama-flask", "ddtrace-run", "python", "./flask_dd_trace.py" ]
