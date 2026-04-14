import argparse
import inspect
import random
import sys
import termios
import tty
from collections import Counter
from dataclasses import dataclass

import pandas as pd


@dataclass
class AttrInfo:
    name: str
    kind: str
    sig_str: str | None
    return_type: str | None


def _return_type_str(annotation: object) -> str | None:
    if annotation is inspect.Parameter.empty:
        return None
    return getattr(annotation, "__name__", None) or str(annotation)


def collect_attrs(cls: type) -> list[AttrInfo]:
    attrs = []
    for name in dir(cls):
        if name.startswith("_"):
            continue
        obj = getattr(cls, name)
        kind = type(obj).__name__
        sig_str = None
        ret_type = None
        try:
            sig = inspect.signature(obj)
            sig_str = str(sig)
            ret_type = _return_type_str(sig.return_annotation)
        except (ValueError, TypeError):
            pass
        attrs.append(AttrInfo(name, kind, sig_str, ret_type))
    return attrs


def print_summary(attrs: list[AttrInfo], cls: type) -> None:
    kind_counter = Counter(a.kind for a in attrs)
    print(f"\n{cls.__name__} — {len(attrs)} public attributes\n")
    for kind, count in kind_counter.most_common():
        print(f"  {kind}: {count}")
        callable_group = [a for a in attrs if a.kind == kind and a.sig_str is not None]
        if callable_group:
            for ret, n in Counter(
                a.return_type or "?" for a in callable_group
            ).most_common():
                print(f"    -> {ret}: {n}")


def get_char() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def run(cls: type, attrs: list[AttrInfo], seed: int | None) -> None:
    shuffled = attrs[:]
    random.Random(seed).shuffle(shuffled)
    total = len(shuffled)

    for i, attr in enumerate(shuffled):
        print(f"\n[{i + 1}/{total}] {attr.name}  ({attr.kind})")
        while True:
            ch = get_char()
            if ch == "d":
                if attr.sig_str:
                    print(f"  {attr.name}{attr.sig_str}")
                doc = getattr(getattr(cls, attr.name), "__doc__", None)
                print(doc or "(no docstring)")
            elif ch == "n":
                break
            elif ch in ("q", "\x03"):
                print("\nQuit.")
                return

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive docstring reviewer")
    parser.add_argument("--polars", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--self-returning", action="store_true", help="Only show methods returning cls"
    )
    args = parser.parse_args()

    cls = pd.DataFrame
    if args.polars:
        import polars as pl

        cls = pl.DataFrame

    attrs = collect_attrs(cls)
    print_summary(attrs, cls)

    if args.self_returning:
        attrs = [a for a in attrs if a.return_type == cls.__name__]
        print(f"\nFiltered to {len(attrs)} self-returning methods.")

    run(cls, attrs, args.seed)


if __name__ == "__main__":
    main()
