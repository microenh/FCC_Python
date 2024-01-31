import os

def data_folder():
    if data_folder.path is None:
        "compute data folder in user local storage"
        s = os.getenv('LOCALAPPDATA')
        if s is None:
            s = ""
        data_folder.path = os.path.join(s, 'fcc')
        if not os.path.exists(data_folder.path):
            os.makedirs(data_folder.path)
        # print (data_folder.path)
    return data_folder.path

data_folder.path = None
