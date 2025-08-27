from datetime import datetime, timedelta

from db import SessionLocal
from models import Event, SellingPoint, EPT, EPTProvider


def run() -> None:
    db = SessionLocal()
    event = Event(
        name="Sample Event",
        start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=1),
    )
    db.add(event)
    db.flush()

    sp1 = SellingPoint(event_id=event.id, name="Bar", latitude=46.52, longitude=6.57)
    sp2 = SellingPoint(event_id=event.id, name="Merch", latitude=46.53, longitude=6.58)
    db.add_all([sp1, sp2])
    db.flush()

    ept1 = EPT(selling_point_id=sp1.id, provider=EPTProvider.worldline, label="WL-1")
    ept2 = EPT(selling_point_id=sp1.id, provider=EPTProvider.sumup, label="SU-1")
    ept3 = EPT(selling_point_id=sp2.id, provider=EPTProvider.other, label="OT-1")
    db.add_all([ept1, ept2, ept3])

    db.commit()
    db.close()
    print("Seeded sample data")


if __name__ == "__main__":
    run()
