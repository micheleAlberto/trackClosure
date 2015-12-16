print 'name '+__name__ + 'imported '
from glob import glob
print 'submodules: ' + ', '.join(glob('*.py')+glob('*/__init__.py))
