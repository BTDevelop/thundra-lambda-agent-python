import os
import sys, inspect
from urllib.parse import urlparse
from thundra import constants
from inspect import getmembers, isfunction

def get_configuration(key, default=None):
    return os.environ.get(key, default=default)


def should_disable(disable_by_env, disable_by_param=False):
    if disable_by_env == 'true':
        return True
    elif disable_by_env == 'false':
        return False
    return disable_by_param


def get_application_id(context):
    aws_lambda_log_stream_name = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)
    application_id = aws_lambda_log_stream_name.split("]")[1] if aws_lambda_log_stream_name is not None else ''
    return application_id


def get_aws_lambda_function_memory_size():
    return os.environ.get(constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE)


#### memory ####
def process_memory_usage():
    try:
        with open('/proc/self/statm', 'r') as procfile:
            process_memory_usages = procfile.readline()
            size_from_env_var = get_aws_lambda_function_memory_size()
            if not size_from_env_var:
                size = process_memory_usages.split(' ')[0]
                size_in_bytes = float(size) * 1024
            else:
                size_in_bytes = float(size_from_env_var) * 1048576

            resident = process_memory_usages.split(' ')[1]
            resident_in_bytes = float(resident)*1024
            return size_in_bytes, resident_in_bytes
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(2)


def system_memory_usage():
    try:
        with open('/proc/meminfo', 'r') as procfile:
            total = procfile.readline()
            total_memory = total.split(': ')[1].split('kB')[0]
            total_mem_in_bytes = int(total_memory)*1024
            free = procfile.readline()
            free_memory = free.split(': ')[1].split('kB')[0]
            free_mem_in_bytes = int(free_memory)*1024
            return total_mem_in_bytes, free_mem_in_bytes
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(2)


##### cpu #####
def process_cpu_usage():
    try:
        with open('/proc/self/stat', 'r') as procfile:
            process_cpu_usages = procfile.readline()
            # get utime from /proc/<pid>/stat, 14 item
            u_time = process_cpu_usages.split(' ')[13]
            # get stime from proc/<pid>/stat, 15 item
            s_time = process_cpu_usages.split(' ')[14]
            # count total process used time
            process_cpu_used = int(u_time) + int(s_time)
            return (float(process_cpu_used))
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(2)


def system_cpu_usage():
    try:
        with open('/proc/stat', 'r') as procfile:
            system_cpu_usages = procfile.readline()
            system_cpu_used = 0
            system_cpu_total = 0
            count = 0
            for usage in system_cpu_usages.split(' ')[2:]:
                if count == 5:
                    break
                elif count != 3 and count != 4:
                    system_cpu_used += int(usage)
                system_cpu_total += int(usage)
                count += 1
            return float(system_cpu_total), float(system_cpu_used)
    except IOError as e:
        print('ERROR: %s' % e)
        sys.exit(3)


#####################################################################
###
#####################################################################


class Singleton(object):
    _instances = {}
    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]


def get_all_env_variables():
    return os.environ


def get_module_name(module):
    return module.__name__


def string_to_list(target, indicator):
    return target.split(indicator)


def str2bool(val):
    if val.lower() in ("yes", "true", "t", "1"):
        return True
    elif val.lower() in ("no", "false", "f", "0"):
        return False
    raise ValueError


def process_trace_def_env_var(value):
    value = value.strip().split('[')
    path = value[0].split('.')
    trace_args = {}

    function_prefix = path[-1][:-1] if path[-1] != '*' else '*'
    module_path = ".".join(path[:-1])

    if len(value) > 1 :
        trace_string = value[1].strip(']').split(',')
        for arg in trace_string:
            arg = arg.split('=')
            try:
                trace_args[arg[0].strip()] = arg[1].strip()
            except:
                pass
    else:
        trace_args["trace_args"] = 'False'
        trace_args["trace_return_value"] = 'False'
        trace_args["trace_error"] = 'False'

    return module_path, function_prefix, trace_args


def classesinmodule(module):
    md = module.__dict__
    return [
        md[c] for c in md if (
            isinstance(md[c], type) and md[c].__module__ == module.__name__
        )
    ]

def get_allowed_functions(module):
    functions_list = []

    for clazz in classesinmodule(module):
        for o in getmembers(clazz):
            if (inspect.isfunction(o[1])):
                functions_list.append({"type" : "class", "className": clazz.__name__, "functionName" : clazz.__name__ + "." + str(o[1].__name__)})

    for o in getmembers(module):
        if ( inspect.isfunction(o[1])):
            functions_list.append({"type": "function", "functionName": str(o[1].__name__)})

    return functions_list

def get_aws_region_from_arn(func_arn):
    return func_arn.split(':')[3] if len(func_arn.split(':')) >= 3 else ""

def is_excluded_url(url):
    host = urlparse(url).netloc
    for method in EXCLUDED_URLS:
        for excluded_url in EXCLUDED_URLS[method]:
            if method(host, excluded_url):
                return True
    return False

# Excluded url's 
EXCLUDED_URLS = {
    str.endswith: [
        'thundra.io',
    ],
    str.__contains__: [
        'amazonaws.com',
        'accounts.google.com',
    ],
}
