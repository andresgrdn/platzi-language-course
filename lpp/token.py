from enum import (
    auto,
    Enum,
    unique,
)
from typing import (
    Dict,
    NamedTuple,
)


@unique
class TokenType(Enum):
    ASSIGN = auto()
    COMMA = auto()
    EOF = auto()
    FUNCTION = auto()
    IDENT = auto()
    ILLEGAL = auto()
    INT = auto()
    LBRACE = auto()
    LET = auto()
    LPAREN = auto()
    PLUS = auto()
    RBRACE = auto()
    RPAREN = auto()
    SEMICOLON = auto()


class Token(NamedTuple):
    token_type: TokenType
    literal: str

    def __str__(self) -> str:
        return f'Tipo: {self.token_type}, literal: {self.literal}'


def lookup_token_type(literal: str) -> TokenType:
    keywords: Dict[str, TokenType] = {
        'variable': TokenType.LET,
        'bloque': TokenType.FUNCTION,
    }

    return keywords.get(literal, TokenType.IDENT)
