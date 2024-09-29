import pathlib
import re
import shutil
import py7zr
import os

seven = None
lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', '.DOC', '.DOCX']
_path_dir = '/home/svdior/parse_etp/'
_path = '/home/svdior/parse_etp/my_z.7z'
with py7zr.SevenZipFile(_path, 'r') as _zip:
    allfiles = _zip.getnames()
    targets = [f for f in allfiles if pathlib.Path(f).suffix in lst_exet_files]
    _zip.extract(path=_path_dir, targets=targets)
    for t in targets:
        _suffix = pathlib.Path(t).suffix
        if re.match(f'.+/.+{_suffix}', t):
            check = 0
            # _root -> folder name
            _root = str(t).rsplit('/', maxsplit=1)[0]
            # file name
            _name_file = ''.join(str(t).split('/')[-1])
        else:
            check = 1
            # _root -> folder name
            _root = ''
            # file name
            _name_file = t
        new_file_name = _name_file.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        old_name = os.path.join(_path_dir, t)
        size = os.path.getsize(old_name)
        new_name = os.path.join(_path_dir, new_file_name)
        if os.path.isdir(old_name):
            os.rename(old_name, new_name)
            shutil.rmtree(old_name, ignore_errors=True)
        else:
            # move file to etp directory
            os.rename(old_name, new_name)
    # delete folder and archive
    os.remove(_path)

