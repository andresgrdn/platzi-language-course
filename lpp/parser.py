from enum import IntEnum
from typing import (
    Callable,
    Optional,
    List,
)

from lpp.ast import (
    Expression,
    ExpressionStatement,
    Program,
    Statement,
    LetStatement,
    Identifier,
    ReturnStatement,
)
from lpp.lexer import Lexer
from lpp.token import (
    Token,
    TokenType,
)


PrefixParseFn = Callable[[], Optional[Expression]]  # + 2 3
InfixParseFn = Callable[[Expression], Optional[Expression]]  # 3 + 2
PrefixParseFns = dict[TokenType, PrefixParseFn]
InfixParseFns = dict[TokenType, InfixParseFn]


class Precedence(IntEnum):
    LOWEST = 1
    EQUALS = 2
    LESS_GREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7


class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self._lexer = lexer
        self._current_token: Optional[Token] = None
        self._peek_token: Optional[Token] = None
        self._errors: List[str] = []

        self._prefix_parse_fns: PrefixParseFns = self._register_prefix_fns()
        self._infix_parse_fns: InfixParseFns = self._register_infix_fns()

        self._advance_tokens()
        self._advance_tokens()

    @property
    def errors(self) -> List[str]:
        return self._errors

    def parse_program(self) -> Program:
        """
        Lee los tokens que genera el parser y genera el ast (abstract sintax tree).\n
        Retorna un ast completo.
        """
        program: Program = Program(statements=[])

        assert self._current_token is not None
        while self._current_token.token_type != TokenType.EOF:
            statement = self._parse_statement()
            if statement is not None:
                program.statements.append(statement)

            self._advance_tokens()

        return program

    def _advance_tokens(self) -> None:
        """Usa el lexer del parser para generar el siguiente token. Cambiando el current y el peek token."""
        self._current_token = self._peek_token
        self._peek_token = self._lexer.next_token()

    def _expected_token(self, token_type: TokenType) -> bool:
        """
        Verifica que el siguiente token tomado por el parser sea del tipo esperado.\n
        Regresando True o False.
        """
        assert self._peek_token is not None
        if self._peek_token.token_type == token_type:
            self._advance_tokens()

            return True

        self._expected_token_error(token_type)
        return False

    def _expected_token_error(self, token_type: TokenType) -> None:
        """
        Agrega los errores generados por el _expected_token a la lista de errores del parser.
        """
        assert self._peek_token is not None
        error = f'Se esperaba que el siguiente token fuera {token_type} ' + \
            f'pero se obtuvo {self._peek_token.token_type}'

        self._errors.append(error)

    def _parse_expression_statement(self) -> Optional[ExpressionStatement]:
        """
        Instancia un expression statement desde el token actual.
        """
        assert self._current_token is not None
        expression_statement = ExpressionStatement(token=self._current_token)

        expression_statement.expression = self._parse_expression(
            Precedence.LOWEST)

        assert self._peek_token is not None
        if self._peek_token.token_type == TokenType.SEMICOLON:
            self._advance_tokens()

        return expression_statement

    def _parse_expression(self, precedence: Precedence) -> Optional[Expression]:
        assert self._current_token is not None
        try:
            prefix_parse_fn = self._prefix_parse_fns[self._current_token.token_type]
        except KeyError:
            return None

        left_expression = prefix_parse_fn()

        return left_expression

    def _parse_identifier(self) -> Identifier:
        assert self._current_token is not None
        return Identifier(token=self._current_token,
                          value=self._current_token.literal)

    def _parse_let_statement(self) -> Optional[LetStatement]:
        assert self._current_token is not None
        let_statement = LetStatement(token=self._current_token)

        if not self._expected_token(TokenType.IDENT):
            return None

        let_statement.name = Identifier(
            token=self._current_token, value=self._current_token.literal)

        if not self._expected_token(TokenType.ASSIGN):
            return None

        # TODO: Implement expressions parser
        while self._current_token.token_type != TokenType.SEMICOLON:
            self._advance_tokens()

        return let_statement

    def _parse_return_statement(self) -> Optional[ReturnStatement]:
        assert self._current_token is not None
        return_statement = ReturnStatement(token=self._current_token)

        self._advance_tokens()

        # TODO: Implement expressions parser
        while self._current_token.token_type != TokenType.SEMICOLON:
            self._advance_tokens()

        return return_statement

    def _parse_statement(self) -> Optional[Statement]:
        assert self._current_token is not None
        if self._current_token.token_type == TokenType.LET:
            return self._parse_let_statement()
        if self._current_token.token_type == TokenType.RETURN:
            return self._parse_return_statement()
        else:
            return self._parse_expression_statement()

    def _register_infix_fns(self) -> InfixParseFns:
        return {}

    def _register_prefix_fns(self) -> PrefixParseFns:
        return {
            TokenType.IDENT: self._parse_identifier,
        }
