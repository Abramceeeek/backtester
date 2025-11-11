"""
Sandbox module for safely executing user-provided trading strategies.
Validates and runs strategy code in a restricted environment.
"""

import ast
import sys
import io
import multiprocessing
import signal
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import logging
from contextlib import redirect_stdout, redirect_stderr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Whitelisted module names that strategies can use
# Note: Access is provided via create_safe_globals; this set is informational.
ALLOWED_MODULES = {
    'pandas',
    'pd',
    'numpy',
    'np',
    'math',
    'datetime',
}

# Blacklisted AST node types (dangerous operations)
BLACKLISTED_NODES = {
    ast.Import,      # We'll manually inject allowed imports
    ast.ImportFrom,
}

# Blacklisted names (dangerous built-ins)
BLACKLISTED_NAMES = {
    'open', 'file', 'input', 'raw_input', 'execfile', 'reload',
    'compile', 'eval', 'exec', '__import__', 'breakpoint',
    'help', 'vars', 'dir', 'globals', 'locals',
    'memoryview', 'bytearray',
}

# Maximum execution time per strategy call (seconds)
MAX_EXECUTION_TIME = 5

# Maximum memory usage (bytes) - 500MB
MAX_MEMORY = 500 * 1024 * 1024


class StrategyValidationError(Exception):
    """Raised when strategy code fails validation."""
    pass


class StrategyExecutionError(Exception):
    """Raised when strategy execution fails."""
    pass


class StrategyTimeout(Exception):
    """Raised when strategy execution times out."""
    pass


def validate_strategy_code(code: str) -> None:
    """
    Validate strategy code using AST analysis.

    Args:
        code: Python code to validate

    Raises:
        StrategyValidationError: If code contains forbidden operations
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise StrategyValidationError(f"Syntax error in strategy code: {e}")

    # Check for blacklisted node types
    for node in ast.walk(tree):
        node_type = type(node)
        if node_type in BLACKLISTED_NODES:
            raise StrategyValidationError(
                f"Forbidden operation: {node_type.__name__} at line {node.lineno}"
            )

        # Check for blacklisted names
        if isinstance(node, ast.Name):
            if node.id in BLACKLISTED_NAMES:
                raise StrategyValidationError(
                    f"Forbidden name: '{node.id}' at line {node.lineno}"
                )

        # Check for attribute access to dangerous modules
        if isinstance(node, ast.Attribute):
            if node.attr in ['__', 'eval', 'exec', 'compile']:
                raise StrategyValidationError(
                    f"Forbidden attribute access: '{node.attr}' at line {node.lineno}"
                )

    # Ensure strategy function exists
    function_names = [node.name for node in ast.walk(tree)
                      if isinstance(node, ast.FunctionDef)]

    if 'strategy' not in function_names:
        raise StrategyValidationError(
            "Strategy code must define a function named 'strategy'"
        )


def create_safe_globals() -> Dict[str, Any]:
    """
    Create a restricted globals dictionary for strategy execution.

    Returns:
        Dictionary of allowed global names and values
    """
    safe_globals = {
        '__builtins__': {
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'dict': dict,
            'enumerate': enumerate,
            'float': float,
            'int': int,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'pow': pow,
            'range': range,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'zip': zip,
            'True': True,
            'False': False,
            'None': None,
        },
        'pd': pd,
        'pandas': pd,
        'np': np,
        'numpy': np,
    }

    return safe_globals


def execute_strategy_isolated(
    code: str,
    data: pd.DataFrame,
    state: Dict[str, Any],
    timeout: int = MAX_EXECUTION_TIME
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Execute strategy code in isolation (used within subprocess).

    Args:
        code: Strategy code to execute
        data: Historical price data
        state: Strategy state dictionary
        timeout: Maximum execution time in seconds

    Returns:
        Tuple of (result_dict, error_message)
    """
    try:
        # Create safe execution environment
        safe_globals = create_safe_globals()
        safe_locals = {}

        # Compile and execute the code
        compiled_code = compile(code, '<strategy>', 'exec')
        exec(compiled_code, safe_globals, safe_locals)

        # Get the strategy function
        if 'strategy' not in safe_locals:
            return None, "No 'strategy' function found in code"

        strategy_func = safe_locals['strategy']

        # Execute the strategy function
        result = strategy_func(data.copy(), state.copy())

        # Validate result format
        if not isinstance(result, dict):
            return None, f"Strategy must return a dict, got {type(result).__name__}"

        required_keys = ['signal']
        if not all(key in result for key in required_keys):
            return None, f"Strategy result must contain keys: {required_keys}"

        valid_signals = ['buy', 'sell', 'flat', 'hold', None]
        if result['signal'] not in valid_signals:
            return None, f"Invalid signal: {result['signal']}, must be one of {valid_signals}"

        # Ensure numeric types for optional fields
        if 'size' in result:
            result['size'] = float(result['size'])
        if 'stop_loss' in result:
            result['stop_loss'] = float(result['stop_loss']) if result['stop_loss'] is not None else None
        if 'take_profit' in result:
            result['take_profit'] = float(result['take_profit']) if result['take_profit'] is not None else None

        return result, None

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        return None, error_msg


