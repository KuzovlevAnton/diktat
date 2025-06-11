import requests
import os
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TOKEN_YANDEX")


class Disk:

    def __init__(self, token):
        self.token__ = token
        self.headers__ = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}

    def upload(self, disk_path, computer_path, filename):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        responce = requests.get(f"{url}?path={disk_path}&overwrite=True", headers=self.headers__)

        with open(computer_path, 'rb') as f:
            link = responce.json()["href"]
            requests.put(f"{link}?path={disk_path}", files={'file': f})
        return responce.json()["href"]

    def download(self, disk_path, computer_path, filename):
        url = "https://cloud-api.yandex.net/v1/disk/resources/download"
        responce = requests.get(f"{url}?path={disk_path}", headers=self.headers__)
        with open(computer_path, "wb") as f:
            f.write(requests.get(responce.json()["href"]).content)
        return responce.json()["href"]








# # url = "https://cloud-api.yandex.net/v1/disk/resources/download"
# url = "https://cloud-api.yandex.net/v1/disk/resources"
# for i in range(1001):
#     responce = requests.put(f"{url}?path=Python{i}", headers=headers)
#     print(i)
#
# # responce = requests.post(f"{url}?from=Горы.jpg&path=Python0/Горы.jpg", headers=headers)
# responce = requests.get(f"{url}?path=Горы.jpg", headers=headers)


disk = Disk(token=TOKEN)

# print(disk.upload("/log.txt", "log.txt", "log.txt"))

# print(disk.download("/log.txt", "log.txt", "log.txt"))


# print(responce)
# print(responce.json())