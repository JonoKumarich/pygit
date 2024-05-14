import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Self
from urllib import parse, request


class PktType(Enum):
    FLUSH = auto()
    DATA = auto()


@dataclass
class PktLineRecord:
    packet_type: PktType
    pkt_len: int
    payload: Optional[bytes]

    @classmethod
    def from_bytes(cls, line: bytes) -> Self:
        pkt_len = int.from_bytes(bytes.fromhex(line[:4].decode()))

        if pkt_len == 0:
            return cls(PktType.FLUSH, pkt_len, None)

        assert (
            length := len(line)
        ) == pkt_len - 1, f"Error, invalid line format. Expected length = {pkt_len}, Observed length = {length}"

        assert pkt_len < 65519, "Packet line length too long"

        return cls(PktType.DATA, pkt_len, line[4:])


class Client:

    def __init__(self, packet_lines: list[PktLineRecord]) -> None:
        self.packet_lines = packet_lines

    @classmethod
    def ref_discovery(cls, author: str, repo: str) -> Self:
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
            ), f"Request status returned: {response.status}. Must be 200 or 304"

            packet_lines = response.read().splitlines()
            print(packet_lines)

            # Clients MUST validate the first five bytes of the response entity matches the regex `^[0-9a-f]{4}#`
            # If this test fails, clients MUST NOT continue.
            assert re.search(
                b"^[0-9a-f]{4}#", (header := packet_lines[0][:5])
            ), f"Response header does not match regex `^[0-9a-f]{4}#`. Observed: {header}"

            # Clients MUST verify the first pkt-line is `# service=$servicename`.
            size = int.from_bytes(bytes.fromhex(header[0:4].decode()))
            assert (observed := packet_lines[0][4:size]) == (
                expected := f"# service={command}".encode()
            ), f"First packet line does not match `{expected}`. Value: {observed}"

            # NOTE: We will skip handling the first and second packet lines for now
            # Example:
            # b'001e# service=git-upload-pack'
            # b'000001532c103af8723ff4dad8ee951a7ede04807fecc44d HEAD\x00multi_ack thin-pack side-band side-band-64k ofs-delta shallow deepen-since deepen-not deepen-relative no-progress include-tag multi_ack_detailed allow-tip-sha1-in-want allow-reachable-sha1-in-want no-done symref=HEAD:refs/heads/main filter object-format=sha1 agent=git/github-f133c3a1d7e6'

            return cls([PktLineRecord.from_bytes(line) for line in packet_lines[2:]])


if __name__ == "__main__":
    client = Client.ref_discovery("JonoKumarich", "pygit")

    data = (
        # b"0077want 2c103af8723ff4dad8ee951a7ede04807fecc44d multi_ack_detailed side-band-64k thin-pack ofs-delta agent=git/1.8.2\n"
        b"0032want 2c103af8723ff4dad8ee951a7ede04807fecc44d\n"
        b"0032want aa94abbbaaecc6113f53c976cd6cf6552b248c24\n"
        b"0000"
        b"0009done\n"
    )

    url = "https://github.com/JonoKumarich/pygit/git-upload-pack"
    headers = {"Content-Type": "application/x-git-upload-pack-request"}

    req = request.Request(url, data=data, method="POST", headers=headers)
    response = request.urlopen(req)

    print(response.status)
    print(response.read())
