#!/usr/bin/env python3
"""Fetch dashboards from provided urls into this chart."""
import json
import textwrap
from os import makedirs, path

import requests
import re
import yaml
from yaml.representer import SafeRepresenter


# https://stackoverflow.com/a/20863889/961092
class LiteralStr(str):
    pass


def change_style(style, representer):
    def new_representer(dumper, data):
        scalar = representer(dumper, data)
        scalar.style = style
        return scalar

    return new_representer


# Source files list
charts = [
    {
        'source': 'https://raw.githubusercontent.com/lightninglabs/lndmon/master/grafana/provisioning/dashboards/chain.json',
        'destination': '../templates/grafana/dashboards'
    },
    {
        'source': 'https://raw.githubusercontent.com/lightninglabs/lndmon/master/grafana/provisioning/dashboards/channels.json',
        'destination': '../templates/grafana/dashboards'
    },
    {
        'source': 'https://raw.githubusercontent.com/lightninglabs/lndmon/master/grafana/provisioning/dashboards/network.json',
        'destination': '../templates/grafana/dashboards'
    },
    {
        'source': 'https://raw.githubusercontent.com/lightninglabs/lndmon/master/grafana/provisioning/dashboards/peers.json',
        'destination': '../templates/grafana/dashboards'
    },
    {
        'source': 'https://raw.githubusercontent.com/lightninglabs/lndmon/master/grafana/provisioning/dashboards/perf.json',
        'destination': '../templates/grafana/dashboards'
    },
]

# standard header
header = '''# Generated from '%(name)s' from %(url)s
# Do not change in-place! In order to change this file first read following link:
# https://github.com/budacom/helm-lnd/tree/master/hack
{{- if and .Values.lndmon.enabled .Values.lndmon.defaultDashboards.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ printf "%%s-%%s" (include "lnd.fullname" $) "%(name)s" | trunc 63 | trimSuffix "-" }}
  labels:
    {{- if $.Values.lndmon.defaultDashboards.sidecarLabel }}
    {{ $.Values.lndmon.defaultDashboards.sidecarLabel }}: "1"
    {{- end }}
    app: {{ template "lnd.name" $ }}-grafana
data:
'''


def init_yaml_styles():
    represent_literal_str = change_style('|', SafeRepresenter.represent_str)
    yaml.add_representer(LiteralStr, represent_literal_str)


def escape(s):
    return s.replace("{{", "{{`{{").replace("}}", "}}`}}")


def yaml_str_repr(struct, indent=2):
    """represent yaml as a string"""
    text = yaml.dump(
        struct,
        width=1000,  # to disable line wrapping
        default_flow_style=False  # to disable multiple items on single line
    )
    text = escape(text)  # escape {{ and }} for helm
    text = textwrap.indent(text, ' ' * indent)
    return text


def write_group_to_file(resource_name, content, url, destination):
    # initialize header
    lines = header % {
        'name': resource_name,
        'url': url
    }

    filename_struct = {resource_name + '.json': (LiteralStr(content))}
    # rules themselves
    lines += yaml_str_repr(filename_struct)

    # footer
    lines += '{{- end }}'

    filename = resource_name + '.yaml'
    new_filename = "%s/%s" % (destination, filename)

    # make sure directories to store the file exist
    makedirs(destination, exist_ok=True)

    # recreate the file
    with open(new_filename, 'w') as f:
        f.write(lines)

    print("Generated %s" % new_filename)


def main():
    init_yaml_styles()
    # read the dashboards, create a new template file per group
    for chart in charts:
        print("Generating dashboards from %s" % chart['source'])
        response = requests.get(chart['source'])
        if response.status_code != 200:
            print('Skipping the file, response code %s not equals 200' % response.status_code)
            continue
        else:
            content = response.text
            name = re.search('/.*\/(.*)\.json$', chart['source']).group(1)
            write_group_to_file(name, content, chart['source'], chart['destination'])
    print("Finished")


if __name__ == '__main__':
    main()
