from django.forms import ModelForm
from common.models import Audit

class AuditForm(ModelForm):
    class Meta:
        model = Audit
        exclude = ( 'cdate',
                    'mdate',
                    'cuser',
                    'muser',
        )

    def save(self, *args, **kwargs):
        kwargs['commit']=False
        obj = super(AuditForm, self).save(*args, **kwargs)

        if not 'cuser' in self.cleaned_data:
            self.cleaned_data['cuser'] = request.user

        self.cleaned_data['muser'] = request.user

        obj.save()


def save_audit_model(self, modelform, instance):
    obj = super(AuditForm, self).save(instance, commit=False)
    
    if not obj.cuser:
        obj.cuser = request.user
        
    obj.muser = request.user
        
    obj.save()



