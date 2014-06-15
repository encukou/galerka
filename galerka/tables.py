import sqlalchemy


def tables_factory(prefix):

    class Tables:
        metadata = sqlalchemy.MetaData()

        users = sqlalchemy.Table(
            prefix + 'users', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('slug', sqlalchemy.String, index=True),
            sqlalchemy.Column('display_name', sqlalchemy.String),
            sqlalchemy.Column('password', sqlalchemy.String, nullable=True),
            sqlalchemy.Column('gender', sqlalchemy.String, nullable=True),
            sqlalchemy.Column('joined_at', sqlalchemy.DateTime),
        )

        user_aliases = sqlalchemy.Table(
            prefix + 'user_aliases', metadata,
            sqlalchemy.Column('name', sqlalchemy.String, primary_key=True),
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        )

    return Tables
