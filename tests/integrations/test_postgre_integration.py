
import psycopg2

from thundra.opentracing.tracer import ThundraTracer
from thundra import constants

connection = psycopg2.connect(
    host='thundra-demo.cdmxpwxmxdtn.us-west-2.rds.amazonaws.com',
    dbname='thundra_demo',
    user='thundra',
    password='thundra1234')  # create the connection

cursor = connection.cursor()  # get the cursor


def test_mysql_integration():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"

    cursor.execute(query)
    for table in cursor.fetchall():
        print(table)

    tracer = ThundraTracer.get_instance()
    postgre_span = tracer.recorder.finished_span_stack[0]

    assert postgre_span.get_tag(constants.SpanTags['SPAN_TYPE']) == constants.SpanTypes['RDB']
    assert postgre_span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
    assert postgre_span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'thundra_demo'
    assert postgre_span.get_tag(constants.SpanTags['DB_URL']) == 'thundra-demo.cdmxpwxmxdtn.us-west-2.rds.amazonaws.com'
    assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT']) == query.lower()
    assert postgre_span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'select'
    assert postgre_span.get_tag(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'AWS-Lambda'
    assert postgre_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'API'

    tracer.clear()