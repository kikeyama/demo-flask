from flask import Flask
from flask import request as flask_request
#import logging
import sys
import blinker as _
import time

import mysql.connector
import json

from logging.config import dictConfig

# DogStatsD
from datadog import statsd

# DB Config
import db_config

## Have flask use stdout as the logger
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '- %(message)s')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': FORMAT,
    }},
    'handlers': {'console': {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'default',
        'stream': 'ext://sys.stdout'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
})

## Connecting MySQL
mydb = mysql.connector.connect(
    host=db_config.db_host,
    user=db_config.db_username,
    passwd=db_config.db_password,
    database=db_config.db_name
)
mycursor = mydb.cursor()

## Flask
app = Flask(__name__)

@app.route('/')
def api_entry():
    start_time = time.time()

    app.logger.info('getting root endpoint')
#    return 'Entrypoint to the Application'
    name = flask_request.args.get('name', str)
    mycursor.execute("SELECT Name, UUID, Number FROM kikeyama_table where name='%s'" % name)
    myresult = mycursor.fetchall()
    
    for x in myresult:
        result = json.dumps(x)
        return result

    duration = time.time() - start_time
    statsd.distribution('kikeyama.dogstatsd.distribution.latency', duration)
    statsd.histogram('kikeyama.dogstatsd.histogram.latency', duration)

@app.route('/api/apm')
def apm_endpoint():
    app.logger.info('getting apm endpoint')
    return 'Getting APM Started'

@app.route('/api/trace')
def trace_endpoint():
    app.logger.info('getting trace endpoint')
    return 'Posting Traces'

@app.route('/api/post', methods=['POST'])
def post_endpoint():
    app.logger.info('posting message: ' + flask_request.form['message'])
    return flask_request.form['message']

@app.route('/lambda')
def lambda_endpoint():
    app.logger.info('getting lambda endpoint')
    q = {'TableName': 'kikeyama-dynamodb'}
    r = requests.get('https://8m92rdlm25.execute-api.us-east-1.amazonaws.com/demo/lambda', headers={
        'x-datadog-trace-id': str(tracer.current_span().trace_id),
        'x-datadog-parent-id': str(tracer.current_span().span_id),
    }, params=q)
    dict_r = json.loads(r.text)
    if dict_r['ResponseMetadata']['HTTPStatusCode'] == 200:
        app.logger.info('lambda call: Returned ' + str(dict_r['Count']) + ' results with RequestId: ' + dict_r['ResponseMetadata']['RequestId'])
    return 'Lambda Traces'

if __name__ == '__main__':
    app.logger.info('%(message)s This is __main__ log')
    app.run(host='0.0.0.0', port='5050')
