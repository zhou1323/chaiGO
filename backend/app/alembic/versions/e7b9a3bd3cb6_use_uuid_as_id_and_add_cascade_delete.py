"""Use UUID as id and add cascade delete

Revision ID: e7b9a3bd3cb6
Revises: 1c94acfdf795
Create Date: 2024-07-25 22:59:16.423177

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e7b9a3bd3cb6"
down_revision = "1c94acfdf795"
branch_labels = None
depends_on = None


def upgrade():
    # Ensure uuid-ossp extension is available
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create a new UUID column with a default UUID value
    op.add_column(
        "user",
        sa.Column(
            "new_id",
            postgresql.UUID(as_uuid=True),
            default=sa.text("uuid_generate_v4()"),
        ),
    )
    op.add_column(
        "receipt",
        sa.Column(
            "new_id",
            postgresql.UUID(as_uuid=True),
            default=sa.text("uuid_generate_v4()"),
        ),
    )
    op.add_column(
        "receipt",
        sa.Column("new_owner_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "receipt_item",
        sa.Column(
            "new_id",
            postgresql.UUID(as_uuid=True),
            default=sa.text("uuid_generate_v4()"),
        ),
    )
    op.add_column(
        "receipt_item",
        sa.Column(
            "new_receipt_id",
            postgresql.UUID(as_uuid=True),
            default=sa.text("uuid_generate_v4()"),
        ),
    )

    # Populate the new columns with UUIDs
    op.execute('UPDATE "user" SET new_id = uuid_generate_v4()')
    op.execute("UPDATE receipt SET new_id = uuid_generate_v4()")
    op.execute(
        'UPDATE receipt SET new_owner_id = (SELECT new_id FROM "user" WHERE "user".id = receipt.owner_id)'
    )
    op.execute("UPDATE receipt_item SET new_id = uuid_generate_v4()")
    op.execute(
        'UPDATE receipt_item SET new_receipt_id = (SELECT new_id FROM "receipt" WHERE "receipt".id = receipt_item.receipt_id)'
    )

    # Set the new_id as not nullable
    op.alter_column("user", "new_id", nullable=False)
    op.alter_column("receipt", "new_id", nullable=False)
    op.alter_column("receipt_item", "new_id", nullable=False)

    # Drop old columns and rename new columns
    op.drop_constraint("receipt_owner_id_fkey", "receipt", type_="foreignkey")
    op.drop_column("receipt", "owner_id")
    op.alter_column("receipt", "new_owner_id", new_column_name="owner_id")

    op.drop_constraint(
        "receipt_item_receipt_id_fkey", "receipt_item", type_="foreignkey"
    )
    op.drop_column("receipt_item", "receipt_id")
    op.alter_column("receipt_item", "new_receipt_id", new_column_name="receipt_id")

    op.drop_column("user", "id")
    op.alter_column("user", "new_id", new_column_name="id")

    op.drop_column("receipt", "id")
    op.alter_column("receipt", "new_id", new_column_name="id")

    op.drop_column("receipt_item", "id")
    op.alter_column("receipt_item", "new_id", new_column_name="id")

    # Create primary key constraint
    op.create_primary_key("user_pkey", "user", ["id"])
    op.create_primary_key("receipt_pkey", "receipt", ["id"])
    op.create_primary_key("receipt_item_pkey", "receipt_item", ["id"])

    # Recreate foreign key constraint
    op.create_foreign_key(
        "receipt_owner_id_fkey", "receipt", "user", ["owner_id"], ["id"]
    )
    op.create_foreign_key(
        "receipt_item_receipt_id_fkey",
        "receipt_item",
        "receipt",
        ["receipt_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column(
        "receipt_item",
        "quantity",
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        existing_nullable=False,
    )

    # ### end Alembic commands ###


def downgrade():
    # Reverse the upgrade process
    op.add_column("user", sa.Column("old_id", sa.Integer, autoincrement=True))
    op.add_column("receipt", sa.Column("old_id", sa.Integer, autoincrement=True))
    op.add_column("receipt", sa.Column("old_owner_id", sa.Integer, nullable=True))
    op.add_column("receipt_item", sa.Column("old_id", sa.Integer, autoincrement=True))
    op.add_column(
        "receipt_item", sa.Column("old_receipt_id", sa.Integer, autoincrement=True)
    )

    # Populate the old columns with default values
    # Generate sequences for the integer IDs if not exist
    op.execute(
        'CREATE SEQUENCE IF NOT EXISTS user_id_seq AS INTEGER OWNED BY "user".old_id'
    )
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS receipt_id_seq AS INTEGER OWNED BY receipt.old_id"
    )
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS receipt_item_id_seq AS INTEGER OWNED BY receipt_item.old_id"
    )

    op.execute(
        "SELECT setval('user_id_seq', COALESCE((SELECT MAX(old_id) + 1 FROM \"user\"), 1), false)"
    )
    op.execute(
        "SELECT setval('receipt_id_seq', COALESCE((SELECT MAX(old_id) + 1 FROM receipt), 1), false)"
    )
    op.execute(
        "SELECT setval('receipt_item_id_seq', COALESCE((SELECT MAX(old_id) + 1 FROM receipt_item), 1), false)"
    )

    op.execute("UPDATE \"user\" SET old_id = nextval('user_id_seq')")
    op.execute(
        'UPDATE receipt SET old_id = nextval(\'receipt_id_seq\'), old_owner_id = (SELECT old_id FROM "user" WHERE "user".id = receipt.owner_id)'
    )
    op.execute(
        "UPDATE receipt_item SET old_id = nextval('receipt_item_id_seq'), old_receipt_id = (SELECT old_id FROM receipt WHERE receipt.id = receipt_item.receipt_id)"
    )

    # Drop new columns and rename old columns back
    op.drop_constraint("receipt_owner_id_fkey", "receipt", type_="foreignkey")
    op.drop_column("receipt", "owner_id")
    op.alter_column("receipt", "old_owner_id", new_column_name="owner_id")

    op.drop_constraint(
        "receipt_item_receipt_id_fkey", "receipt_item", type_="foreignkey"
    )
    op.drop_column("receipt_item", "receipt_id")
    op.alter_column("receipt_item", "old_receipt_id", new_column_name="receipt_id")

    op.drop_column("user", "id")
    op.alter_column("user", "old_id", new_column_name="id")

    op.drop_column("receipt", "id")
    op.alter_column("receipt", "old_id", new_column_name="id")

    op.drop_column("receipt_item", "id")
    op.alter_column("receipt_item", "old_id", new_column_name="id")

    # Create primary key constraint
    op.create_primary_key("user_pkey", "user", ["id"])
    op.create_primary_key("receipt_pkey", "receipt", ["id"])
    op.create_primary_key("receipt_item_pkey", "receipt_item", ["id"])

    # Recreate foreign key constraint
    op.create_foreign_key(
        "receipt_owner_id_fkey", "receipt", "user", ["owner_id"], ["id"]
    )
    op.create_foreign_key(
        "receipt_item_receipt_id_fkey",
        "receipt_item",
        "receipt",
        ["receipt_id"],
        ["id"],
    )

    op.alter_column(
        "receipt_item",
        "quantity",
        existing_type=sa.Float(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
