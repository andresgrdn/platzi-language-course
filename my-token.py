class TokenType(Enum):
    ASSIGN = auto()
    ...

class Token(NamedTuple):
    token_type: TokenType
    literal: str