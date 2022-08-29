import os
import hashlib


def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files.

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    return filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))


def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    content = file.read()  # get content of file
    ext = os.path.splitext(file.filename)[1]  # get extension of file
    hash_obj = hashlib.md5()
    hash_obj.update(content)
    file.seek(0)  # to return pointer to the init of the file
    new_filename = hash_obj.hexdigest() + ext
    return new_filename
