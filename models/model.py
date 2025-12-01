from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ArtigoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    DOI: Optional[str] = Field(None, max_length=100)
    publicadora: Optional[str] = Field(None, max_length=255)
    data_publicacao: Optional[date] = None

class ArtigoCreate(ArtigoBase):
    pass

class ArtigoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    DOI: Optional[str] = Field(None, max_length=100)
    publicadora: Optional[str] = Field(None, max_length=255)
    data_publicacao: Optional[date] = None

class ArtigoResponse(ArtigoBase):
    id_artigo: int
    
    class Config:
        from_attributes = True

class ArtigoWithAuthors(ArtigoResponse):
    autores: list[dict] = []
