import os

app_redis_hostname = os.environ.get('REDIS_HOST')
app_redis_port     = int(os.environ.get('REDIS_PORT'))
app_algorithm_name = str(os.environ.get('ALGORITHM_NAME'))
app_algorithm_version = str(os.environ.get('ALGORITHM_VERSION'))

app_algorithm_full_name = app_algorithm_name + '_' + app_algorithm_version
lower_name = app_algorithm_full_name.replace('-', '_').replace('.',  '_').lower()
upper_name = app_algorithm_full_name.replace('-', '_').replace('.',  '_').upper()


app_info_key = '{}_INFO_KEY'.format(upper_name)
app_response_key = '{}_RESPONSE_KEY'.format(upper_name)
app_error_key = '{}_ERROR_KEY'.format(upper_name)

app_kafka_host = os.environ.get('KAFKA_HOST')
app_kafka_topic = '{}_queue'.format(lower_name)
app_kafka_key = '{}_requests'.format(lower_name)
app_group_id  = 'calculator'

app_storage_host = os.environ.get('STORAGE_HOST')

call_interval  = 1
sleep_interval = 7


# --------------
print('app_redis_hostname', app_redis_hostname)
print('app_redis_port', app_redis_port)
print('app_algorithm_name', app_algorithm_name)
print('app_algorithm_version',  app_algorithm_version)
print('app_info_key', app_info_key)
print('app_response_key', app_response_key)
print('app_error_key', app_error_key)
print('app_kafka_host', app_kafka_host)
print('app_kafka_topic', app_kafka_topic)
print('app_kafka_key', app_kafka_key)
print('app_storage_host', app_storage_host)
# --------------