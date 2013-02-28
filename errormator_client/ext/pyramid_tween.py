from errormator_client.exceptions import get_current_traceback
from errormator_client.timing import get_local_storage, local_timing
from pyramid.tweens import EXCVIEW
import pyramid
import logging

log = logging.getLogger(__name__)

def errormator_tween_factory(handler, registry):

    blacklist = (pyramid.httpexceptions.WSGIHTTPException,)

    def error_tween(request):
        try:
            response = handler(request)
        except blacklist as e:
            raise
        except:
            if 'errormator.client' in request.environ:
                errormator_storage = get_local_storage(local_timing)
                stats, slow_calls = errormator_storage.get_thread_stats()
                traceback = get_current_traceback(skip=1,
                                                  show_hidden_frames=True,
                                                  ignore_system_exceptions=True)
                request.environ['errormator.client'].py_report(request.environ,
                                traceback, message=None,
                                http_status=500, request_stats=stats)
            raise
        return response
    return error_tween


def includeme(config):
    config.add_tween('errormator_client.ext.pyramid_tween.errormator_tween_factory',
                     under=EXCVIEW)