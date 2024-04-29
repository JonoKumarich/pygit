from dataclasses import dataclass
import configparser
from typing import Self
from pathlib import Path


@dataclass
class GitConfig:
    name: str
    email: str

    @classmethod
    def source(cls) -> Self:
        config = configparser.ConfigParser()
        # TODO: At the moment this is the only possible path for config vars. We should add the others
        config.read(Path.home() / '.config/git/config')

        assert 'user' in config, "'user' field must be set in git config"
        assert 'name' in config['user'], "'user.name' field must set in git config"
        assert 'email' in config['user'], "'user.email' field must set in git config"

        return cls(name=config['user']['name'], email=config['user']['email'])

