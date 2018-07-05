"""basic benchmark

Revision ID: 5b0f7063808d
Revises: 
Create Date: 2018-07-05 13:02:38.458322

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5b0f7063808d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('retweeted_users_1')
    op.drop_table('hash_activity_2')
    op.drop_table('retweeted_users_7')
    op.drop_table('retweeted_tweets_2')
    op.drop_table('hash_activity_28')
    op.drop_table('retweeted_users_2')
    op.drop_table('dist_activity_1')
    op.drop_table('dist_activity_28')
    op.drop_table('hash_activity_1')
    op.drop_table('retweeted_tweets_28')
    op.drop_table('dist_activity_2')
    op.drop_table('dist_activity_7')
    op.drop_table('retweeted_users_28')
    op.drop_table('retweeted_tweets_1')
    op.drop_table('hash_activity_7')
    op.drop_table('retweeted_tweets_7')
    op.create_index(op.f('ix_District_district_name'), 'District', ['district_name'], unique=False)
    op.drop_index('district_district_name_idx', table_name='District')
    op.create_index(op.f('ix_Hashtag_hashtag'), 'Hashtag', ['hashtag'], unique=False)
    op.drop_index('hashtag_hashtag_idx', table_name='Hashtag')
    op.create_index(op.f('ix_Post_created_at'), 'Post', ['created_at'], unique=False)
    op.create_index(op.f('ix_Post_original_author_scrname'), 'Post', ['original_author_scrname'], unique=False)
    op.drop_index('post_created_at_idx', table_name='Post')
    op.drop_index('post_original_author_scrname_idx', table_name='Post')
    op.drop_index('post_post_id_idx', table_name='Post')
    op.drop_column('Post', 'original_text_created_at')
    op.create_index(op.f('ix_User_user_cap_perc'), 'User', ['user_cap_perc'], unique=False)
    op.create_index(op.f('ix_User_user_scrname'), 'User', ['user_scrname'], unique=False)
    op.drop_index('user_user_cap_perc_idx', table_name='User')
    op.drop_index('user_user_scrname_idx', table_name='User')
    op.alter_column('postdist_assoc', 'district_name',
               existing_type=mysql.VARCHAR(length=12),
               nullable=True)
    op.alter_column('postdist_assoc', 'post_id',
               existing_type=mysql.VARCHAR(length=25),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('postdist_assoc', 'post_id',
               existing_type=mysql.VARCHAR(length=25),
               nullable=False)
    op.alter_column('postdist_assoc', 'district_name',
               existing_type=mysql.VARCHAR(length=12),
               nullable=False)
    op.create_index('user_user_scrname_idx', 'User', ['user_scrname'], unique=False)
    op.create_index('user_user_cap_perc_idx', 'User', ['user_cap_perc'], unique=False)
    op.drop_index(op.f('ix_User_user_scrname'), table_name='User')
    op.drop_index(op.f('ix_User_user_cap_perc'), table_name='User')
    op.add_column('Post', sa.Column('original_text_created_at', mysql.CHAR(length=19), nullable=True))
    op.create_index('post_post_id_idx', 'Post', ['post_id'], unique=False)
    op.create_index('post_original_author_scrname_idx', 'Post', ['original_author_scrname'], unique=False)
    op.create_index('post_created_at_idx', 'Post', ['created_at'], unique=False)
    op.drop_index(op.f('ix_Post_original_author_scrname'), table_name='Post')
    op.drop_index(op.f('ix_Post_created_at'), table_name='Post')
    op.create_index('hashtag_hashtag_idx', 'Hashtag', ['hashtag'], unique=False)
    op.drop_index(op.f('ix_Hashtag_hashtag'), table_name='Hashtag')
    op.create_index('district_district_name_idx', 'District', ['district_name'], unique=False)
    op.drop_index(op.f('ix_District_district_name'), table_name='District')
    op.create_table('retweeted_tweets_7',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('original_post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('hash_activity_7',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('hash_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('hashtag', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('retweeted_tweets_1',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('original_post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('retweeted_users_28',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('original_author_scrname', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('dist_activity_7',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('district_name', mysql.VARCHAR(length=12), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('dist_activity_2',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('district_name', mysql.VARCHAR(length=12), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('retweeted_tweets_28',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('original_post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('hash_activity_1',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('hash_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('hashtag', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('dist_activity_28',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('district_name', mysql.VARCHAR(length=12), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('dist_activity_1',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('district_name', mysql.VARCHAR(length=12), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('retweeted_users_2',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('original_author_scrname', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('hash_activity_28',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('hash_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('hashtag', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('retweeted_tweets_2',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('original_post_id', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('retweeted_users_7',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('original_author_scrname', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('hash_activity_2',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('hash_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('hashtag', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('retweeted_users_1',
    sa.Column('rank', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('original_author_scrname', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('rank'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
