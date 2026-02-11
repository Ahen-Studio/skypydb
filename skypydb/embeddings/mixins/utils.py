"""
Module containing the Utils class, which is used to make the embed class callable.
"""

from typing import List

class Utils:
    def __call__(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Make the class callable for compatibility with other libraries.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """

        return self.embed(texts)
