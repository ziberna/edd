# Spynoza Baruch (Python library for common-use)
# Copyright (C) 2011 Jure Žiberna
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see http://www.gnu.org/licenses/gpl-3.0.html

class lict(dict):
    def __init__(self, *args, **kwargs):
        self.__list__ = []
        self.update(*args, **kwargs)
    
    def update(self, *args, **kwargs):
        for arg in args:
            try:
                arg = dict(arg)
                for key in arg:
                    self[key] = arg[key]
            except (TypeError, ValueError):
                self[arg] = arg
        for kwarg in kwargs:
            self[key]
    
    def __setitem__(self, key, value):
        if key not in self.__list__:
            self.__list__.append(key)
        super(lict, self).__setitem__(key, value)
    
    def __delitem__(self, key):
        super(lict, self).__delitem__(key)
        del self.__list__[self.__list__.index(key)]
    
    def __call__(self, index, value=Exception):
        if value == Exception:
            return self.__list__[index]
        else:
            self[self.__list__[index]] = value
            return value
    
    def __iter__(self):
        return self.__list__.__iter__()
    
    def __repr__(self):
        return '[%s]' % ', '.join(['%s: %s' %  (repr(key), repr(self[key])) for key in self.__list__])
