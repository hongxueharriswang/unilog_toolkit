
import shutil

class NotAvailable(RuntimeError):
    pass


def which(cmd: str):
    return shutil.which(cmd)


def require(cmd: str):
    path = which(cmd)
    if not path:
        raise NotAvailable(f"Required external tool '{cmd}' was not found in PATH.")
    return path
