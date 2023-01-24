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
# Enums for Address
# #####################################################
address_type = (
    "company address",
    "private address",
    "mailing address",
    "temporary address",
    "one time address",
)
address_type_enum = Enum(*address_type, name="address_type", native_enum=False)

# #####################################################
# Enums for Person
# #####################################################
person_type = ("Legal Person", "Natural Person")
person_type_enum = Enum(*person_type, name="person_type", native_enum=False)

language = ("german", "english", "french", "italian")
language_enum = Enum(*language, name="language", native_enum=False)

legal_form = ("Limited", "Listed", "Single Owner")
legal_form_enum = Enum(*legal_form, name="legal_form", native_enum=False)

gender = ("male", "female", "other")
gender_enum = Enum(*gender, name="gender", native_enum=False)

marital_status = ("single", "married", "divorced", "seperated", "widowed")
marital_status_enum = Enum(*marital_status, name="marital_status", native_enum=False)

permit_type = ("None", "Type C", "Type G", "Type S", "other")
permit_type_enum = Enum(*permit_type, name="permit_type", native_enum=False)

own_employee = ("Regular", "Executive", "Board", "other")
own_employee_enum = Enum(
    *own_employee, name="own_employee", native_enum=False
)

# #####################################################
# Enums for User
# #####################################################
notification_frequency = (
    "daily",
    "every other day",
    "weekly",
    "monthly",
)
notification_frequency_enum = Enum(
    *notification_frequency, name="notification_frequency", native_enum=False
)

# #####################################################
# Enums for PersonRole
# #####################################################
person_roles = (
    "Account Manager",
    "Commercial Card Holder",
    "Primary Card Holder",
    "Supplementary Card Holder",
    "Beneficial Owner",
    "Authorised Signatory",
    "Power of Attorney",
    "Bank Contact - RM",
    "Bank Contact - Administration Officer",
    "Controlling Owner",
    "Founder",
    "Beneficiary",
    "Grantor",
    "Settlor",
    "Member Get Member",
    "Partner Plus Benefit Contact",
    "Protector",
    "Trustee",
    "Other",
    "V-Payment Administrator",
)
person_role_enum = Enum(*person_roles, name="person_roles", native_enum=False)

signatory_statuses = (
    "Without Authorization To Sign",
    "Individual Signature",
    "Single Signature (with restriction)",
    "Joint Signature At Two",
    "Joint Signature At Two (with restriction)",
    "Joint Signature At Three",
    "Joint Signature At Three (with restriction)",
    "Joint Signature At Four",
    "Joint Signature At Four (with restriction)",
    "Joint Signature At Five",
    "Joint Signature At Five (with restriction)",
    "Individual Procuration",
    "Individual Procuration (with restriction)",
    "Joint Agent Signature At Two",
    "Joint Agent Signature At Two (with restriction)",
    "Joint Agent Signature At Three",
    "Joint Agent Signature At Three (with restriction)",
    "Other",
)
signatory_status_enum = Enum(
    *signatory_statuses, name="signatory_status", native_enum=False
)

poa_types = (
    "Power of Attorny for Natural Person",
    "Power of Attorny for Legal Person",
    "CPC Power of Attorny",
)
poa_type_enum = Enum(*poa_types, name="poa_type", native_enum=False)

# #####################################################
#     Sub Structure components
# #####################################################

# openapi component spec for address
address = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "address_type": {
                "type": "string",
                "enum": address_type,
                "x-nullable": True,
            },
            "line1": {"type": "string", "x-nullable": True},
            "line2": {"type": "string", "x-nullable": True},
            "line3": {"type": "string", "x-nullable": True},
            "zip_code": {"type": "string", "x-nullable": True},
            "city": {"type": "string", "x-nullable": True},
            "state": {"type": "string", "x-nullable": True},
            "country_name": {"type": "string", "x-nullable": True},
            "country_iso3": {"type": "string", "x-nullable": True},
        },
    },
}

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


