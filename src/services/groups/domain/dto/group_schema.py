from datetime import datetime

from pydantic import BaseModel

from src.services.groups.domain.entities.group import Group


class CreateGroupRequest(BaseModel):
    name:    str
    subject: str


class AddMemberRequest(BaseModel):
    student_id: int


class GroupMemberResponse(BaseModel):
    id:             int
    student_id:     int
    name:           str
    last_name:      str
    email:          str
    joined_at:      datetime | None
    oauth_provider: str


class GroupResponse(BaseModel):
    id:           int
    name:         str
    subject:      str
    cover_image:  str | None
    professor_id: int
    code:         str
    created_at:   datetime | None
    members:      list[GroupMemberResponse] = []

    @classmethod
    def from_entity(cls, group: Group) -> "GroupResponse":
        return cls(
            id=group.id,
            name=group.name,
            subject=group.subject,
            cover_image=group.cover_image,
            professor_id=group.professor_id,
            code=group.code,
            created_at=group.created_at,
            members=[
                GroupMemberResponse(
                    id=m.id,
                    student_id=m.student_id,
                    name=m.name,
                    last_name=m.last_name,
                    email=m.email,
                    joined_at=m.joined_at,
                    oauth_provider=m.oauth_provider,
                )
                for m in group.members
            ],
        )
