#!/usr/bin/env python3
from Parser.jsonParser import parse_json
from Parser.yamlParser import parse_yaml
import networkx as nx

from bokeh.models import Circle, MultiLine
from bokeh.plotting import figure, from_networkx, show

json_parser = parse_json("traces/reflextrace_formatted.json")

yaml_parser = parse_yaml("YamlFiles/ReflexGame.yaml")
yaml_parser.plot()


