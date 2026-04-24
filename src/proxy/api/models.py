from datetime import datetime

from pydantic import BaseModel

from movienight.schemas.proposal import CreateProposalRequest


class InternalUserCreateRequest(BaseModel):
    username: str
    password_hash: str
    created_at: datetime


class InternalProposalCreateRequest(BaseModel):
    payload: CreateProposalRequest
    current_user_id: int


class InternalProposalDeleteRequest(BaseModel):
    proposal_id: int
    current_user_id: int


class InternalVoteRequest(BaseModel):
    proposal_id: int
    current_user_id: int


class InternalReactionRequest(BaseModel):
    proposal_id: int
    category: str
    current_user_id: int


class InternalUserIdRequest(BaseModel):
    user_id: int


class InternalUsernameRequest(BaseModel):
    username: str


class InternalRevokedTokenExistsRequest(BaseModel):
    jti: str


class InternalRevokedTokenCreateRequest(BaseModel):
    jti: str
    expires_at: datetime
    reason: str = "logout"


class InternalHomeRequest(BaseModel):
    current_user_id: int
    mine_only: bool = False