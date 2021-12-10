"""

    runtime -- application runtime management
    =========================================

    This module provides a way to manage runtime in Python applicaitons.

    Most of the code borrowed from the ``werkzeug.local`` by the Werkzeug Team.

    :copyright:
        (c) 2011 by the Werkzeug Team
        (c) 2012 by Andrey Popp
    :license: BSD

"""

import logging

# since each thread has its own greenlet we can just use those as identifiers
# for the context.  If greenlets are not available we fall back to the
# current thread ident.
try:
    from greenlet import getcurrent as get_ident  # pylint: disable=F0401
except ImportError:  # pragma: no cover
    try:
        from thread import get_ident
    except ImportError:  # pragma: no cover
        from dummy_thread import get_ident

__all__ = (
    'Context', 'Local', 'LocalStack', 'Proxy', 'release',
    'current_object', 'is_bound')

class UnboundProxyError(RuntimeError):
    """ Trying to access an object via an unbound proxy"""

class Context(object):
    """ Context

    This object represents a group of related objects exposed via proxies and
    allows them to be managed as a stack.
    """

    cleanup = None

    def __init__(self, name=None, logging_name=None):
        self.name = name
        self.values = LocalStack()
        self.proxies = {}
        self.log = logging.getLogger(
            'runtime.Context.%s' % (logging_name or name,))

    def __getattr__(self, name):
        """ Construct a new proxy which will be bound at configuration time"""
        if name in self.proxies:
            return self.proxies[name]

        def _lookup():
            try:
                return self.values.value[name]
            except (KeyError, AttributeError):
                raise UnboundProxyError("object '%s' unbound" % name)

        proxy = Proxy(_lookup)
        self.proxies[name] = proxy
        return proxy

    def __str__(self):
        try:
            self.values.value
        except UnboundProxyError:
            initialized = False
        else:
            initialized = True
        return "<%s '%s'%s>" % (
            self.__class__.__name__,
            self.name,
            '' if initialized else ' uninitialized')

    __repr__ = __str__

    def __call__(self, **values):
        """ Create a new session for context which implements context manager
        protocol"""
        return Session(self, values)

    def overlay(self, **values):
        try:
            current = dict(self.values.value)
        except UnboundProxyError:
            current = {}
        current.update(values)
        return Session(self, current)

class Session(object):

    def __init__(self, context, values):
        self.context = context
        self.values = values

    def __enter__(self):
        self.context.log.debug('entering context')
        self.context.values.push(self.values)
        return self

    def __exit__(self, *args):
        self.context.log.debug('exiting context')
        if self.context.cleanup:
            self.context.cleanup()
        self.context.values.pop()