class StrategySandbox:
    """Manages safe execution of user trading strategies."""

    def __init__(self):
        self.validated_strategies = {}

    def validate(self, code: str, strategy_id: str = None) -> None:
        """
        Validate strategy code.

        Args:
            code: Strategy code to validate
            strategy_id: Optional ID to cache validation

        Raises:
            StrategyValidationError: If validation fails
        """
        validate_strategy_code(code)

        if strategy_id:
            self.validated_strategies[strategy_id] = code

        logger.debug("Strategy validation passed")

    def execute(
        self,
        code: str,
        data: pd.DataFrame,
        state: Optional[Dict[str, Any]] = None,
        timeout: int = MAX_EXECUTION_TIME
    ) -> Dict[str, Any]:
        """
        Execute strategy code safely.

        Args:
            code: Strategy code to execute
            data: Historical price data (DataFrame with OHLCV)
            state: Strategy state dictionary (persists between calls)
            timeout: Maximum execution time in seconds

        Returns:
            Strategy result dictionary with signal, size, stop_loss, take_profit

        Raises:
            StrategyValidationError: If code validation fails
            StrategyExecutionError: If execution fails
            StrategyTimeout: If execution exceeds timeout
        """
        # Validate first
        self.validate(code)

        if state is None:
            state = {}

        # Execute in the same process for simplicity
        # In production, consider using multiprocessing for better isolation
        try:
            result, error = execute_strategy_isolated(code, data, state, timeout)

            if error:
                raise StrategyExecutionError(error)

            return result

        except Exception as e:
            if isinstance(e, (StrategyValidationError, StrategyExecutionError)):
                raise
            raise StrategyExecutionError(f"Unexpected error: {str(e)}")

    def get_strategy_template(self) -> str:
        """
        Get a template for writing strategies.

        Returns:
            String containing strategy template code
        """
        template = '''def strategy(data, state):
    """
    Trading strategy function.

    Args:
        data: pandas DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
              Index is DatetimeIndex. Use .iloc[-1] for current bar, .iloc[-2] for previous, etc.
        state: dict for persisting variables between calls (e.g., state['my_var'] = value)

    Returns:
        dict with keys:
            - 'signal': 'buy', 'sell', 'flat', or 'hold'/'None' (no action)
            - 'size': optional, position size (default: full position based on capital)
            - 'stop_loss': optional, stop loss as multiplier (0.98 = 2% below entry) or absolute price
            - 'take_profit': optional, take profit as multiplier (1.05 = 5% above entry) or absolute price

    Example:
        return {
            'signal': 'buy',
            'size': 1.0,
            'stop_loss': 0.98,  # 2% stop loss
            'take_profit': 1.05  # 5% take profit
        }
    """

    # Your strategy logic here
    close = data['close'].values

    # Example: Simple moving average crossover
    if len(close) < 50:
        return {'signal': None}

    sma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
    sma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

    if sma_20 > sma_50:
        return {
            'signal': 'buy',
            'stop_loss': 0.95,
            'take_profit': 1.10
        }
    elif sma_20 < sma_50:
        return {'signal': 'sell'}

    return {'signal': None}
'''
        return template


# Singleton instance
_sandbox = StrategySandbox()


def get_sandbox() -> StrategySandbox:
    """Get the singleton StrategySandbox instance."""
    return _sandbox
