from typing import List, Optional
from app.database.connection import Database
from app.database.connection import get_db_cursor
from app.schemas.artigo import ArtigoCreate, ArtigoUpdate, ArtigoResponse, ArtigoWithAuthors
import logging

from app.schemas.schemas import Artigo
from app.services import estoque_service

logger = logging.getLogger(__name__)

class ArtigoService:
    def __init__(self):
        self.db = Database()

    async def create_artigo(self, artigo_data: ArtigoCreate) -> ArtigoResponse:
        """Criar um novo artigo"""
        with get_db_cursor() as cursor:
            try:
                # Primeiro inserir na tabela Titulo
                titulo_query = """
                    INSERT INTO Titulo (tipo_midia) 
                    VALUES ('artigo') 
                    RETURNING id_titulo
                """
                cursor.execute(titulo_query)
                id_titulo = cursor.fetchone()['id_titulo']
                
                # Depois inserir na tabela Artigos
                artigo_query = """
                    INSERT INTO Artigos (id_artigo, titulo, DOI, publicadora, data_publicacao)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_artigo, titulo, DOI, publicadora, data_publicacao
                """
                cursor.execute(artigo_query, (
                    id_titulo,
                    artigo_data.titulo,
                    artigo_data.DOI,
                    artigo_data.publicadora,
                    artigo_data.data_publicacao
                ))
                
                result = cursor.fetchone()
                # estoque_service.reload_materialized_view()  
                return ArtigoResponse(**result)
                
            except Exception as e:
                logger.error(f"Erro ao criar artigo: {e}")
                raise
            

    async def get_artigo_by_id(self, artigo_id: int) -> Optional[ArtigoResponse]:
        """Buscar artigo por ID"""
        with get_db_cursor() as cursor:
            try:
                query = """
                    SELECT id_artigo, titulo, DOI, publicadora, data_publicacao
                    FROM Artigos 
                    WHERE id_artigo = %s
                """
                cursor.execute(query, (artigo_id,))
                result = cursor.fetchone()
                
                if result:
                    return ArtigoResponse(**result)
                return None
                
            except Exception as e:
                print(f"Erro ao buscar artigo {artigo_id}: {e}")
                logger.error(f"Erro ao buscar artigo {artigo_id}: {e}")
                raise
        

    async def get_artigos(self, skip: int = 0, limit: int = 100) -> List[ArtigoResponse]:
        """Listar artigos com paginação"""
        with get_db_cursor() as cursor:
            try:
                query = """
                    SELECT id_artigo, titulo, DOI, publicadora, data_publicacao
                    FROM Artigos 
                    ORDER BY titulo
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, skip))
                results = cursor.fetchall()
                print(results)
                
                return [Artigo(**row) for row in results]
                
            except Exception as e:
                logger.error(f"Erro ao listar artigos: {e}")
                raise
        

    async def update_artigo(self, artigo_id: int, artigo_data: ArtigoUpdate) -> Optional[Artigo]:
        """Atualizar artigo"""
        with get_db_cursor() as cursor:
            try:
                # Construir query dinamicamente baseado nos campos fornecidos
                fields = []
                values = []
                
                if artigo_data.titulo is not None:
                    fields.append("titulo = %s")
                    values.append(artigo_data.titulo)
                if artigo_data.DOI is not None:
                    fields.append("DOI = %s")
                    values.append(artigo_data.DOI)
                if artigo_data.publicadora is not None:
                    fields.append("publicadora = %s")
                    values.append(artigo_data.publicadora)
                if artigo_data.data_publicacao is not None:
                    fields.append("data_publicacao = %s")
                    values.append(artigo_data.data_publicacao)
                
                if not fields:
                    return await self.get_artigo_by_id(artigo_id)
                
                values.append(artigo_id)
                query = f"""
                    UPDATE Artigos 
                    SET {', '.join(fields)}
                    WHERE id_artigo = %s
                    RETURNING id_artigo, titulo, DOI, publicadora, data_publicacao
                """
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                
                if result:
                    return ArtigoResponse(**result)
                return None
                
            except Exception as e:
                logger.error(f"Erro ao atualizar artigo {artigo_id}: {e}")
                raise
            

    async def delete_artigo(self, artigo_id: int) -> bool:
        """Excluir artigo"""
        with get_db_cursor() as cursor:
            try:
                # Verificar se existe no estoque
                check_query = """
                    SELECT COUNT(*) AS counter 
                    FROM Estoque e
                    INNER JOIN Titulo t ON e.id_titulo = t.id_titulo
                    WHERE t.id_titulo = %s
                """
                cursor.execute(check_query, (artigo_id,))
                count = cursor.fetchone()['counter']
                
                if count > 0:
                    raise ValueError("Não é possível excluir artigo que possui exemplares no estoque")
                
                # Excluir artigo
                delete_artigo_query = "DELETE FROM Artigos WHERE id_artigo = %s"
                cursor.execute(delete_artigo_query, (artigo_id,))
                
                # Excluir da tabela Titulo
                delete_titulo_query = "DELETE FROM Titulo WHERE id_titulo = %s"
                cursor.execute(delete_titulo_query, (artigo_id,))
                
                return cursor.rowcount > 0
                
            except Exception as e:
                logger.error(f"Erro ao excluir artigo {artigo_id}: {e}")
                raise
            

    async def search_artigos(self, query: str) -> List[ArtigoResponse]:
        """Buscar artigos por título, DOI ou publicadora"""
        with get_db_cursor() as cursor:
            try:
                search_query = """
                    SELECT id_artigo, titulo, DOI, publicadora, data_publicacao
                    FROM Artigos 
                    WHERE titulo ILIKE %s OR DOI ILIKE %s OR publicadora ILIKE %s
                    ORDER BY titulo
                """
                search_param = f"%{query}%"
                cursor.execute(search_query, (search_param, search_param, search_param))
                results = cursor.fetchall()
                
                return [
                    ArtigoResponse(**row)
                    for row in results
                ]
                
            except Exception as e:
                logger.error(f"Erro ao buscar artigos: {e}")
                raise
        

    async def get_artigo_with_authors(self, artigo_id: int) -> Optional[ArtigoWithAuthors]:
        """Buscar artigo com seus autores"""
        with get_db_cursor() as cursor:
            try:
                query = """
                    SELECT a.id_artigo, a.titulo, a.DOI, a.publicadora, a.data_publicacao,
                        au.id_autor, au.nome as autor_nome
                    FROM Artigos a
                    LEFT JOIN Autorias aut ON a.id_artigo = aut.id_titulo
                    LEFT JOIN Autores au ON aut.id_autor = au.id_autor
                    WHERE a.id_artigo = %s
                """
                cursor.execute(query, (artigo_id,))
                results = cursor.fetchall()
                
                if not results:
                    return None
                
                # Primeira linha contém dados do artigo
                first_row = results[0]
                artigo = ArtigoWithAuthors(
                    autores=[],
                    **first_row
                )
                
                # Adicionar autores se existirem
                for row in results:
                    if row[5]:  # Se tem autor
                        artigo.autores.append({
                            "id_autor": row[5],
                            "nome": row[6]
                        })
                
                return artigo
                
            except Exception as e:
                logger.error(f"Erro ao buscar artigo com autores {artigo_id}: {e}")
                raise
        
    async def search_artigos(self, q: str):
        with get_db_cursor() as cursor:
            query = """
                SELECT id_artigo, titulo, DOI, publicadora, data_publicacao
                FROM Artigos
                WHERE titulo ILIKE %s OR DOI ILIKE %s
                ORDER BY titulo
                LIMIT 200 
            """
            param = f"%{q}%"
            cursor.execute(query, tuple([param for _ in range(2)]))
            results = cursor.fetchall()
            return [Artigo(**row) for row in results]