address_person_association_table = Table(
    "address_use",
    Base.metadata,
    Column("person_id", Integer, ForeignKey("person.person_id"), primary_key=True),
    Column("address_id", Integer, ForeignKey("address.address_id"), primary_key=True),
)


class Address(AuditAPI, Base):
    """
    Generic Address Entity to be used for Address_Use
    """

    __tablename__ = "address"
    address_id = Column(Integer, primary_key=True, autoincrement=True)
    address_type = Column(address_type_enum, nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String)
    address_line3 = Column(String)
    zip_code = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String)

    status = Column(
        status_enum,
        nullable=False,
        comment="Current Status of Address record",
    )

    source = Column(
        String, nullable=False, comment="Raw data / source system original source"
    )

    def __repr__(self):
        return f"{self.id} {self.address_type} {self.city} {self.status}"


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
        "addresses": address,
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

    person_type = Column(
        person_type_enum,
        nullable=False,
        comment="Person's Type - either Legal or Natural Person",
    )

    #    ''' First Block of Natural Person attributes '''
    salutation = Column(String, nullable=False, comment="Person Salutation")
    title = Column(String, nullable=False, comment="Person Title")
    first_name = Column(String, nullable=False, comment="Person First Name")
    last_name = Column(String, nullable=False, comment="Person Last Name")
    gender = Column(gender_enum, nullable=False, comment="Person Gender")
    date_of_birth = Column(DATE, nullable=False, comment="Person Date of Birth")
    poa_seccode = Column(String, nullable=False)

    permit_since = Column(
        DATE, nullable=False, comment="Person Date Permit received first time"
    )
    permit_type = Column(permit_type_enum, nullable=False, comment="Person Permit Type")
    ch_residency_since = Column(
        DATE, nullable=False, comment="Person's first date of Swiss residency"
    )
    marital_status = Column(
        marital_status_enum, nullable=False, comment="Person Marital Status"
    )

    id_document_type = Column(String, nullable=False)
    id_document_number = Column(String, nullable=False)

    email = Column(String, nullable=False, comment="Natural Person email address")
    phone_business_mobile = Column(
        String, nullable=False, comment="Natural Person business mobile phone number"
    )
    phone_mobile = Column(
        String, nullable=False, comment="Natural Person mobile phone number"
    )
    phone_private = Column(
        String, nullable=False, comment="Natural Person private phone number"
    )
    fax = Column(String, nullable=False)

    occupation = Column(String, comment="Person occupational description")
    department = Column(
        String, comment="Person departmental / organizational link within employer"
    )
    employee_reference_id = Column(String)
    employed_since = Column(DATE, nullable=False, comment="Person employed since Date")
    employment_type = Column(
        String, nullable=False, comment="Person Employment Type => possibly enum"
    )
    income_gross_annual = Column(
        Float, nullable=False, comment="Person gross annual income"
    )
    income_change_date = Column(
        DATE, nullable=False, comment="Person income change date"
    )
    own_employee = Column(
        own_employee_enum,
        nullable=False,
        comment="Person's Own Employee Type / Status",
    )

    #    ''' Second Block of Legal Person attributes '''
    company_name = Column(String, nullable=False, comment="Company Full Name")
    legal_form = Column(
        legal_form_enum, nullable=False, comment="Legal form of Company"
    )
    noga_code = Column(
        String,
        nullable=False,
        comment="Company Industry Classification along NOGA Code standard",
    )
    noga_description = Column(
        String,
        nullable=False,
        comment="Company Industry Classification along NOGA description",
    )
    stock_exchange = Column(
        String, nullable=False, comment="Stock Exchange where Company is listed"
    )
    main_stock_exchange = Column(
        String,
        nullable=False,
        comment="Stock Exchange where Company's Ultimate Parent is listed",
    )
    stock_exchange_code = Column(String, nullable=False)
    share_capital = Column(Float, nullable=False)
    parent = Column(
        Integer,
        ForeignKey("person.person_id"),
        comment="ID of direct Parent Company (FK to another Legal Person)",
    )
    assets_of_company = Column(Float, nullable=False)
    foundation_date = Column(DATE, nullable=False, comment="Company Foundation Date")
    commercial_register_name = Column(String, nullable=False)
    hr_registration_number = Column(String, nullable=False)
    comercial_register_date = Column(DATE, nullable=False)
    operational_activity = Column(String, nullable=False)
    number_of_employees = Column(Integer, nullable=False)

    #    ''' Third Block of attributes related to both Legal & Natural Persons '''
    language = Column(
        language_enum,
        nullable=False,
        comment="Default communications language for Person",
    )

    phone_business = Column(
        String, nullable=False, comment="Legal Person business phone number"
    )

    bank_name = Column(
        String,
        nullable=False,
        comment="Legal Person CH Reference Bank Name (BIC or Name)",
    )
    bank_iban = Column(
        String,
        nullable=False,
        comment="Legal Person CH Reference Bank Account Number (IBAN)",
    )

    consent_email = Column(Boolean, comment="Person marketing consent for email")
    consent_mobile = Column(Boolean, comment="Person marketing consent for mobile")
    credit_risk_score = Column(
        Float, nullable=False, comment="Person Credit Risk Code or Rating"
    )

    address_links = relationship(Address, secondary=address_person_association_table)

    status = Column(
        status_enum,
        nullable=False,
        comment="Current Status of Person",
    )
    tags = relationship(TaggableEntity, secondary=tagging_table)

    source = Column(
        String, nullable=False, comment="Raw data / source system original source"
    )


