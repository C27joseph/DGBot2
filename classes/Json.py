import os
import json


def load(pathfile="", encoding='utf-8'):
    try:
        with open(pathfile, "r", encoding=encoding) as f:
            data = json.load(f)
            return data
    except IOError:
        return None


def loadWrite(pathfile="", default={}, encoding='utf-8'):
    try:
        with open(pathfile+".json", "r", encoding=encoding) as f:
            data = json.load(f)
            return data
    except IOError:
        cur_path = ""
        for path in pathfile.split("/")[:-1]:
            cur_path += path+"/"
            try:
                os.mkdir(cur_path)
            except Exception:
                pass
        with open(pathfile+".json", 'w', encoding=encoding) as f:
            json.dump(default, f, indent=4, ensure_ascii=False)
            return default


def write(pathfile="", default={}, encoding="utf-8", **kv):
    try:
        cur_path = ""
        for path in pathfile.split("/")[:-1]:
            cur_path += path+"/"
            try:
                os.mkdir(cur_path)
            except Exception:
                pass
        with open(pathfile+".json", 'w', encoding=encoding) as f:
            json.dump(default, f, indent=4, ensure_ascii=False, **kv)
            return True
    except IOError:
        print(f"cannot write {pathfile}")


def delete(pathfile="", isdirectory=False):
    try:
        if isdirectory:
            os.rmdir(pathfile)
        else:
            os.remove(f"{pathfile}.json")
    except Exception:
        pass
    return True
