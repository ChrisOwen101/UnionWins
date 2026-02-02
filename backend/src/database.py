"""
Database connection and initialization.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.models import Base

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create tables."""
    inspector = inspect(engine)

    # Check if union_name and emoji columns exist, add them if they don't
    columns = [
        col['name'] for col in inspector.get_columns('union_wins')
    ] if inspector.has_table('union_wins') else []

    if 'union_wins' in inspector.get_table_names():
        with engine.connect() as conn:
            if 'union_name' not in columns:
                # Add the union_name column to existing table
                print("Adding union_name column to union_wins table...")
                conn.execute(
                    text("ALTER TABLE union_wins ADD COLUMN union_name VARCHAR")
                )
                conn.commit()
                print("union_name column added successfully!")

            if 'emoji' not in columns:
                # Add the emoji column to existing table
                print("Adding emoji column to union_wins table...")
                conn.execute(
                    text("ALTER TABLE union_wins ADD COLUMN emoji VARCHAR")
                )
                conn.commit()
                print("emoji column added successfully!")

            if 'win_type' not in columns:
                # Add the win_type column to existing table
                print("Adding win_type column to union_wins table...")
                conn.execute(
                    text("ALTER TABLE union_wins ADD COLUMN win_type VARCHAR")
                )
                conn.commit()
                print("win_type column added successfully!")

            if 'win_types' not in columns:
                # Add the win_types column to existing table (supports multiple types)
                print("Adding win_types column to union_wins table...")
                conn.execute(
                    text("ALTER TABLE union_wins ADD COLUMN win_types VARCHAR")
                )
                conn.commit()
                print("win_types column added successfully!")

            # Add unique constraint on url if it doesn't exist
            try:
                constraints = inspector.get_unique_constraints('union_wins')
                url_constraint_exists = any(
                    'url' in constraint.get('column_names', [])
                    for constraint in constraints
                )

                if not url_constraint_exists:
                    conn.execute(
                        text(
                            "CREATE UNIQUE INDEX IF NOT EXISTS ix_union_wins_url ON union_wins (url)")
                    )
                    conn.commit()
            except Exception as e:
                print(
                    f"Note: Could not add unique constraint (may already exist): {e}"
                )

    # Check newsletter_subscriptions table for new columns
    if inspector.has_table('newsletter_subscriptions'):
        newsletter_columns = [
            col['name'] for col in inspector.get_columns('newsletter_subscriptions')
        ]
        with engine.connect() as conn:
            if 'last_email_sent_at' not in newsletter_columns:
                print(
                    "Adding last_email_sent_at column to newsletter_subscriptions table...")
                conn.execute(
                    text(
                        "ALTER TABLE newsletter_subscriptions ADD COLUMN last_email_sent_at TIMESTAMP")
                )
                conn.commit()
                print("last_email_sent_at column added successfully!")

    # Check scrape_sources table for new columns
    if inspector.has_table('scrape_sources'):
        scrape_columns = [
            col['name'] for col in inspector.get_columns('scrape_sources')
        ]
        with engine.connect() as conn:
            if 'last_scrape_status' not in scrape_columns:
                print("Adding last_scrape_status column to scrape_sources table...")
                conn.execute(
                    text("ALTER TABLE scrape_sources ADD COLUMN last_scrape_status VARCHAR")
                )
                conn.commit()
                print("last_scrape_status column added successfully!")

            if 'last_scrape_error' not in scrape_columns:
                print("Adding last_scrape_error column to scrape_sources table...")
                conn.execute(
                    text("ALTER TABLE scrape_sources ADD COLUMN last_scrape_error TEXT")
                )
                conn.commit()
                print("last_scrape_error column added successfully!")

    Base.metadata.create_all(bind=engine)
    
    # Seed initial scrape sources
    try:
        from src.models import ScrapeSourceDB
        
        initial_sources = [
            ("https://www.aegistheunion.co.uk/news", "Aegis the Union"),
            ("https://artistsunionengland.org.uk/news", "Artists' Union England (AUE)"),
            ("https://aslef.org.uk/media/press-releases", "ASLEF"),
            ("https://www.aep.org.uk/latest-news", "Association of Educational Psychologists (AEP)"),
            ("https://www.afacwa.org/news", "Association of Flight Attendants (AFA)"),
            ("https://www.ahds.org.uk/news", "Association of Headteachers and Deputes in Scotland (AHDS)"),
            ("https://www.ascl.org.uk/news", "Association of School and College Leaders (ASCL)"),
            ("https://bfawu.org/latest-news", "Bakers, Food and Allied Workers Union (BFAWU)"),
            ("https://www.balpa.org/latest", "British Airline Pilots' Association (BALPA)"),
            ("https://www.badn.org.uk/latest-news", "British Association of Dental Nurses (BADN)"),
            ("https://www.rcot.co.uk/latest-news", "British Association of Occupational Therapists (BAOT)"),
            ("https://www.bda.uk.com/news-campaigns", "British Dietetic Association (BDA)"),
            ("https://www.bma.org.uk/news-and-opinion", "British Medical Association (BMA)"),
            ("https://www.orthoptics.org.uk/bostu-news", "British Orthoptic Society Trade Union (BOSTU)"),
            ("https://www.csp.org.uk/news", "Chartered Society of Physiotherapy (CSP)"),
            ("https://www.cwu.org/news-and-activity", "Communication Workers Union (CWU)"),
            ("https://community-tu.org/news", "Community"),
            ("https://www.eis.org.uk/news", "Educational Institute of Scotland (EIS)"),
            ("https://www.equity.org.uk/news", "Equity"),
            ("https://www.fda.org.uk/news", "FDA"),
            ("https://www.fbu.org.uk/news", "Fire Brigades Union (FBU)"),
            ("https://www.gmb.org.uk/news", "GMB"),
            ("https://www.hcsa.com/news", "Hospital Consultants and Specialists Association (HCSA)"),
            ("https://iwgb.org.uk/news", "Independent Workers' Union of Great Britain (IWGB)"),
            ("https://iww.org.uk/news", "Industrial Workers of the World (IWW)"),
            ("https://musiciansunion.org.uk/news", "Musicians' Union (MU)"),
            ("https://www.naht.org.uk/news", "National Association of Head Teachers (NAHT)"),
            ("https://www.napo.org.uk/news", "National Association of Probation Officers (NAPO)"),
            ("https://naors.co.uk", "National Association of Racing Staff (NARS)"),
            ("https://www.nasuwt.org.uk/news", "National Association of Schoolmasters Union of Women Teachers (NASUWT)"),
            ("https://neu.org.uk/press-releases", "National Education Union (NEU)"),
            ("https://yoursa.org.uk", "National House Building Council Staff Association (NHBCSA)"),
            ("https://www.nsead.org/news", "National Society for Education in Art and Design (NSEAD)"),
            ("https://www.nuj.org.uk/news", "National Union of Journalists (NUJ)"),
            ("https://num.org.uk", "National Union of Mineworkers (NUM)"),
            ("https://nupfc.com/latest-news", "National Union of Professional Foster Carers (NUPFC)"),
            ("https://www.rmt.org.uk/news", "National Union of Rail, Maritime and Transport Workers (RMT)"),
            ("https://ngsu.org.uk/news", "Nationwide Group Staff Union (NGSU)"),
            ("https://www.nautilus-intl.org/news", "Nautilus UK"),
            ("https://www.poauk.org.uk/news-room", "Prison Officers Association (POA)"),
            ("https://www.thepfa.com/news", "Professional Footballers' Association (PFA)"),
            ("https://prospect.org.uk/news", "Prospect"),
            ("https://www.pcs.org.uk/news", "Public and Commercial Services Union (PCS)"),
            ("https://www.rcm.org.uk/news-views", "Royal College of Midwives (RCM)"),
            ("https://www.rcn.org.uk/news", "Royal College of Nursing (RCN)"),
            ("https://rcpod.org.uk/news", "Royal College of Podiatry (RCPod)"),
            ("https://www.sor.org/news", "Society of Radiographers (SoR)"),
            ("https://www.tuc.org.uk/news", "Trades Union Congress (TUC)"),
            ("https://www.tssa.org.uk/news", "Transport Salaried Staffs' Association (TSSA)"),
            ("https://www.athrawon.com/news", "Undeb Cenedlaethol Athrawon Cymru (UCAC)"),
            ("https://www.usdaw.org.uk/news", "Union of Shop, Distributive and Allied Workers (USDAW)"),
            ("https://www.unison.org.uk/news", "Unison"),
            ("https://www.unitetheunion.org/news", "Unite the Union"),
            ("https://www.urtu.com/news", "United Road Transport Union (URTU)"),
            ("https://www.uvwunion.org.uk/news", "United Voices of the World (UVW)"),
            ("https://www.ucu.org.uk/news", "University and College Union (UCU)"),
            ("https://writersguild.org.uk/news", "Writers' Guild of Great Britain (WGGB)"),
        ]

        with SessionLocal() as db:
            count = 0
            for url, org in initial_sources:
                existing = db.query(ScrapeSourceDB).filter(ScrapeSourceDB.url == url).first()
                if not existing:
                    # check if url provided started with www or not to prevent duplicates if only schema differs
                    # Simple check - if we have exact match skip.
                    # As user requested, we just add them.
                    db.add(ScrapeSourceDB(url=url, organization_name=org))
                    count += 1
            
            if count > 0:
                print(f"Seeding {count} new scrape sources...")
                db.commit()
            else:
                print("All scrape sources already exist.")

    except Exception as e:
        print(f"Error seeding scrape sources: {e}")
