from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.artigo import ArtigoCreate, ArtigoUpdate, ArtigoResponse, ArtigoWithAuthors
from app.services.artigo_service import ArtigoService

router = APIRouter()
artigo_service = ArtigoService()

@router.post("/", response_model=ArtigoResponse, status_code=201)
async def create_artigo(artigo: ArtigoCreate):
    """Criar um novo artigo"""
    try:
        return await artigo_service.create_artigo(artigo)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{artigo_id}", response_model=ArtigoResponse)
async def get_artigo(artigo_id: int):
    """Buscar artigo por ID"""
    artigo = await artigo_service.get_artigo_by_id(artigo_id)
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    
    return artigo

@router.get("/", response_model=List[ArtigoResponse])
async def list_artigos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Listar artigos com paginação"""
    return await artigo_service.get_artigos(skip=skip, limit=limit)

@router.put("/{artigo_id}", response_model=ArtigoResponse)
async def update_artigo(artigo_id: int, artigo: ArtigoUpdate):
    """Atualizar artigo"""
    try:
        updated_artigo = await artigo_service.update_artigo(artigo_id, artigo)
        if not updated_artigo:
            raise HTTPException(status_code=404, detail="Artigo não encontrado")
        return updated_artigo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{artigo_id}")
async def delete_artigo(artigo_id: int):
    """Excluir artigo"""
    try:
        deleted = await artigo_service.delete_artigo(artigo_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Artigo não encontrado")
        return {"message": "Artigo excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/", response_model=List[ArtigoResponse])
async def search_artigos(q: str = Query(..., min_length=1)):
    """Buscar artigos por título, DOI ou publicadora"""
    return await artigo_service.search_artigos(q)

@router.get("/{artigo_id}/autores", response_model=ArtigoWithAuthors)
async def get_artigo_with_authors(artigo_id: int):
    """Buscar artigo com seus autores"""
    artigo = await artigo_service.get_artigo_with_authors(artigo_id)
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    return artigo


@router.get("/pesquisar/artigos", response_model=List[ArtigoResponse])
async def search_artigos(
    title: Optional[str] = Query(None, description="Título do item a ser pesquisado")
):
    """Buscar itens do estoque a partir do ID do estoque ou da biblioteca"""
    if not title:
        raise HTTPException(status_code=400, detail="Título é obrigatório para busca")
    return await artigo_service.search_artigos(title)