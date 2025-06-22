"""added users table column unique

Revision ID: 9e4e7584410b
Revises: eea67a4e3de8
Create Date: 2025-06-22 16:56:27.673749

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '9e4e7584410b'
down_revision = 'eea67a4e3de8'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    # First handle tenants table
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=50),
               existing_nullable=False,
               existing_server_default=sa.text("'temp_password'"))
        
        # Check for duplicate emails in tenants
        duplicates = conn.execute(text("""
            SELECT email, COUNT(*) as count 
            FROM tenants 
            GROUP BY email 
            HAVING count > 1
        """)).fetchall()
        
        # Fix duplicates by appending id
        for email, count in duplicates:
            conn.execute(
                text("""
                    UPDATE tenants 
                    SET email = id || '_' || email 
                    WHERE email = :email AND id NOT IN (
                        SELECT MIN(id) FROM tenants WHERE email = :email
                    )
                """),
                {"email": email}
            )
        
        # Now create named constraint
        batch_op.create_unique_constraint('uq_tenants_email', ['email'])

    # Then handle users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=255),
               existing_nullable=False)
        
        # Check for duplicate emails in users
        duplicates = conn.execute(text("""
            SELECT email, COUNT(*) as count 
            FROM users 
            GROUP BY email 
            HAVING count > 1
        """)).fetchall()
        
        # Fix duplicates by appending id
        for email, count in duplicates:
            conn.execute(
                text("""
                    UPDATE users 
                    SET email = id || '_' || email 
                    WHERE email = :email AND id NOT IN (
                        SELECT MIN(id) FROM users WHERE email = :email
                    )
                """),
                {"email": email}
            )
        
        # Now create named constraint
        batch_op.create_unique_constraint('uq_users_email', ['email'])


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_email', type_='unique')
        batch_op.alter_column('password',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)

    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.drop_constraint('uq_tenants_email', type_='unique')
        batch_op.alter_column('password',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False,
               existing_server_default=sa.text("'temp_password'"))