import os
import time
import random
import json
from typing import List, Tuple

class CollaborativeMoodBoard:
    def __init__(self, board_id: str):
        self.board_id = board_id
        self.images: List[Tuple[str, str]] = []
        self.comments: List[Tuple[str, str, float]] = []
        self.last_updated = time.time()

    def add_image(self, user_id: str, image_url: str):
        self.images.append((user_id, image_url))
        self.last_updated = time.time()

    def add_comment(self, user_id: str, comment: str, timestamp: float):
        self.comments.append((user_id, comment, timestamp))
        self.last_updated = time.time()

    def serialize(self) -> str:
        data = {
            'board_id': self.board_id,
            'images': self.images,
            'comments': self.comments,
            'last_updated': self.last_updated
        }
        return json.dumps(data)

    @classmethod
    def deserialize(cls, data: str):
        board_data = json.loads(data)
        board = cls(board_data['board_id'])
        board.images = board_data['images']
        board.comments = board_data['comments']
        board.last_updated = board_data['last_updated']
        return board

class SwarmCoordinator:
    def __init__(self):
        self.boards: Dict[str, CollaborativeMoodBoard] = {}

    def create_board(self, board_id: str) -> CollaborativeMoodBoard:
        board = CollaborativeMoodBoard(board_id)
        self.boards[board_id] = board
        return board

    def get_board(self, board_id: str) -> CollaborativeMoodBoard:
        if board_id not in self.boards:
            raise ValueError(f'Board {board_id} does not exist')
        return self.boards[board_id]

    def save_boards(self, directory: str):
        for board_id, board in self.boards.items():
            file_path = os.path.join(directory, f'{board_id}.json')
            with open(file_path, 'w') as f:
                f.write(board.serialize())

    def load_boards(self, directory: str):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r') as f:
                    board_data = f.read()
                board = CollaborativeMoodBoard.deserialize(board_data)
                self.boards[board.board_id] = board
