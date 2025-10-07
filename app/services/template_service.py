from jinja2 import Environment, StrictUndefined
from app.models.template import Template

class TemplateService:
    _env = Environment(undefined=StrictUndefined)
    
    @staticmethod
    def create_template(name, body, placeholders, channel='whatsapp', locale='en'):
        '''Create a new template - updated to handle both old and new schema'''
        template = Template(
            channel=channel,
            locale=locale,
            placeholders=placeholders or []
        )
        # Store body in placeholders for backward compatibility
        if body and not placeholders:
            template.placeholders = [body]
        elif body and placeholders:
            # Store the template body as the first placeholder for rendering
            template.placeholders = [body] + placeholders
        return template.save()
    
    @staticmethod
    def render_template(template_placeholders, user_attributes):
        '''Render template with placeholders'''
        try:
            # If placeholders is a list, use the first item as template body
            if isinstance(template_placeholders, list) and template_placeholders:
                template_body = template_placeholders[0]
            else:
                template_body = str(template_placeholders)
                
            template = TemplateService._env.from_string(template_body)
            return template.render(**user_attributes)
        except Exception as e:
            raise Exception(f"Template rendering error: {str(e)}")
    
    @staticmethod
    def preview_template(template_id, placeholders):
        '''Preview template rendering'''
        template = Template.get_by_id(template_id)
        if not template:
            raise ValueError("Template not found")
        
        try:
            rendered = TemplateService.render_template(template.placeholders, placeholders)
            return rendered
        except Exception as e:
            raise ValueError(f"Template preview error: {str(e)}")