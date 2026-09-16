import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.core.database import get_session
from app.crud.application import (
    create_application,
    delete_application,
    get_application_by_id,
    get_applications_by_user,
    update_application_status,
)
from app.models.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatusUpdate,
)
from app.services.ai import process_application_scoring
from app.services.deps import get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationRead)
async def create_applications(payload: ApplicationCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_session), current_user = Depends(get_current_user)):
    application = create_application(db, payload, current_user.id)

    if current_user.parsed_resume_data is not None:
        background_tasks.add_task( 
           process_application_scoring,
              application.application_id,
              current_user.id,
              current_user.parsed_resume_data,
              payload.job_description
           )
        

    return application


@router.get("", response_model=list[ApplicationRead])
async def get_applications(db: Session = Depends(get_session), current_user = Depends(get_current_user)):

   applications = get_applications_by_user(db, current_user.id)

   return applications


# GET /applications/{application_id}
@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(application_id: uuid.UUID, db: Session = Depends(get_session), current_user = Depends(get_current_user)):

   application = get_application_by_id(db, application_id, current_user.id)

   if not application:
      raise HTTPException(status_code=404, detail="Application not found")
   
   return application




# PATCH /{application_id}
@router.patch("/{application_id}", response_model=ApplicationRead)
async def patch_application(payload: ApplicationStatusUpdate, application_id: uuid.UUID, db: Session = Depends(get_session), current_user = Depends(get_current_user)):

   
   
   updated_application =  update_application_status(db, application_id, current_user.id, payload.status)

   if  updated_application is None:
      raise HTTPException(status_code=404, detail="Application not found")
   
   return updated_application
   



# DELETE /{application_id}
@router.delete("/{application_id}", status_code=204)
async def delete(application_id: uuid.UUID, db: Session = Depends(get_session), current_user = Depends(get_current_user)):

   result = delete_application(db, application_id, current_user.id)

   if not result.get("ok"):
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )
      