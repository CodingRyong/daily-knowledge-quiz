"""문제 JSON 검증. 사용: python scripts/validate.py data/2026-10-22.json"""
import json
import os
import sys
from collections import Counter

EXPECT = {"시사": 4, "경제": 3, "상식": 3}


def check(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    assert os.path.basename(path) == f"{d.get('date')}.json", "date 필드가 파일명과 달라요"
    br = d.get("briefing")
    assert isinstance(br, list) and 6 <= len(br) <= 14, "briefing은 6~14개"
    for i, b in enumerate(br, 1):
        assert b.get("category") in EXPECT, f"브리핑 {i}번: category 오류 {b.get('category')!r}"
        for k in ("title", "summary"):
            assert isinstance(b.get(k), str) and b[k].strip(), f"브리핑 {i}번: {k} 비어 있음"
        if b["category"] == "시사" or b.get("source"):
            assert str(b.get("source", "")).startswith("http"), f"브리핑 {i}번: source는 URL (시사는 필수)"
    bc = Counter(b["category"] for b in br)
    assert all(bc[k] >= 1 for k in EXPECT), f"브리핑에 빠진 카테고리: {[k for k in EXPECT if not bc[k]]}"
    qs = d.get("questions")
    assert isinstance(qs, list) and len(qs) == 10, f"질문은 10개여야 함 (현재 {len(qs) if isinstance(qs, list) else '없음'})"
    for i, q in enumerate(qs, 1):
        assert q.get("category") in EXPECT, f"{i}번: category 오류 {q.get('category')!r}"
        assert isinstance(q.get("choices"), list) and len(q["choices"]) == 4, f"{i}번: choices는 4개"
        assert isinstance(q.get("answer"), int) and 0 <= q["answer"] <= 3, f"{i}번: answer는 0~3"
        for t in (q.get("q"), q.get("explanation"), *q["choices"]):
            assert isinstance(t, str) and t.strip(), f"{i}번: 빈 텍스트"
        assert len(set(q["choices"])) == 4, f"{i}번: 선택지 중복"
    counts = Counter(q["category"] for q in qs)
    assert counts == Counter(EXPECT), f"카테고리 개수 {dict(counts)} != {EXPECT}"


if __name__ == "__main__":
    try:
        check(sys.argv[1])
    except (AssertionError, KeyError, ValueError, OSError) as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    print("OK")
