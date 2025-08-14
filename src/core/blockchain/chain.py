# src/core/blockchain/chain.py
import json
from typing import List
from .block import Block
from pathlib import Path

class Blockchain:
    def __init__(self, crypto):
        self.chain: List[Block] = []
        self.crypto = crypto
        self._initialize_chain()

    def _initialize_chain(self):
        if not self.chain:
            genesis_data = {"note": "Genesis Block"}
            genesis_block = Block(0, genesis_data, "0", self.crypto)
            self.chain.append(genesis_block)

    def add_block(self, note_data: Dict[str, Any]):
        new_block = Block(
            index=len(self.chain),
            data=note_data,
            previous_hash=self.chain[-1].hash,
            crypto=self.crypto
        )
        self.chain.append(new_block)

    def save_to_file(self, file_path: str):
        chain_data = [{
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.encrypted_data,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        } for block in self.chain]

        Path(file_path).parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'w') as f:
            json.dump(chain_data, f, indent=2)

    def load_from_file(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                chain_data = json.load(f)
                self.chain = []
                for block_data in chain_data:
                    block = Block(
                        index=block_data['index'],
                        data={},  # داده واقعی در decrypt پر می‌شود
                        previous_hash=block_data['previous_hash'],
                        crypto=self.crypto
                    )
                    block.timestamp = block_data['timestamp']
                    block.encrypted_data = block_data['data']
                    block.hash = block_data['hash']
                    self.chain.append(block)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_chain()