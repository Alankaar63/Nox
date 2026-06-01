__all__ = ["FitnessAgent"]


def __getattr__(name: str):
    if name == "FitnessAgent":
        from .agent import FitnessAgent

        return FitnessAgent
    raise AttributeError(name)
