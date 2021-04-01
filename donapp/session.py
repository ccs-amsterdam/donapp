import json
import logging
import secrets
import time
import threading
from enum import Enum
from multiprocessing import Process
from pathlib import Path

from subprocess import TimeoutExpired
from threading import Thread
from typing import Mapping, Tuple, Optional, List

from fasteners import InterProcessLock
from selenium.common.exceptions import TimeoutException

from whatsappstract.whatsapp import Whatsapp


class Status(Enum):
    ERROR = -1
    STARTING = 0
    WAITING_SCAN = 1
    SCRAPING = 2
    DONE = 3

#TODO: Periodic cleanup temporary folders
class FolderIPC:
    """
    Inter-process communication between flask and whatsapp process based on files in a temporary folder
    (should be placed on RAM disk to ensure no sensitive data is written to disk)
    """

    @classmethod
    def create(cls, id: str):
        folder = Path("/tmp") / id
        folder.mkdir(mode=0o700)
        return cls(id)

    def __init__(self, id: str):
        folder = Path("/tmp") / id
        self.status = folder/'status.json'
        self.qr = folder/'qr.png'
        self.result = folder/'result.json'
        self.info = folder/'info.json'
        self.lock = InterProcessLock(folder / 'lock.file')

    def set_status(self, status: Status, **kargs):
        logging.info(f"Status: {status}")
        status_dict = dict(status=status.name, **kargs)
        with self.lock:
            with self.status.open('w') as f:
                json.dump(status_dict, f)

    def get_status(self) -> dict:
        with self.lock:
            with self.status.open('r') as f:
                status = json.load(f)
        return status

    def write_qr(self, qr: str):
        logging.info(f"Writing QR to {self.qr}")
        with self.lock:
            with self.qr.open('w') as f:
                f.write(qr)

    def get_qr(self):
        with self.lock:
            with self.qr.open('r') as f:
                return f.read()

    def append_links(self, links: List[dict]):
        with self.lock:
            with self.result.open('a') as f:
                for link in links:
                    json.dump(link, f)
                    f.write("\n")
                    
    def make_json(self):
        with self.result.open('r+') as f:
            data = f.read()
            f.seek(0)
            f.truncate()
            all_chats = [json.loads(jline) for jline in data.splitlines()]
            json.dump(all_chats, f)

    def get_links(self) -> str:
        with self.lock:
            with self.result.open('r') as f:
                return f.read()


class WhatsappProcess(Process):
    def __init__(self, folder: FolderIPC, n_chats: int):
        super().__init__()
        self.folder = folder
        self.folder.set_status(Status.STARTING)
        self.n_chats = n_chats

    def run(self):
        try:
            self.w = Whatsapp(screenshot_folder="/tmp")
            self.wait_for_qr()
            self.do_scrape()
            self.folder.set_status(Status.DONE)
        except Exception as e:
            self.folder.set_status(Status.ERROR, message=f"{type(e)}: {e}")
            raise

    def wait_for_qr(self):
        last_qr = None
        qr_number = 0
        while not self.w.is_qr_scanned():
            logging.info("Checking QR code")
            try:
                qr = self.w.get_qr()
            except TimeoutException:
                # Check if the app was loading the ready screen and is ready now, otherwise re-raise
                if self.w.is_qr_scanned():
                    return
                raise
            if qr != last_qr:
                self.folder.write_qr(qr)
                last_qr = qr
                qr_number += 1
                self.folder.set_status(Status.WAITING_SCAN, progress=qr_number)
            time.sleep(0.5)

    def do_scrape(self):
        self.folder.set_status(Status.SCRAPING, progress=0, message="Starting scraping")
        nlinks = 0
        for i, chat in enumerate(self.w.get_all_chats(), start=1):
            if i > self.n_chats:
                break
            self.folder.set_status(Status.SCRAPING,
                                   progress=round(i * 100 / (self.n_chats + 1)),
                                   message=f"Scraping contact {i}/{self.n_chats}: {chat.text} [{nlinks} links found]"
                                   )
            links = list(self.w.get_links_per_chat(chat))
            nlinks += len(links)
            self.folder.append_links(links)
        self.folder.make_json()


def start_whatsapp(**kargs) -> str:
    """Start a new whatsapp scraper process
    :param the IP address that the original call came from
    :return the ID to use for contacting this process
    """
    id = secrets.token_urlsafe()
    folder = FolderIPC.create(id)
    p = WhatsappProcess(folder, **kargs)
    p.start()
    return id


def get_status(id: str) -> Status:
    status = FolderIPC(id).get_status()
    return Status[status["status"]]


def get_status_details(id: str) -> dict:
    return FolderIPC(id).get_status()


def get_qr(id: str) -> str:
    return FolderIPC(id).get_qr()


def get_result(id: str) -> str:
    return FolderIPC(id).get_links()
