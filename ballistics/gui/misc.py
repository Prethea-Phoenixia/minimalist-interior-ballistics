def tree_selected(func):
    def wrapped(pf, *args, **kwargs):
        return func(pf, *args, pid=pf.tree.focus(), **kwargs)

    return wrapped
