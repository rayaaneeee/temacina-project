from rest_framework.renderers import JSONRenderer
import json

class StandardJSONRenderer(JSONRenderer):
    """Wraps every response in { success, data, meta, errors }."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200
        success = 200 <= status_code < 400

        # DRF errors arrive as dict with 'detail' or field names
        if not success:
            payload = {"success": False, "data": None, "errors": data}
        else:
            payload = {"success": True, "data": data, "errors": None}

        return super().render(payload, accepted_media_type, renderer_context)
