"""
Handles loading and creating the templating engine
"""
import os
from pathlib import Path
from typing import Union
from jinja2 import Environment, FileSystemLoader, BaseLoader, select_autoescape


def for_file(template_file: Union[str, Path]):
    """
    Loads the templating engine for the template file specified
    :param template_file: to fill in, string or Path
    :return: the templating engine
    """
    return Jinja2Engine(template_file)


def string(template):
    """ Returns a template engine for processing templates as strings """
    return Jinja2StringEngine(template)


class Jinja2Engine:
    """
    A simple class that creates a facade around a Jinja2 templating environment
    """

    def __init__(self, template_file: Union[str, Path]):
        template_dir = os.path.dirname(template_file)
        self.template_name = os.path.basename(template_file)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def process(self, record):
        """
        Render the template using the fields in the provided record
        :param record: dictionary of field in template to value to populate the field with
        :return: The rendered template
        """
        template = self.env.get_template(self.template_name)
        return template.render(record)


class Jinja2StringEngine:
    """
    A Jinja2 Templating Engine for String Templates
    """

    def __init__(self, template):
        self.template = template
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def process(self, record):
        """
        Render the template using the fields in the provided record
        :param record: dictionary of field in template to value to populate the field with
        :return: The rendered template
        """
        template = self.env.from_string(self.template)
        return template.render(record)