class PersonRole(AuditAPI, Base):
    __generate_api__ = True
    __tablename__ = "person_role"
    # __related__ = {"person": "Person", "entity": "TaggableEntity"}
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Obj Id for the person role",
    )
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    role = Column(person_role_enum, nullable=False)
    signatory_status = Column(signatory_status_enum, nullable=False)
    poa_type = Column(poa_type_enum, nullable=False)
    main_auth_rep = Column(Boolean, nullable=False)
    start_date_poa = Column(DATE, nullable=False)
    end_date_poa = Column(DATE, nullable=False)
    dms_link = Column(String, nullable=False)
    dms_document_typ = Column(String, nullable=False)
    taggable_entity_id = Column(
        Integer, ForeignKey("taggable_entity.id"), nullable=False
    )
    person = relationship("Person", backref="roles")
    entity = relationship("TaggableEntity", backref="involved_persons")
    __table_args__ = (
        UniqueConstraint(
            "person_id", "role", "taggable_entity_id", name="_person_role_uc1"
        ),
    )


organizations_users_association_table = Table(
    "organizations_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("organization_id", Integer, ForeignKey("organization.id"), primary_key=True),
)

"""  # #####################################################
     # Internal Roles & Access rights on the DB & API Schema
     # #####################################################  """


class Organization(AuditAPI, Base):
    __generate_api__ = {"find", "create", "read", "update", "delete"}
    __tablename__ = "organization"
    __related__ = {"users": "User"}
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID of organisation which user belong to",
    )
    name = Column(
        String, nullable=False, comment="Name of organisation which user belong to"
    )
    owner = Column(
        String, nullable=False, comment="Owner of organisation which user belong to"
    )
    users = relationship(
        "User",
        secondary=organizations_users_association_table,
    )

    def __repr__(self):
        return self.name


class User(AuditAPI, Base):
    __generate_api__ = True
    __tablename__ = "user"
    __related__ = {"organizations": "Organization"}
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID of user")

    username = Column(
        String, nullable=False, comment="Account name of user for loging this app"
    )
    email = Column(String, nullable=False, comment="Email of user")
    name = Column(String, nullable=False, comment="Name of user")
    notification_frequency = Column(
        notification_frequency_enum,
        nullable=False,
        comment="How often does user want to be notified of tasks",
    )
    organizations = relationship(
        "Organization",
        secondary=organizations_users_association_table,
    )

    def __repr__(self):
        return self.username


# #######################################################################################################
# Create all tables in the DB
# #######################################################################################################

# db.create_all()
