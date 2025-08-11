from functools import lru_cache

__all__ = ["get_analyzer", "get_summary_chain", "get_hashtags_chain", "get_ideas_chain"]

@lru_cache
def get_analyzer():
    from .analyze import analyzer  # imports analyze + builds LLM on first call
    return analyzer

@lru_cache
def get_summary_chain():
    from .analyze import summary_chain
    return summary_chain

@lru_cache
def get_hashtags_chain():
    from .analyze import hashtags_chain
    return hashtags_chain

@lru_cache
def get_ideas_chain():
    from .analyze import ideas_chain
    return ideas_chain
