import re
from dataclasses import dataclass
from enum import Enum
from typing import Self
from urllib import request


@dataclass
class DataPacket:
    sha: bytes
    ref: bytes

    @classmethod
    def from_packet_line(cls, line: bytes) -> Self:
        sha, ref = line.split(maxsplit=1)

        return cls(sha, ref)


def ref_discovery(author: str, repo: str) -> list[DataPacket]:
    # TODO: At the moment this only handles github
    # TODO: Maybe can just stream read this through a socket as we have byte size encoding?

    command = "git-upload-pack"
    url = f"https://github.com/{author}/{repo}/info/refs?service={command}"

    with request.urlopen(url) as response:

        # The Content-Type MUST be `application/x-$servicename-advertisement`.
        # NOTE: We do not implement the dumb http protocol to must follow this content type
        assert (
            content_type := response.headers.get_content_type()
        ) == f"application/x-{command}-advertisement", f"Content type does not follow correct format of `application/x-$servicename-advertisement`. Observed: {content_type}"

        # Clients MUST validate the status code is either `200 OK` or `304 Not Modified`.
        assert response.status in (
            200,
            304,
        ), f"Request status returned: {response.status}"

        # Clients MUST validate the first five bytes of the response entity matches the regex `^[0-9a-f]{4}#`.  If this test fails, clients MUST NOT continue.
        assert re.search(
            b"^[0-9a-f]{4}#", (header := response.read(5))
        ), f"Response header does not match regex `^[0-9a-f]{4}#`. Observed: {header}"

        # Clients MUST parse the entire response as a sequence of pkt-line records.

        # Clients MUST verify the first pkt-line is `# service=$servicename`.

        # Clients MUST ignore an LF at the end of the line.

        lines = response.read().split(b"\n")

    packets = [DataPacket.from_packet_line(line) for line in lines[2:-1]]
    return packets


if __name__ == "__main__":
    refs = ref_discovery("JonoKumarich", "pygit")
    print(refs)
