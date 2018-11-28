import abc
import time
import traceback
from thundra.opentracing.tracer import ThundraTracer


class BaseIntegration(abc.ABC):

    _OPERATION_TO_TABLE_NAME_KEYWORD = {
        'select': 'from',
        'insert': 'into',
        'update': 'update',
        'delete': 'from',
        'create': 'table'
    }

    _OPERATION_TO_TYPE = {
        'select': 'READ',
        'insert': 'WRITE',
        'update': 'WRITE',
        'delete': 'DELETE'
    }

    @staticmethod
    def _extract_table_name(query, operation):
        if operation in BaseIntegration._OPERATION_TO_TABLE_NAME_KEYWORD:
            keyword = BaseIntegration._OPERATION_TO_TABLE_NAME_KEYWORD[operation]
            query_words = query.lower().split()
            if keyword in query_words:
                return query.split()[query_words.index(keyword) + 1]
        return ''

    def set_exception(self, exception, traceback_data, span):
        span.set_tag('error.stack', traceback_data)
        span.set_error_to_tag(exception)

    def create_span(self, wrapped, instance, args, kwargs):
        tracer = ThundraTracer.get_instance()
        response = None
        exception = None

        with tracer.start_active_span(operation_name=self.get_operation_name(), finish_on_close=True) as scope:
            try:
                response = wrapped(*args, **kwargs)
                return response
            except Exception as operation_exception:
                exception = operation_exception
                raise
            finally:
                try:
                    self.inject_span_info(scope, wrapped, instance, args, kwargs, response, exception)
                except Exception as instrumentation_exception:
                    error = {
                        'type': str(type(instrumentation_exception)),
                        'message': str(instrumentation_exception),
                        'traceback': traceback.format_exc(),
                        'time': time.time()
                    }
                    traceback.print_exc()
                    scope.span.set_tag('instrumentation_error', error)

    @abc.abstractmethod
    def get_operation_name(self):
        raise Exception("should be implemented")


    @abc.abstractmethod
    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response, exception):
        raise Exception("should be implemented")