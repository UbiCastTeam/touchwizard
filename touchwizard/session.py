#!/usr/bin/env python
# -*- coding: utf-8 -*
import easyevent
import logging

logger = logging.getLogger('touchwizard')

class Session(easyevent.User):
    """Session is a shared dictionnary-like object which notify when modified.
    
    (Should only have one instance.)
    
    Listen for event:
    
    - request_session
          Request for receiving the shared session. The session is sent back
          through the session_reply event type.
    
    Launch the event:
    
    - session_update
          Sent when the session has been modified.
    
    - session_reply (session)
          Sent after receiving request_session. The content is the share
          session itself (dictionnary-like object).
    """
    MODIFYING_METHOD_NAMES = ('__delitem__', '__setitem__',
                             'clear', 'pop', 'popitem', 'setdefault', 'update')
    
    def __init__(self, *args, **kw):
        easyevent.User.__init__(self)
        self.dict = dict(*args, **kw)
        self.register_event('request_session')
    
    def evt_request_session(self, event):
        logger.debug('in session: Session requested by %s' %event.source)
        self.launch_event('session_reply', self)
    
    def __getattr__(self, name):
        attr = self.dict.__getattribute__(name)
        if name in self.MODIFYING_METHOD_NAMES:
            return self.__decorate_by_notifier(attr)
        return attr
    
    def __decorate_by_notifier(self, method):
        def notify(*args, **kw):
            logger.debug('in session: Session modified (%s)', method.__name__)
            result = method(*args, **kw)
            self.launch_event('session_update')
            return result
        return notify

if __name__ == '__main__':
    class Observer(easyevent.User):
        def __init__(self):
            easyevent.Listener.__init__(self)
            self.register_event('session_reply', 'session_update')
            self.session = None
            self.launch_event('request_session')
        
        def evt_session_reply(self, event):
            self.unregister_event('session_reply')
            self.session = event.content
            print self
        
        def evt_session_update(self, event):
            print self
        
        def __str__(self):
            return 'My session is now %r.' %(self.session)
    
    session = Session(hello='world')
    observer = Observer()
    session['good'] = 'luck'
    session['good'] = 'bye'
    del session['good']
    session.popitem()
    
