
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.encoding import force_unicode
from gridfs import GridFS, NoFile
from gridfs.grid_file import GridIn, GridOut
from mongodj.db.base import get_connection_from_dict

class GridFSStorage(Storage):
    """
    A gridFS storage class.
    """

    def _get_fs(self):
        setting_dict = settings.MONGODB_FILE_STORAGE_DATABASE
        if setting_dict is None:
            raise ValueError("""GridFSStorage need
 MONGODB_FILE_STORAGE_DATABASE setting to be set.""")
        conn, name = get_connection_from_dict(setting_dict)
        return GridFS(conn[name])

    def open(self, name, mode='rb'):
        fs = self._get_fs()
        if 'r' in mode:
            try:
                file = fs.get_last_version(name)
            except NoFile:
                file = fs.new_file(filename=name)
                file.close()
                file = fs.get_last_version(name)
        elif 'w' in mode:
            file = fs.new_file(filename=name)
        else:
            raise NotImplementedError()
        return file

    def save(self, name, content):
        """
        Saves new content to the file specified by name. The content should be a
        proper File object, ready to be read from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name
        fs = self._get_fs()
        file = fs.new_file(filename=name)
        file.write(content)
        file.close()
        # Store filenames with forward slashes, even on Windows
        return force_unicode(name.replace('\\', '/'))

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        return name

    def path(self, name):
        """
        Returns a local filesystem path where the file can be retrieved using
        Python's built-in open() function. Storage systems that can't be
        accessed using open() should *not* implement this method.
        """
        raise NotImplementedError("This backend doesn't support absolute paths.")

    # The following methods form the public API for storage systems, but with
    # no default implementations. Subclasses must implement *all* of these.

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        fs = self._get_fs()
        file = fs.delete(name)

    def exists(self, name):
        """
        Returns True if a file referened by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        raise NotImplementedError()

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        fs = self._get_fs()
        return ((),fs.list())
        

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        raise NotImplementedError()

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a web browser.
        """
        raise NotImplementedError()

