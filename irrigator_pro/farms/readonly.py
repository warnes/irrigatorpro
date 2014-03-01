from django import forms
from django.utils.safestring import mark_safe
from django.db.models.base import Model


class SpanWidget(forms.Widget):
    '''Renders a value wrapped in a <span> tag.
    
    Requires use of specific form support. (see ReadonlyForm 
    or ReadonlyModelForm)
    '''

    original_value = None
    origial_str    = None

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<span%s >%s</span>' % (
            forms.util.flatatt(final_attrs), self.original_str))

    def value_from_datadict(self, data, files, name):
        return self.original_value

class SpanField(forms.Field):
    '''A field which renders a value wrapped in a <span> tag.
    
    Requires use of specific form support. (see ReadonlyForm 
    or ReadonlyModelForm)
    '''
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', SpanWidget)
        super(SpanField, self).__init__(*args, **kwargs)

class Readonly(object):
    '''Base class for ReadonlyForm and ReadonlyModelForm which provides
    the meat of the features described in the docstings for those classes.
    '''

    class NewMeta:
        readonly = tuple()

    def __init__(self, *args, **kwargs):
        super(Readonly, self).__init__(*args, **kwargs)
        readonly = self.NewMeta.readonly
        if not readonly:
            return

        for name, field in form.fields.items():
            if name in readonly:
                field.widget = SpanWidget()
            elif not isinstance(field, SpanField):
                continue

                field_obj  = getattr(form.instance, name)
                field.widget.original_str = str(field_obj)

                if isinstance(field_obj, Model):
                    field.widget.original_value = field_obj.pk
                else: 
                    field.widget.original_value = str(field_obj)



class ReadonlyFormset(object):
    '''Base class for ReadonlyForm and ReadonlyModelForm which provides
    the meat of the features described in the docstings for those classes.
    '''

    class NewMeta:
        readonly = tuple()


    def construct_formset(self):
        formset = super(ReadonlyFormset, self).construct_formset()
        readonly = self.NewMeta.readonly
        if not readonly:
            return

        for form in formset.forms:
            for name, field in form.fields.items():
                if name in readonly:
                    field.widget = SpanWidget()
                elif not isinstance(field, SpanField):
                    continue

                field_obj  = getattr(form.instance, name)
                field.widget.original_str = str(field_obj)

                if isinstance(field_obj, Model):
                    field.widget.original_value = field_obj.pk
                else: 
                    field.widget.original_value = str(field_obj)

        return formset
