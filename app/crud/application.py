from sqlmodel import Session, select

from app.models.application import Application, ApplicationCreate, ApplicationStatus


def get_applications_by_user(db: Session, user_id) -> list[Application]:
    statement = select(Application).where(Application.user_id == user_id)
    return list(db.exec(statement).all())  

def get_application_by_id(db: Session, application_id, user_id) -> Application | None:    
    statement = select(Application).where(Application.application_id == application_id).where(Application.user_id == user_id)
    result = db.exec(statement).first()
    return result


def create_application(db: Session, application_in: ApplicationCreate, user_id) -> Application | None:


    application = Application (
    user_id=user_id,
    role_title=application_in.role_title,
    company_name=application_in.company_name,
    job_description_url=application_in.job_description_url,
    status= ApplicationStatus.Applied,
    job_description=None
    )



    db.add(application)
    db.commit()
    db.refresh(application)

    return application

