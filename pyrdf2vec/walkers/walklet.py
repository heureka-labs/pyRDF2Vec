from typing import Dict, Set, Tuple

import attr

from pyrdf2vec.graphs import KG, Vertex
from pyrdf2vec.walkers import RandomWalker


@attr.s
class WalkletWalker(RandomWalker):
    """Defines the walklet walking strategy.

    Attributes:
        depth: The depth per entity.
        max_walks: The maximum number of walks per entity.
        sampler: The sampling strategy.
            Defaults to UniformSampler().
        n_jobs: The number of process to use for multiprocessing.
            Defaults to 1.
        random_state: The random state to use to ensure ensure random
            determinism to generate the same walks for entities.
            Defaults to None.

    """

    def _extract(
        self, kg: KG, instance: Vertex
    ) -> Dict[str, Tuple[Tuple[str, ...], ...]]:
        """Extracts walks rooted at the provided instances which are then each
        transformed into a numerical representation.

        Args:
            kg: The Knowledge Graph.

                The graph from which the neighborhoods are extracted for the
                provided instances.
            instance: The instance to be extracted from the Knowledge Graph.

        Returns:
            The 2D matrix with its number of rows equal to the number of
            provided instances; number of column equal to the embedding size.

        """
        canonical_walks: Set[Tuple[str, ...]] = set()
        walks = self.extract_walks(kg, instance)
        for walk in walks:
            if len(walk) == 1:
                canonical_walks.add((walk[0].name,))
            for n in range(1, len(walk)):
                canonical_walks.add((walk[0].name, walk[n].name))
        return {instance.name: tuple(canonical_walks)}
