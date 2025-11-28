#!/usr/bin/env python3
"""Simple Unit Converter

Supports length, weight and temperature conversions from CLI or interactively.

Usage (positional):
  python unitconverter.py <value> <from_unit> <to_unit>

Examples:
  python unitconverter.py 100 cm m
  python unitconverter.py 2 kg lb
  python unitconverter.py 32 F C
"""
from __future__ import annotations
import sys
from typing import Dict, Callable


LENGTH_TO_METER: Dict[str, float] = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mm": 0.001,
    "mi": 1609.344,
    "yd": 0.9144,
    "ft": 0.3048,
    "in": 0.0254,
}

WEIGHT_TO_KG: Dict[str, float] = {
    "kg": 1.0,
    "g": 0.001,
    "mg": 0.000001,
    "lb": 0.45359237,
    "oz": 0.028349523125,
    "ton": 1000.0,
}


def c_to_f(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0


def f_to_c(f: float) -> float:
    return (f - 32.0) * 5.0 / 9.0


def c_to_k(c: float) -> float:
    return c + 273.15


def k_to_c(k: float) -> float:
    return k - 273.15


TEMP_FUNCS: Dict[str, Dict[str, Callable[[float], float]]] = {
    "C": {
        "F": c_to_f,
        "K": c_to_k,
        "C": lambda x: x,
    },
    "F": {
        "C": f_to_c,
        "K": lambda f: c_to_k(f_to_c(f)),
        "F": lambda x: x,
    },
    "K": {
        "C": k_to_c,
        "F": lambda k: c_to_f(k_to_c(k)),
        "K": lambda x: x,
    },
}


def convert_length(value: float, from_u: str, to_u: str) -> float:
    try:
        to_m = LENGTH_TO_METER[from_u]
        from_m = LENGTH_TO_METER[to_u]
    except KeyError:
        raise ValueError("Unsupported length unit")
    # convert value -> meters -> target
    meters = value * to_m
    return meters / from_m


def convert_weight(value: float, from_u: str, to_u: str) -> float:
    try:
        to_kg = WEIGHT_TO_KG[from_u]
        from_kg = WEIGHT_TO_KG[to_u]
    except KeyError:
        raise ValueError("Unsupported weight unit")
    kg = value * to_kg
    return kg / from_kg


def convert_temperature(value: float, from_u: str, to_u: str) -> float:
    from_u = from_u.upper()
    to_u = to_u.upper()
    try:
        func = TEMP_FUNCS[from_u][to_u]
    except KeyError:
        raise ValueError("Unsupported temperature unit")
    return func(value)


def detect_and_convert(value: float, from_u: str, to_u: str) -> float:
    # try length
    if from_u in LENGTH_TO_METER and to_u in LENGTH_TO_METER:
        return convert_length(value, from_u, to_u)
    if from_u in WEIGHT_TO_KG and to_u in WEIGHT_TO_KG:
        return convert_weight(value, from_u, to_u)
    if from_u.upper() in TEMP_FUNCS and to_u.upper() in TEMP_FUNCS:
        return convert_temperature(value, from_u, to_u)
    raise ValueError("Units belong to different categories or are unsupported")


def print_help() -> None:
    print(__doc__)
    print("Supported length units:", ", ".join(sorted(LENGTH_TO_METER.keys())))
    print("Supported weight units:", ", ".join(sorted(WEIGHT_TO_KG.keys())))
    print("Supported temperature units: C, F, K")


def interactive() -> None:
    print("Simple Unit Converter — type 'help' for units, 'exit' to quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw.lower() in {"exit", "quit"}:
            break
        if raw.lower() in {"help", "h", "?"}:
            print_help()
            continue
        parts = raw.split()
        if len(parts) != 3:
            print("Enter: <value> <from_unit> <to_unit>  (e.g. '100 cm m') or 'help'")
            continue
        try:
            val = float(parts[0])
        except ValueError:
            print("Invalid number")
            continue
        from_u, to_u = parts[1], parts[2]
        try:
            out = detect_and_convert(val, from_u, to_u)
            print(f"{val} {from_u} = {out} {to_u}")
        except ValueError as e:
            print("Error:", e)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        interactive()
        return 0
    if argv[0] in {"-h", "--help", "help"} or len(argv) < 3:
        print_help()
        return 0
    # parse positional
    try:
        value = float(argv[0])
    except ValueError:
        print("First argument must be a number. Use: <value> <from_unit> <to_unit>")
        return 1
    from_u = argv[1]
    to_u = argv[2]
    try:
        result = detect_and_convert(value, from_u, to_u)
    except ValueError as e:
        print("Error:", e)
        return 2
    # display with reasonable formatting
    print(f"{value} {from_u} = {result:.6g} {to_u}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
