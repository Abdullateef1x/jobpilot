import uuid
from datetime import datetime, timezone

from sqlmodel import Session, desc, select

from app.models.application import Application, ApplicationCreate, ApplicationStatus


def get_applications_by_user(db: Session, user_id) -> list[Application]:
    statement = select(Application).where(Application.user_id == user_id)
    return list(db.exec(statement).all())  

def get_top_matches_by_user(db: Session, user_id: int) -> list[Application]:
    statement = (
        select(Application)
        .where(Application.user_id == user_id)
        .order_by(desc(Application.match_score).nullslast())
    )
    return list(db.exec(statement).all())


def get_application_by_id(db: Session, application_id:uuid.UUID, user_id) -> Application | None:    
    statement = select(Application).where(Application.application_id == application_id).where(Application.user_id == user_id)
    result = db.exec(statement).first()
    return result


def create_application(db: Session, application_in: ApplicationCreate, user_id) -> Application:

    

    application = Application (
    user_id=user_id,
    role_title=application_in.role_title,
    company_name=application_in.company_name,
    job_description_url=application_in.job_description_url,
    status= ApplicationStatus.Applied,
    job_description=application_in.job_description
    )



    db.add(application)
    db.commit()
    db.refresh(application)

    return application

def update_application_match(db: Session, application_id: uuid.UUID,  user_id, match_score: float, match_explanation: str ) -> Application | None:


    application = get_application_by_id(db, application_id, user_id) 


    if application:
        application.match_score = match_score
        application.match_explanation= match_explanation
        application.updated_at = datetime.now(timezone.utc)  
        db.commit()
        db.refresh(application)
    
    return application


def update_application_status(db: Session, application_id, user_id, new_status) -> Application | None:
    application = get_application_by_id(db, application_id, user_id) 

    
    if application:
        application.status = new_status
        application.updated_at = datetime.now(timezone.utc)  
        db.commit()
        db.refresh(application)


    return application


def update_application_cover_letter(db, application_id, user_id, cover_letter: str) -> Application | None:

    application = get_application_by_id(db, application_id, user_id)

    if application:
        application.cover_letter = cover_letter
        application.updated_at = datetime.now(timezone.utc)  
        db.commit()
        db.refresh(application)

    return application





def delete_application(db: Session, application_id, user_id) -> dict:
    application = get_application_by_id(db, application_id, user_id) 

    if not application:
        return {"ok": False}

    db.delete(application)
    db.commit()

    return {"ok": True}