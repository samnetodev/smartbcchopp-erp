"""fix usuario_id fks to reference usuario

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-31 10:30:00.000000

"""
from alembic import op

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

TABLES = (
    'auditoria',
    'documento',
    'veiculo_historico',
    'chopeira_historico',
    'inventario',
    'movimentacao',
)


def upgrade() -> None:
    for table in TABLES:
        op.execute(
            f'ALTER TABLE {table} '
            f'DROP CONSTRAINT {table}_usuario_id_fkey, '
            f'ADD CONSTRAINT {table}_usuario_id_fkey '
            f'FOREIGN KEY (usuario_id) REFERENCES usuario(id)'
        )


def downgrade() -> None:
    for table in TABLES:
        op.execute(
            f'ALTER TABLE {table} '
            f'DROP CONSTRAINT {table}_usuario_id_fkey, '
            f'ADD CONSTRAINT {table}_usuario_id_fkey '
            f'FOREIGN KEY (usuario_id) REFERENCES funcionario(id)'
        )
