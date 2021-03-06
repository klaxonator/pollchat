"""add_summ_tables

Revision ID: 37121388a27b
Revises: 5b0f7063808d
Create Date: 2018-07-05 13:21:11.695601

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37121388a27b'
down_revision = '5b0f7063808d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dist_activity_1',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('district_name', sa.String(length=12), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('dist_activity_2',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('district_name', sa.String(length=12), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('dist_activity_28',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('district_name', sa.String(length=12), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('dist_activity_7',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('district_name', sa.String(length=12), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('hash_activity_1',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('hash_id', sa.Integer(), nullable=False),
    sa.Column('hashtag', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('hash_activity_2',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('hash_id', sa.Integer(), nullable=False),
    sa.Column('hashtag', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('hash_activity_28',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('hash_id', sa.Integer(), nullable=False),
    sa.Column('hashtag', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('hash_activity_7',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('hash_id', sa.Integer(), nullable=False),
    sa.Column('hashtag', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_tweets_1',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.String(length=25), nullable=False),
    sa.Column('original_post_id', sa.String(length=25), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_tweets_2',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.String(length=25), nullable=False),
    sa.Column('original_post_id', sa.String(length=25), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_tweets_28',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.String(length=25), nullable=False),
    sa.Column('original_post_id', sa.String(length=25), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_tweets_7',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.String(length=25), nullable=False),
    sa.Column('original_post_id', sa.String(length=25), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_users_1',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('original_author_scrname', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_users_2',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('original_author_scrname', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_users_28',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('original_author_scrname', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('retweeted_users_7',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('original_author_scrname', sa.String(length=50), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('top_tweeters_1',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=25), nullable=False),
    sa.Column('user_scrname', sa.String(length=50), nullable=False),
    sa.Column('user_cap_perc', sa.Float(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('top_tweeters_2',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=25), nullable=False),
    sa.Column('user_scrname', sa.String(length=50), nullable=False),
    sa.Column('user_cap_perc', sa.Float(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('top_tweeters_28',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=25), nullable=False),
    sa.Column('user_scrname', sa.String(length=50), nullable=False),
    sa.Column('user_cap_perc', sa.Float(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    op.create_table('top_tweeters_7',
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=25), nullable=False),
    sa.Column('user_scrname', sa.String(length=50), nullable=False),
    sa.Column('user_cap_perc', sa.Float(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('rank')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('top_tweeters_7')
    op.drop_table('top_tweeters_28')
    op.drop_table('top_tweeters_2')
    op.drop_table('top_tweeters_1')
    op.drop_table('retweeted_users_7')
    op.drop_table('retweeted_users_28')
    op.drop_table('retweeted_users_2')
    op.drop_table('retweeted_users_1')
    op.drop_table('retweeted_tweets_7')
    op.drop_table('retweeted_tweets_28')
    op.drop_table('retweeted_tweets_2')
    op.drop_table('retweeted_tweets_1')
    op.drop_table('hash_activity_7')
    op.drop_table('hash_activity_28')
    op.drop_table('hash_activity_2')
    op.drop_table('hash_activity_1')
    op.drop_table('dist_activity_7')
    op.drop_table('dist_activity_28')
    op.drop_table('dist_activity_2')
    op.drop_table('dist_activity_1')
    # ### end Alembic commands ###
