from typing_extensions import Annotated

from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, Dict, Union


class DownloadData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: HttpUrl
    file_name: Annotated[str, Field(exclude=True)] = None
    method: str = "GET"
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    data: Optional[Union[str, Dict]] = None
    cookies: Annotated[str, Field(exclude=True)] = None
    host: Annotated[str, Field(exclude=True)] = None
    referer: Annotated[str, Field(exclude=True)] = None
    verify: Optional[bool] = True
    is_image: Annotated[bool, Field(exclude=True)] = False
    order: Annotated[int, Field(exclude=True)] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.host:
            self.headers["Host"] = self.host
        if self.referer:
            self.headers["Referer"] = self.referer
        if self.cookies:
            self.headers["Cookie"] = self.cookies
