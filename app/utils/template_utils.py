from jinja2 import Environment, StrictUndefined

ENV = Environment(undefined=StrictUndefined)

def render_template_text(body, placeholders):
    """Render template text with placeholders"""
    tmpl = ENV.from_string(body)
    return tmpl.render(**placeholders)