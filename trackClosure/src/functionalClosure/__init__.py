print 'module '+__name__ + ' : imported '
from glob import glob
print 'submodules: \n\t' + '\n\t'.join(glob('*.py')+glob('*/__init__.py'))

