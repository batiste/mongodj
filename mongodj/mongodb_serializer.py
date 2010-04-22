from pymongo import Connection
from pymongo.son_manipulator import SONManipulator

def encode_django(model):
    from .fields import EmbeddedModel
    if isinstance(model, EmbeddedModel):
        res = model.serialize()
        res["_type"] = "emb"
        return res
    if not model.pk:
        model.save()
    return {'_app':model._meta.app_label, 
            '_model':model._meta.module_name,
            'pk':model.pk,
            '_type':"django"}

def decode_django(data):
    from django.contrib.contenttypes.models import ContentType
    model = ContentType.objects.get(app_label=data['_app'], model=data['_model'])
    if data['_type']=="django":
        return model.get_object_for_this_type(pk=data['pk'])
    elif data['_type']=="emb":
        del data['_type']
        del data['_app']
        del data['_model']
        data.pop('_id', None)
        data = dict([(str(k),v) for k,v in data.items()])
        return model.model_class()(**data)

class TransformDjango(SONManipulator):
    def transform_incoming(self, son, collection):
        from django.db.models import Model
        from .fields import EmbeddedModel
        if isinstance(son, dict):
            for (key, value) in son.items():
                if isinstance(value, (Model, EmbeddedModel)):
                    son[key] = encode_django(value)
                elif isinstance(value, dict): # Make sure we recurse into sub-docs
                    son[key] = self.transform_incoming(value, collection)
                elif hasattr(value, "__iter__"): # Make sure we recurse into sub-docs
                    son[key] = [self.transform_incoming(item, collection) for item in value]
        elif hasattr(son, "__iter__"): # Make sure we recurse into sub-docs
            son = [self.transform_incoming(item, collection) for item in son]
        elif isinstance(son, (Model, EmbeddedModel)):
            son = encode_django(son)
        return son
    
    def transform_outgoing(self, son, collection):
        if isinstance(son, dict):
            if "_id" in son:
                pk = son.pop('_id')
                son['id'] = unicode(pk)
            if "_type" in son and son["_type"] in [u"django", u'emb']:
                son = decode_django(son)
            else:
                for (key, value) in son.items():
                    if isinstance(value, dict):
                        if "_type" in value and value["_type"] in [u"django", u'emb']:
                            son[key] = decode_django(value)
                        else:
                            son[key] = self.transform_outgoing(value, collection)
                    elif hasattr(value, "__iter__"): # Make sure we recurse into sub-docs
                        son[key] = [self.transform_outgoing(item, collection) for item in value]
                    else: # Again, make sure to recurse into sub-docs
                        son[key] = self.transform_outgoing(value, collection)
        elif hasattr(son, "__iter__"): # Make sure we recurse into sub-docs
            son = [self.transform_outgoing(item, collection) for item in son]
            
        return son
