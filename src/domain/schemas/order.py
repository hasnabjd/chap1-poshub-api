from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, StrictFloat, StrictStr


class OrderIn(BaseModel):
    customer_name: StrictStr = Field(alias="nom_client", max_length=128)
    total_amount: StrictFloat = Field(alias="montant", ge=0)
    currency: StrictStr = Field(alias="devise", pattern="^[A-Z]{3}$")

    model_config = {
        "strict": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {"nom_client": "hasna", "montant": 99.99, "devise": "EUR"}
        },
    }


class OrderOut(BaseModel):
    order_id: UUID = Field(alias="order")
    customer_name: StrictStr = Field(alias="nom_client")
    total_amount: StrictFloat = Field(alias="montant")
    currency: StrictStr = Field(alias="devise")
    created_by: Optional[str] = None

    model_config = {
        "strict": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "order": "123e4567-e89b-12d3-a456-426614174000",
                "nom_client": "hasna",
                "montant": 99.99,
                "devise": "EUR",
                "created_by": "admin",
            }
        },
    }
