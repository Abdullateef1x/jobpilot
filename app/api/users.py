from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session

from app.core.database import get_session
from app.crud.user import update_user_resume_key
from app.models.user import User
from app.services.deps import get_current_user
from app.services.storage import get_resume_url, upload_resume

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/me/resume")
async def upload_resume_route(
    file: UploadFile,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    if current_user.id is None: 
        raise HTTPException(status_code=500, detail="Server error: Authenticated object should have an ID but doesn't")
    
    if file.filename is None:
         raise HTTPException(status_code=404, detail="No file was provided")
    
    file_bytes = await file.read()
    key = upload_resume(file_bytes, file.filename, current_user.id)

    update_user_resume_key(db, current_user, key)

    resume_url = get_resume_url(key, current_user.id)

    return resume_url
    