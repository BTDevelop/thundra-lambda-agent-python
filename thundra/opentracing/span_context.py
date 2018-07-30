import opentracing
from threading import Lock

class ThundraSpanContext(opentracing.SpanContext):
    def __init__(self,
                 trace_id=None,
                 span_id=None,
                 parent_span_id=None,
                 baggage=None):
        self._trace_id = trace_id
        self._span_id = span_id
        self._parent_span_id = parent_span_id
        self._baggage = baggage or opentracing.SpanContext.EMPTY_BAGGAGE
        self._lock = Lock()

    @property
    def trace_id(self):
        with self._lock:
            return self._trace_id

    @property
    def span_id(self):
        with self._lock:
         return self._span_id

    @span_id.setter
    def span_id(self, value):
        self._span_id = value

    @property
    def parent_span_id(self):
        with self._lock:
            return self._parent_span_id

    @property
    def baggage(self):
        return self._baggage

    def context_with_baggage_item(self, key, value):
        new_baggage_item = self.baggage.copy()
        new_baggage_item[key] = value
        return ThundraSpanContext(trace_id=self.trace_id,
                                  span_id=self.span_id,
                                  parent_span_id=self.parent_span_id,
                                  baggage=new_baggage_item)
