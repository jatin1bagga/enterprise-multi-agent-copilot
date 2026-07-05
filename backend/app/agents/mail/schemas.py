from pydantic import BaseModel


class MailResult(BaseModel):
    to: str
    subject: str
    attachments: list[str]
    status: str