class Local(object):
    __slots__ = ('__storage__', '__ident_func__')

    def __init__(self):
        object.__setattr__(self, '__storage__', {})
        object.__setattr__(self, '__ident_func__', get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __call__(self, proxy):
        """Create a proxy for a name."""
        def _lookup():
            try:
                return getattr(self, proxy)
            except AttributeError:
                raise UnboundProxyError("object '%s' unbound" % proxy)
        return Proxy(_lookup)

    def __release__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

class LocalStack(object):
    """This class works similar to a :class:`.Local` but keeps a stack
    of objects instead.  This is best explained with an example::

        >>> ls = LocalStack()
        >>> ls.push(42)
        >>> ls.value
        42
        >>> ls.push(23)
        >>> ls.value
        23
        >>> ls.pop()
        23
        >>> ls.value
        42

    They can be force released by using a :class:`Manager` or with
    the :func:`release` function but the correct way is to pop the
    item from the stack after using.  When the stack is empty it will
    no longer be bound to the current context (and as such released).

    By calling the stack without arguments it returns a proxy that resolves to
    the topmost item on the stack.
    """

    def __init__(self):
        self._local = Local()

    def __release__(self):
        release(self._local)

    def _get__ident_func__(self):
        return self._local.__ident_func__

    def _set__ident_func__(self, value):
        object.__setattr__(self._local, '__ident_func__', value)
    __ident_func__ = property(_get__ident_func__, _set__ident_func__)
    del _get__ident_func__, _set__ident_func__

    def push(self, obj):
        """Pushes a new item to the stack"""
        rv = getattr(self._local, 'stack', None)
        if rv is None:
            self._local.stack = rv = []  # pylint: disable=W0201
        rv.append(obj)
        return rv

    def pop(self):
        """Removes the topmost item from the stack, will return the
        old value or `None` if the stack was already empty.
        """
        stack = getattr(self._local, 'stack', None)
        if stack is None:
            return None
        elif len(stack) == 1:
            release(self._local)
            return stack[-1]
        else:
            return stack.pop()

    @property
    def value(self):
        """The topmost item on the stack.  If the stack is empty,
        `None` is returned.
        """
        try:
            return self._local.stack[-1]
        except (AttributeError, IndexError):
            raise UnboundProxyError('object unbound')

class Proxy(object):
    """Acts as a proxy for a werkzeug local.  Forwards all operations to
    a proxied object.  The only operations not supported for forwarding
    are right handed operands and any kind of assignment.

    Example usage::

        from werkzeug.local import Local
        l = Local()

        # these are proxies
        request = l('request')
        user = l('user')


        from werkzeug.local import LocalStack
        _response_local = LocalStack()

        # this is a proxy
        response = _response_local()

    Whenever something is bound to l.user / l.request the proxy objects
    will forward all operations.  If no object is bound a
    :exc:`UnboundProxyError` will be raised.

    To create proxies to :class:`Local` or :class:`LocalStack` objects,
    call the object as shown above.  If you want to have a proxy to an
    object looked up by a function, you can (as of Werkzeug 0.6.1) pass
    a function to the :class:`Proxy` constructor::

        session = Proxy(lambda: get_current_request().session)

    """
    __slots__ = ('__lookup', '__dict__',)

    def __init__(self, lookup=None):
        object.__setattr__(self, '_Proxy__lookup', lookup)

    def __current_object__(self):
        """Return the current object.  This is useful if you want the real
        object behind the proxy at a time for performance reasons or because
        you want to pass the object into a different context.
        """
        return self.__lookup()

    def __set_lookup__(self, lookup):
        object.__setattr__(self, '_Proxy__lookup', lookup)

    @property
    def __dict__(self):
        try:
            return self.__current_object__().__dict__
        except UnboundProxyError:
            raise AttributeError('__dict__')

    def __repr__(self):
        try:
            obj = self.__current_object__()
        except UnboundProxyError:
            return '<%s unbound>' % self.__class__.__name__
        return repr(obj)

    def __nonzero__(self):
        try:
            return bool(self.__current_object__())
        except UnboundProxyError:
            return False

    def __unicode__(self):
        try:
            return unicode(self.__current_object__())
        except UnboundProxyError:
            return repr(self)

    def __dir__(self):
        try:
            return dir(self.__current_object__())
        except UnboundProxyError:
            return []

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self.__current_object__())
        return getattr(self.__current_object__(), name)

    def __setitem__(self, key, value):
        self.__current_object__()[key] = value

    def __delitem__(self, key):
        del self.__current_object__()[key]

    def __setslice__(self, i, j, seq):
        self.__current_object__()[i:j] = seq

    def __delslice__(self, i, j):
        del self.__current_object__()[i:j]

    __setattr__ = lambda x, n, v: setattr(x.__current_object__(), n, v)
    __delattr__ = lambda x, n: delattr(x.__current_object__(), n)
    __str__ = lambda x: str(x.__current_object__())
    __lt__ = lambda x, o: x.__current_object__() < o
    __le__ = lambda x, o: x.__current_object__() <= o
    __eq__ = lambda x, o: x.__current_object__() == o
    __ne__ = lambda x, o: x.__current_object__() != o
    __gt__ = lambda x, o: x.__current_object__() > o
    __ge__ = lambda x, o: x.__current_object__() >= o
    __cmp__ = lambda x, o: cmp(x.__current_object__(), o)
    __hash__ = lambda x: hash(x.__current_object__())
    __call__ = lambda x, *a, **kw: x.__current_object__()(*a, **kw)
    __len__ = lambda x: len(x.__current_object__())
    __getitem__ = lambda x, i: x.__current_object__()[i]
    __iter__ = lambda x: iter(x.__current_object__())
    __contains__ = lambda x, i: i in x.__current_object__()
    __getslice__ = lambda x, i, j: x.__current_object__()[i:j]
    __add__ = lambda x, o: x.__current_object__() + o
    __sub__ = lambda x, o: x.__current_object__() - o
    __mul__ = lambda x, o: x.__current_object__() * o
    __floordiv__ = lambda x, o: x.__current_object__() // o
    __mod__ = lambda x, o: x.__current_object__() % o
    __divmod__ = lambda x, o: x.__current_object__().__divmod__(o)
    __pow__ = lambda x, o: x.__current_object__() ** o
    __lshift__ = lambda x, o: x.__current_object__() << o
    __rshift__ = lambda x, o: x.__current_object__() >> o
    __and__ = lambda x, o: x.__current_object__() & o
    __xor__ = lambda x, o: x.__current_object__() ^ o
    __or__ = lambda x, o: x.__current_object__() | o
    __div__ = lambda x, o: x.__current_object__().__div__(o)
    __truediv__ = lambda x, o: x.__current_object__().__truediv__(o)
    __neg__ = lambda x: -(x.__current_object__())
    __pos__ = lambda x: +(x.__current_object__())
    __abs__ = lambda x: abs(x.__current_object__())
    __invert__ = lambda x: ~(x.__current_object__())
    __complex__ = lambda x: complex(x.__current_object__())
    __int__ = lambda x: int(x.__current_object__())
    __long__ = lambda x: long(x.__current_object__())
    __float__ = lambda x: float(x.__current_object__())
    __oct__ = lambda x: oct(x.__current_object__())
    __hex__ = lambda x: hex(x.__current_object__())
    __index__ = lambda x: x.__current_object__().__index__()
    # pylint: disable=W0108
    __coerce__ = lambda x, o: x.__current_object__().__coerce__(x, o)
    __enter__ = lambda x: x.__current_object__().__enter__()
    __exit__ = lambda x, *a, **kw: x.__current_object__().__exit__(*a, **kw)

def current_object(proxy):
    """ Return object proxy currently points to"""
    return proxy.__current_object__()

def is_bound(proxy):
    """ Return ``True`` if ``proxy`` is bound to some value"""
    try:
        current_object(proxy)
    except UnboundProxyError:
        return False
    else:
        return True

def release(local):
    """Releases the contents of the local for the current context.
    This makes it possible to use locals without a manager.

    Example::

        >>> loc = Local()
        >>> loc.foo = 42
        >>> release(loc)
        >>> hasattr(loc, 'foo')
        False

    With this function one can release :class:`Local` objects as well
    as :class:`StackLocal` objects.  However it is not possible to
    release data held by proxies that way, one always has to retain
    a reference to the underlying local object in order to be able
    to release it.
    """
    local.__release__()
