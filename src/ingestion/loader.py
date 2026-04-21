import os

def load_files_from_folder(folder_path):
    documents = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                documents.append({
                    "text": f.read(),
                    "source": folder_path.split("/")[-1],  # logs or docs
                    "file_name": file_name
                })

    return documents


def load_all_data():
    logs = load_files_from_folder("data/logs")
    docs = load_files_from_folder("data/docs")

    return logs + docs