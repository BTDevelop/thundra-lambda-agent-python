import mysql.connector
from thundra.opentracing.tracer import ThundraTracer
from thundra import constants

connection = mysql.connector.connect(
    user='admin',
    host='thundra-db-staging.cdmxpwxmxdtn.us-west-2.rds.amazonaws.com',
    password='Thundra0ops',
    database='thundra_db_lab')

cursor = connection.cursor()


def test_mysql_integration():
    query = "select * from users where id='4af58645-7b31-499a-9a58-bc187ba91d26'"
    cursor.execute(query)

    tracer = ThundraTracer.get_instance()
    mysql_span = tracer.recorder.finished_span_stack[0]

    assert mysql_span.get_tag(constants.SpanTags['SPAN_TYPE']) == constants.SpanTypes['RDB']
    assert mysql_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
    assert mysql_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'thundra_db_lab'
    assert mysql_span.get_tag(constants.SpanTags['DB_URL']) == 'thundra-db-staging.cdmxpwxmxdtn.us-west-2.rds.amazonaws.com'
    assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
    assert mysql_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'select'
    assert mysql_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'AWS-Lambda'
    assert mysql_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'API'

    tracer.clear()
