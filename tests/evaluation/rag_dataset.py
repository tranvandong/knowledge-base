from dataclasses import dataclass


@dataclass
class EvaluationCase:
    query: str
    expected_chunk_ids: list[str]


DATASET = [
    EvaluationCase(
        query="Nhân viên được nghỉ phép bao nhiêu ngày?",
        expected_chunk_ids=["chunk_leave"],
    ),
    EvaluationCase(
        query="Có cần đăng ký nghỉ phép trước không?",
        expected_chunk_ids=["chunk_leave_request"],
    ),
    EvaluationCase(
        query="Chính sách làm việc từ xa là gì?",
        expected_chunk_ids=["chunk_remote_work"],
    ),
]