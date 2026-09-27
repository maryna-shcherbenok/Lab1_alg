from array import array
from pathlib import Path
import sys

HASH_BASE = 31
HASH_MOD = 1_000_000_007
BUCKETS = 1_000_003
MAX_LEN = 15
MAX_OPS = 1_000_000
MAX_ACTIVE = 1_000_000


def check_token(text: str) -> None:
    if not 1 <= len(text) <= MAX_LEN:
        raise ValueError('Word length must be from 1 to 15 characters.')
    if any(ch < 'a' or ch > 'z' for ch in text):
        raise ValueError('Only lowercase Latin letters a-z are allowed.')


def calc_poly(text: str) -> int:
    value = 0
    for ch in text:
        value = (value * HASH_BASE + (ord(ch) - 96)) % HASH_MOD
    return value


class ChainWordSet:
    def __init__(self, bucket_count: int = BUCKETS):
        if bucket_count <= 0:
            raise ValueError('Bucket count must be positive.')

        self.heads = array('i', [-1]) * bucket_count
        self.words = []
        self.hashes = array('I')
        self.links = array('i')
        self.active = bytearray()
        self.plus_count = array('I')
        self.current_size = 0

    def __len__(self) -> int:
        return self.current_size

    def _seek(self, text: str, hash_value: int) -> int:
        pos = self.heads[hash_value % len(self.heads)]
        while pos != -1:
            if self.hashes[pos] == hash_value and self.words[pos] == text:
                return pos
            pos = self.links[pos]
        return -1

    def put_word(self, text: str) -> bool:
        check_token(text)
        hash_value = calc_poly(text)
        pos = self._seek(text, hash_value)

        if pos != -1:
            self.plus_count[pos] += 1
            if not self.active[pos]:
                if self.current_size >= MAX_ACTIVE:
                    raise ValueError('The set cannot contain more than 1,000,000 elements.')
                self.active[pos] = 1
                self.current_size += 1
                return True
            return False

        if self.current_size >= MAX_ACTIVE:
            raise ValueError('The set cannot contain more than 1,000,000 elements.')

        bucket = hash_value % len(self.heads)
        new_pos = len(self.words)
        self.words.append(text)
        self.hashes.append(hash_value)
        self.links.append(self.heads[bucket])
        self.active.append(1)
        self.plus_count.append(1)
        self.heads[bucket] = new_pos
        self.current_size += 1
        return True

    def drop_word(self, text: str) -> bool:
        check_token(text)
        hash_value = calc_poly(text)
        pos = self._seek(text, hash_value)

        if pos == -1 or not self.active[pos]:
            return False

        self.active[pos] = 0
        self.current_size -= 1
        return True

    def has_word(self, text: str) -> bool:
        check_token(text)
        hash_value = calc_poly(text)
        pos = self._seek(text, hash_value)
        return pos != -1 and bool(self.active[pos])

    def iter_repeats(self):
        for pos, text in enumerate(self.words):
            if self.plus_count[pos] > 1:
                yield text, self.plus_count[pos]


def read_commands(stream, answer_stream=sys.stdout):
    table = ChainWordSet()
    operation_count = 0
    ended = False

    for line_no, raw_line in enumerate(stream, 1):
        line = raw_line.strip()
        if not line:
            continue

        if line == '#':
            ended = True
            break

        parts = line.split()
        if len(parts) != 2 or parts[0] not in ('+', '-', '?'):
            raise ValueError(
                f'Line {line_no}: expected "+ word", "- word", "? word" or "#".'
            )

        sign, text = parts
        check_token(text)
        operation_count += 1
        if operation_count > MAX_OPS:
            raise ValueError('The input cannot contain more than 1,000,000 operations.')

        if sign == '+':
            table.put_word(text)
        elif sign == '-':
            table.drop_word(text)
        else:
            answer_stream.write('yes\n' if table.has_word(text) else 'no\n')

    if not ended:
        raise ValueError('Input data must end with #.')

    return table, operation_count


def main() -> int:
    source_path = Path(__file__).with_name('input.txt')

    try:
        with source_path.open('r', encoding='utf-8-sig') as source:
            table, _ = read_commands(source)

        for text, count in table.iter_repeats():
            print(text, count)

    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
