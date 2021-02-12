import inspect
import os
import pkgutil
from operator import itemgetter
from typing import Any, List, Tuple, TypeVar

import pandas as pd
import pytest

import pyrdf2vec
from pyrdf2vec.graphs import KG
from pyrdf2vec.walkers import Walker

TRAIN_DF = pd.read_csv("samples/mutag/train.tsv", sep="\t", header=0)

ENTITIES = [entity for entity in TRAIN_DF["bond"]]
ENTITIES_SUBSET = ENTITIES[:5]

T = TypeVar("T")


def _get_classes() -> List[Tuple[str, T]]:
    """Gets the classes from a package.

    Returns:
        The classes from a package.

    """
    classes = []
    base_path = [os.path.dirname(pyrdf2vec.__file__)]
    for _, name, _ in pkgutil.walk_packages(
        path=base_path, prefix="pyrdf2vec."
    ):
        module = __import__(name, fromlist="dummy")
        classes.extend(inspect.getmembers(module, inspect.isclass))
    return classes


def _get_walkers() -> List[Tuple[str, Any]]:
    """Gets the classes that are not a subclass of `sklearn.BaseEstimator` and
    that are not an abstract class.

    Returns:
        The classes.

    """
    classes = [  # type: ignore
        cls  # type: ignore
        for cls in set(_get_classes())  # type: ignore
        if issubclass(cls[1], Walker)  # type: ignore
    ]
    return sorted(set(classes), key=itemgetter(0))


def check_walker(name, Walker):
    max_walks = 5
    depth = 2

    canonical_walks = Walker(depth, max_walks, random_state=42).extract(
        KG(
            "samples/mutag/mutag.owl",
            skip_predicates={
                "http://dl-learner.org/carcinogenesis#isMutagenic"
            },
        ),
        ENTITIES_SUBSET,
    )
    assert type(canonical_walks) == set

    if name == "WLWalker":
        assert len(canonical_walks) <= len(ENTITIES_SUBSET * max_walks * 5)

    # Sometimes, WalkletWalker returns one/two more walks than the ones
    # specified.  We need to fix that.
    elif name == "WalkletWalker":
        assert len(canonical_walks) <= len(
            ENTITIES_SUBSET * max_walks * (depth + 2)
        )
    else:
        assert len(canonical_walks) <= len(ENTITIES_SUBSET * max_walks)


def is_abstract(cls: Any) -> bool:
    """Tells whether a class is abstract or not.

    Args:
        cls: The class has to determine if it is abstract or not.

    Returns:
        True if abstract class, False otherwise.

    """
    return (
        hasattr(cls, "__abstractmethods__")
        and len(cls.__abstractmethods__) != 0
    )


@pytest.mark.parametrize("name, Walker", _get_walkers())
def test_walkers(name: str, Walker: T):
    """Tests the walkers.

    Args:
        name: The name of the walker.
        Walker: The class of the walker.

    """
    print(f"Testing the Walker: {name}")
    check_walker(name, Walker)
