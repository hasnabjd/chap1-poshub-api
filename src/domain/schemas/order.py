from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, StrictFloat, StrictStr


class OrderIn(BaseModel):
    customer_name: Annotated[StrictStr, Field(alias="nom_client", max_length=128)]
    total_amount: Annotated[StrictFloat, Field(alias="montant", ge=0)]
    currency: Annotated[StrictStr, Field(alias="devise", pattern="^[A-Z]{3}$")]

    model_config = {
        "strict": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "nom_client": "John Doe",
                "montant": 99.99,
                "devise": "EUR"
            }
        }
    }


class OrderOut(BaseModel):
    order_id: UUID = Field(alias="order")
    created_at: Annotated[datetime, Field(alias="created_at")]
    customer_name: Annotated[StrictStr, Field(alias="nom_client")]
    total_amount: Annotated[StrictFloat, Field(alias="montant")]
    currency: Annotated[StrictStr, Field(alias="devise")]
    created_by: Optional[str] = None

    model_config = {
        "strict": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "order": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2024-03-20T10:00:00Z",
                "nom_client": "John Doe",
                "montant": 99.99,
                "devise": "EUR",
                "created_by": "admin"
            }
        }
    }
