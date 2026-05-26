from sqlalchemy.orm import Session
from models.raw_complaint import RawComplaint


def collect_public_data(db: Session, source: str):
    sample_data = [
        {
            "source": source,
            "external_id": "demo-001",
            "title": "서울시 도로 파손 민원 증가",
            "content": "서울시 일부 지역에서 도로 파손 관련 민원이 반복적으로 접수되고 있음.",
            "region": "서울",
            "category": "도로",
        },
        {
            "source": source,
            "external_id": "demo-002",
            "title": "부산시 야간 소음 신고 증가",
            "content": "부산시 주거지역 야간 소음 관련 신고가 증가하는 추세를 보임.",
            "region": "부산",
            "category": "소음",
        },
    ]

    collected_count = 0

    for item in sample_data:
        existing = db.query(RawComplaint).filter(
            RawComplaint.external_id == item["external_id"]
        ).first()

        if existing:
            continue

        complaint = RawComplaint(
            source=item["source"],
            external_id=item["external_id"],
            title=item["title"],
            content=item["content"],
            region=item["region"],
            category=item["category"],
        )
        db.add(complaint)
        collected_count += 1

    db.commit()
    return collected_count
