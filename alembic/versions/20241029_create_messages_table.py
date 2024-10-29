from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

revision = '20241029'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        'uploaded_files',
        Column('id', Integer, primary_key=True),
        Column('filename', String, index=True),
        Column('file_path', String, unique=True),
        Column('file_type', String),
        Column('file_size', Integer),
        Column('timestamp', DateTime, server_default=func.now())
    )

    op.create_table(
        'messages',
        Column('id', Integer, primary_key=True, index=True),
        Column('sender_id', Integer, ForeignKey('users.id')),
        Column('receiver_id', Integer, ForeignKey('users.id')),
        Column('content', String),
        Column('timestamp', DateTime, server_default=func.now()),
        Column('file_id', Integer, ForeignKey('uploaded_files.id'), nullable=True)
    )

    op.create_table(
        'chats',
        Column('id', Integer, primary_key=True, index=True),
        Column('user1_id', Integer, ForeignKey('users.id')),
        Column('user2_id', Integer, ForeignKey('users.id'))
    )


def downgrade():
    op.drop_table('messages')
    op.drop_table('uploaded_files')
    op.drop_table('chats')
