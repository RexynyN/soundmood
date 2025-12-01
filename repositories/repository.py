from datetime import datetime
from typing import List, Optional
from database.models import History, session

class HistoryRepository:
    def insert_record(self, link: str, store: str, price: float, product_id: int = 0) -> int:
        history = History(
            link=link,
            store=store,
            price=price,
            product_id=product_id,
            datestamp=datetime.now()
        )
        session.add(history)
        session.commit()
        return history.id

    def delete_record(self, id: int) -> bool:
        history = session.query(History).get(id)
        if not history:
            return False
        
        session.delete(history)
        session.commit()
        return True

    def update_record(self, id: int, link: str, store: str, price: float, product_id: int):
        history = session.query(History).get(id)
        if not history:
            return None

        history.link = link
        history.store = store
        history.price = price
        history.product_id = product_id
        session.commit()
        
        return history

    def get_record(self, id: int) -> Optional[History]:
        return session.query(History).get(id)

    def get_by_product_id(self, prod_id: int, days: int) -> List[History]:
        date = get_anomesdia(days_delta=days)

        return session.query(History).filter(
            History.product_id == prod_id,
            History.datestamp >= date
        ).all()

    def get_by_product_name(self, prod_name: str, days: int) -> List[History]:
        date = get_anomesdia(days_delta=days)
        return session.query(History).join(Product).filter(
            Product.name.ilike(f"%{prod_name}%"),
            History.datestamp >= date
        ).all()

    def get_all_records(self, limit: int = 1000, orderby: str = "desc") -> List[History]:
        order = History.id.desc() if orderby.lower() == "desc" else History.id.asc()
        return session.query(History).order_by(order).limit(limit).all()



