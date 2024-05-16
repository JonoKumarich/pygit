import re
import zlib
from dataclasses import dataclass
from enum import Enum, auto
from typing import IO, Optional, Self
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
        self.advertised = set(
            packet.payload.split(maxsplit=1)[0]
            for packet in packet_lines
            if packet.payload is not None
        )
        self.common = set()
        self.want = self.advertised
        self.c_pening = []

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

    def compute(self) -> IO[bytes]:

        body = b""

        # Sets some additional info up the top
        # body += b"0054want 2c103af8723ff4dad8ee951a7ede04807fecc44d multi_ack side-band-64k ofs-delta\n"

        for want in self.want:
            body += b"0032want " + want + b"\n"

        for common in self.common:
            body += b"0032have " + common + b"\n"

        COMMIT_LIMIT = 32
        for _ in range(COMMIT_LIMIT):
            if len(self.c_pening) == 0:
                break

            have = self.c_pening.pop(0)
            body += b"0032have " + have + b"\n"

        body += b"0000"
        body += b"0009done\n"

        # TODO: Currently, there is no packfile negotiation, just simply a packfile request. (Will need to negotiate properly when using git fetch)
        # https://github.com/git/git/blob/795ea8776befc95ea2becd8020c7a284677b4161/Documentation/gitprotocol-pack.txt#L241

        headers = {"Content-Type": "application/x-git-upload-pack-request"}
        url = "https://github.com/JonoKumarich/pygit/git-upload-pack"
        req = request.Request(url, data=body, method="POST", headers=headers)
        response = request.urlopen(req)

        assert response.status == 200, "Compute request response status != 200"

        return response
