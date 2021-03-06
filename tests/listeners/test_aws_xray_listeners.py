from thundra.opentracing.tracer import ThundraTracer
from thundra import constants
from aws_xray_sdk.core import xray_recorder


def test_annotation_metadata_and_tags(handler_with_xray_testing, mock_event, mock_context):
    thundra, handler = handler_with_xray_testing
    tracer = ThundraTracer.get_instance()
    document = handler(mock_event, mock_context)
    xray_recorder.end_segment()
    data = tracer.test_xray_traces[-1]
    xray = data['xray']
    span = data['span']
    # Testing span values
    assert xray['name'] == span['operation_name']
    assert constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME'] in span['tags']
    # Testing annotation values
    assert xray['annotations']['spanId'] == span['_context'].span_id
    assert xray['annotations']['applicationVersion'] == 'function_version'
    assert xray['annotations']['applicationRuntime'] == 'python'
    assert xray['annotations']['applicationRuntimeVersion'] == '3'
    assert xray['annotations']['applicationStage'] == 'dev'
    # Testing metadata
    assert xray['metadata']['default'][constants.AwsXrayConstants['XRAY_SUBSEGMENTED_TAG_NAME']] == True
    tracer.test_xray_traces.clear()
    tracer.recorder.listeners.clear()
    tracer.clear()
