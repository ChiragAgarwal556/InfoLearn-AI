from typing import TypedDict, List, Dict, Any


class TutorState(TypedDict, total=False):
    checkpoint: Dict[str, Any]
    context: str
    questions: List[Dict[str, Any]]
    answers: List[str]
    score: float
    weak_topics: List[str]
