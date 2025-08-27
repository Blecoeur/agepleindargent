from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from .. import models, schemas
from ..db import get_db
from ..parsers import PARSER_REGISTRY

router = APIRouter(prefix="/events", tags=["events"])


# Event CRUD
@router.get("/", response_model=list[schemas.EventRead])
def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()


@router.post("/", response_model=schemas.EventRead)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(get_db)):
    event = models.Event(**event_in.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}", response_model=schemas.EventRead)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}", response_model=schemas.EventRead)
def update_event(event_id: str, event_in: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for field, value in event_in.dict(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_event(event_id: str, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"ok": True}


# Selling Points CRUD
@router.get("/{event_id}/selling-points", response_model=list[schemas.SellingPointRead])
def list_selling_points(event_id: str, db: Session = Depends(get_db)):
    return db.query(models.SellingPoint).filter_by(event_id=event_id).all()


@router.post("/{event_id}/selling-points", response_model=schemas.SellingPointRead)
def create_selling_point(event_id: str, sp_in: schemas.SellingPointCreate, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    sp = models.SellingPoint(event_id=event_id, **sp_in.dict())
    db.add(sp)
    db.commit()
    db.refresh(sp)
    return sp


@router.patch("/{event_id}/selling-points/{sp_id}", response_model=schemas.SellingPointRead)
def update_selling_point(event_id: str, sp_id: str, sp_in: schemas.SellingPointUpdate, db: Session = Depends(get_db)):
    sp = db.get(models.SellingPoint, sp_id)
    if not sp or sp.event_id != event_id:
        raise HTTPException(status_code=404, detail="Selling point not found")
    for field, value in sp_in.dict(exclude_unset=True).items():
        setattr(sp, field, value)
    db.commit()
    db.refresh(sp)
    return sp


@router.delete("/{event_id}/selling-points/{sp_id}")
def delete_selling_point(event_id: str, sp_id: str, db: Session = Depends(get_db)):
    sp = db.get(models.SellingPoint, sp_id)
    if not sp or sp.event_id != event_id:
        raise HTTPException(status_code=404, detail="Selling point not found")
    db.delete(sp)
    db.commit()
    return {"ok": True}


# EPT CRUD
@router.get("/selling-points/{sp_id}/epts", response_model=list[schemas.EPTRead])
def list_epts(sp_id: str, db: Session = Depends(get_db)):
    return db.query(models.EPT).filter_by(selling_point_id=sp_id).all()


@router.post("/selling-points/{sp_id}/epts", response_model=schemas.EPTRead)
def create_ept(sp_id: str, ept_in: schemas.EPTCreate, db: Session = Depends(get_db)):
    sp = db.get(models.SellingPoint, sp_id)
    if not sp:
        raise HTTPException(status_code=404, detail="Selling point not found")
    ept = models.EPT(selling_point_id=sp_id, **ept_in.dict())
    db.add(ept)
    db.commit()
    db.refresh(ept)
    return ept


@router.patch("/selling-points/{sp_id}/epts/{ept_id}", response_model=schemas.EPTRead)
def update_ept(sp_id: str, ept_id: str, ept_in: schemas.EPTUpdate, db: Session = Depends(get_db)):
    ept = db.get(models.EPT, ept_id)
    if not ept or ept.selling_point_id != sp_id:
        raise HTTPException(status_code=404, detail="EPT not found")
    for field, value in ept_in.dict(exclude_unset=True).items():
        setattr(ept, field, value)
    db.commit()
    db.refresh(ept)
    return ept


@router.delete("/selling-points/{sp_id}/epts/{ept_id}")
def delete_ept(sp_id: str, ept_id: str, db: Session = Depends(get_db)):
    ept = db.get(models.EPT, ept_id)
    if not ept or ept.selling_point_id != sp_id:
        raise HTTPException(status_code=404, detail="EPT not found")
    db.delete(ept)
    db.commit()
    return {"ok": True}


# CSV Import
@router.post("/{event_id}/imports", response_model=schemas.ImportSummary)
def import_csv(
    event_id: str,
    parser: str = Form(...),
    file: UploadFile = File(...),
    ept_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    parser_impl = PARSER_REGISTRY.get(parser)
    if not parser_impl:
        raise HTTPException(status_code=400, detail="Unknown parser")

    processed = inserted = skipped = errors = 0
    for tx in parser_impl.parse(file.file):
        processed += 1
        sp = (
            db.query(models.SellingPoint)
            .filter_by(event_id=event_id, name=tx.selling_point_name)
            .first()
        )
        if not sp:
            errors += 1
            continue
        ept = None
        if tx.ept_label:
            ept = (
                db.query(models.EPT)
                .filter_by(selling_point_id=sp.id, label=tx.ept_label)
                .first()
            )
        if not ept and ept_id:
            ept = db.get(models.EPT, ept_id)
        if not ept:
            errors += 1
            continue

        t = models.Transaction(
            event_id=event_id,
            selling_point_id=sp.id,
            ept_id=ept.id,
            amount_cents=tx.amount_cents,
            currency=tx.currency,
            occurred_at=tx.occurred_at,
            card_last4=tx.card_last4,
            source=parser,
            source_row_hash=tx.source_row_hash,
        )
        db.add(t)
        try:
            db.commit()
            inserted += 1
        except IntegrityError:
            db.rollback()
            skipped += 1
        except Exception:
            db.rollback()
            errors += 1

    return schemas.ImportSummary(
        processed=processed, inserted=inserted, skipped_duplicates=skipped, errors=errors
    )


# Summary endpoint
@router.get("/{event_id}/summary", response_model=schemas.EventSummary)
def event_summary(event_id: str, db: Session = Depends(get_db)):
    event = (
        db.query(models.Event)
        .options(joinedload(models.Event.selling_points).joinedload(models.SellingPoint.epts))
        .filter(models.Event.id == event_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    sp_totals = {
        sp_id: total
        for sp_id, total in db.query(
            models.Transaction.selling_point_id, func.coalesce(func.sum(models.Transaction.amount_cents), 0)
        )
        .filter(models.Transaction.event_id == event_id)
        .group_by(models.Transaction.selling_point_id)
    }

    ept_totals = {
        ept_id: total
        for ept_id, total in db.query(
            models.Transaction.ept_id, func.coalesce(func.sum(models.Transaction.amount_cents), 0)
        )
        .filter(models.Transaction.event_id == event_id)
        .group_by(models.Transaction.ept_id)
    }

    selling_points = []
    for sp in event.selling_points:
        epts = [
            schemas.EPTSummary(
                id=ept.id,
                label=ept.label,
                total_cents=ept_totals.get(ept.id, 0),
            )
            for ept in sp.epts
        ]
        selling_points.append(
            schemas.SellingPointSummary(
                id=sp.id,
                name=sp.name,
                total_cents=sp_totals.get(sp.id, 0),
                epts=epts,
            )
        )

    return schemas.EventSummary(event_id=event.id, selling_points=selling_points)
