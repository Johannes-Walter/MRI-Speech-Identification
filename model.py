from sqlalchemy import (
    DATE,
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from apigenerator.api_classes import AuditAPI, minio_file_list, minio_file_structure, role_access, roles
from swagger_server.globals import db

"""
client_consul = None
consul_config = None
minio_client = None
minio_external_client = None
"""


session = db.session
Base = db.Model

# #####################################################
#     Generic Enum Definitions
# #####################################################
entity_type = ("Entry", "Person")
entity_type_enum = Enum(*entity_type, name="entity_type", native_enum=False)

status = ("Active", "DQ Earmark", "Blocked", "Closed")
status_enum = Enum(*status, name="status", native_enum=False)

# #####################################################
# Enums for Person
# #####################################################
gender = ("male", "female", "other")
gender_enum = Enum(*gender, name="gender", native_enum=False)

# openapi component spec for list of URL's
url_list = {"type": "array", "items": {"type": "string"}}



# #####################################################
#     ORM Model of the DB Schema
# #####################################################
#     Tagging Framework
# #####################################################

tagging_table = Table(
    "tagging",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.id")),
    Column("entity_id", Integer, ForeignKey("taggable_entity.id")),
)


class Tag(AuditAPI, Base):
    __tablename__ = "tag"
    __related__ = {"tagged_entities": "TaggableEntity"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(100), unique=True)
    tagged_entities = relationship(
        "TaggableEntity", secondary=tagging_table, back_populates="tags"
    )

    def __repr__(self):
        return self.description


class TaggableEntity(AuditAPI, Base):
    __generate_api__ = {"find"}  # , 'read'}
    __tablename__ = "taggable_entity"
    __related__ = {"tags": "Tag"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(entity_type_enum)
    tags = relationship(
        "Tag", secondary=tagging_table, back_populates="tagged_entities"
    )
    __mapper_args__ = {"polymorphic_identity": "Entry", "polymorphic_on": entity_type}



# #####################################################
#     Core Entities - Master - Basic - Card - Person  #
# #####################################################

class Person(TaggableEntity):
    __generate_api__ = True
    __tablename__ = "person"
    __related__ = {
        "tags": "TaggableEntity",
    }
    __special_types__ = {
        "person_document_link": minio_file_structure,
        "person_document_url": minio_file_list,
        "id_document_url": minio_file_list,
    }
    __mapper_args__ = {
        "polymorphic_identity": "Person",
    }

    person_id = Column(
        Integer,
        ForeignKey("taggable_entity.id"),
        primary_key=True,
        comment="ID of each record in person entity",
    )
    
    #    ''' First Block of Natural Person attributes '''
    gender = Column(gender_enum, nullable=False, comment="Person Gender")
    age = Column(Integer, nullable=False, comment="Person Age")

    #    ''' Third Block of attributes related to both Legal & Natural Persons '''
    language = Column(
        String,
        nullable=False,
        comment="Default communications language for Person",
    )
    tags = relationship(TaggableEntity, secondary=tagging_table)


# db.create_all()
