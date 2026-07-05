from pydantic import BaseModel


class PythonExecResult(BaseModel):
    code: str
    stdout: str
    artifact_paths: list[str]
