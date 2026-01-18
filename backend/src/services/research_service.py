"""
Service for handling deep research operations using OpenAI.
"""
import json
import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.config import client
from src.models import SearchRequestDB, UnionWinDB


def create_research_input(date_range: str) -> str:
    """
    Create the research input prompt for OpenAI Deep Research.

    Args:
        date_range: String representing the date range to search

    Returns:
        Formatted research prompt
    """
    return f"""Research and find as many recent trade union victories as you can, successful union organizing campaigns, and labour movement wins from {date_range} in the United Kingdom.

Here is a list of major UK trade unions to consider, it is not exhaustive but should help guide your research:
- Accord
- Advance
- Aegis the Union
- Artists' Union England (AUE)
- ASLEF (Associated Society of Locomotive Engineers and Firemen)
- Association of Educational Psychologists (AEP)
- Association of Flight Attendants (AFA)
- BFAWU (Bakers, Food and Allied Workers Union)
- BALPA (British Airline Pilots' Association)
- British Dietetic Association (BDA)
- British Orthoptic Society Trade Union (BOSTU)
- CSP (Chartered Society of Physiotherapy)
- CWU (Communication Workers Union)
- EIS (Educational Institute of Scotland) 
- Equity
- FDA
- FBU (Fire Brigades Union)
- GMB
- HCSA (Hospital Consultants and Specialists Association)
- MU (Musicians' Union)
- NAPO (National Association of Probation Officers)
- NAHT (National Association of Head Teachers)
- NARS (National Association of Racing Staff)
- NASUWT (National Association of Schoolmasters Union of Women Teachers)
- NEU (National Education Union)
- NUJ (National Union of Journalists)
- NUM (National Union of Mineworkers)
- NGSU (Nationwide Group Staff Union)
- Nautilus UK
- POA (Prison Officers Association), 
- PFA (Professional Footballers' Association)
- Prospect
- PCS (Public and Commercial Services Union)
- RMT (National Union of Rail, Maritime and Transport Workers)
- RCM (Royal College of Midwives)
- RCPod (Royal College of Podiatry)
- SoR (Society of Radiographers)
- TSSA (Transport Salaried Staffs' Association)
- UCAC (Undeb Cenedlaethol Athrawon Cymru)
- USDAW (Union of Shop, Distributive and Allied Workers)
- Unison
- Unite the Union
- URTU (United Road Transport Union)
- UCU (University and College Union)
- WGGB (Writers' Guild of Great Britain)
- TUC (Trades Union Congress)

Do:
- Find specific, verified trade union victories and labour movement wins
- Include exact dates, specific figures, and measurable outcomes where available
- Identify the specific union or labour organization involved in each victory
- Choose an appropriate emoji that represents the industry, sector, or type of victory (e.g., 🏥 for healthcare, 🚌 for transport, 📚 for education etc)
- Prioritize reliable, up-to-date sources: official union websites, reputable news outlets (BBC, The Guardian, Reuters), government announcements
- For each victory, provide: a clear descriptive title, union name, representative emoji, exact date (YYYY-MM-DD format), credible source URL, and a 2-3 sentence summary
- Include inline citations for each win
- Only include actual verified wins, not speculation or ongoing negotiations

CRITICAL: Format your response as a valid JSON array. Each win must be a JSON object with these exact fields:
- title: string (clear, descriptive title)
- union_name: string (name of the union or labour organization, e.g., "Unite", "GMB", "Unison", "TUC", etc)
- emoji: string (single emoji character that represents the win, e.g., "🏥", "🚌", "📚", "✊")
- date: string (YYYY-MM-DD format)
- url: string (credible source URL)
- summary: string (3-5 sentence summary)

Example format:
[
  {
        "title": "Example Union Victory",
    "union_name": "Unite the Union",
    "emoji": "🏥",
    "date": "2026-01-10",
    "url": "https://example.com/article",
    "summary": "A brief summary of the victory."
  },
  {...}
]

Return ONLY the JSON array, no additional text before or after."""


def create_background_task(research_input: str) -> str:
    """
    Create a background research task with OpenAI.

    Args:
        research_input: The research prompt

    Returns:
        Response ID for polling
    """
    response = client.responses.create(
        model="gpt-5-mini",
        input=research_input,
        background=True,
        tools=[{"type": "web_search"}],
        reasoning={"effort": "high"}
    )
    return response.id


def poll_task_status(response_id: str) -> tuple[str, str | None]:
    """
    Poll the status of a background research task.

    Args:
        response_id: The OpenAI response ID

    Returns:
        Tuple of (status, output_text or None)
    """
    response = client.responses.retrieve(response_id)
    output_text = response.output_text if response.status == "completed" else None
    return response.status, output_text


def extract_json_from_response(output_text: str) -> list[dict]:
    """
    Extract JSON array from OpenAI response text.
    If JSON is malformed, uses GPT-4o to fix it.

    Args:
        output_text: Raw response text from OpenAI

    Returns:
        List of win dictionaries

    Raises:
        json.JSONDecodeError: If JSON parsing fails even after GPT fix attempt
    """
    json_text = output_text.strip()

    # Try to extract JSON from code blocks
    json_match = re.search(
        r'```(?:json)?\s*(\[.*?\])\s*```', json_text, re.DOTALL
    )
    if json_match:
        json_text = json_match.group(1)
    elif not json_text.startswith('['):
        # Try to find JSON array anywhere in text
        json_match = re.search(r'\[.*\]', json_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"⚠️  Malformed JSON detected: {str(e)}")
        print(f"📝 Attempting to fix JSON with GPT-5.2...")

        # Use GPT-5.2 to fix the malformed JSON
        try:
            fixed_json = fix_malformed_json(json_text)
            return json.loads(fixed_json)
        except Exception as fix_error:
            print(f"❌ Failed to fix JSON: {str(fix_error)}")
            raise e  # Re-raise the original error


def fix_malformed_json(malformed_json: str) -> str:
    """
    Use GPT-5.2 to fix malformed JSON.

    Args:
        malformed_json: The malformed JSON string

    Returns:
        Fixed JSON string

    Raises:
        Exception: If GPT fails to fix the JSON
    """
    prompt = f"""Fix the following malformed JSON and return ONLY the corrected JSON array, with no additional text or explanation.

The JSON should be an array of objects with these fields:
- title: string
- union_name: string or null
- emoji: string (single emoji)
- date: string (YYYY-MM-DD format)
- url: string
- summary: string

Malformed JSON:
{malformed_json}

Return ONLY the corrected JSON array:"""

    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=[
            {
                "role": "system",
                "content": "You are a JSON repair expert. Fix malformed JSON and return only valid JSON, no explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    fixed_text = response.choices[0].message.content.strip()

    # Remove markdown code blocks if present
    fixed_text = re.sub(r'```(?:json)?\s*', '', fixed_text)
    fixed_text = re.sub(r'\s*```', '', fixed_text)

    print(f"✅ JSON fixed successfully")
    return fixed_text.strip()


def validate_win_data(win_data: dict) -> bool:
    """
    Validate that win data has all required fields.

    Args:
        win_data: Dictionary containing win information

    Returns:
        True if valid, False otherwise
    """
    required_fields = ['title', 'date', 'url', 'summary']
    return all(key in win_data for key in required_fields)


def check_duplicate_win(db: Session, url: str) -> bool:
    """
    Check if a win with the given URL already exists.

    Args:
        db: Database session
        url: URL to check

    Returns:
        True if duplicate exists, False otherwise
    """
    existing = db.query(UnionWinDB).filter(UnionWinDB.url == url).first()
    return existing is not None


def create_win_from_data(win_data: dict) -> UnionWinDB:
    """
    Create a UnionWinDB instance from win data dictionary.

    Args:
        win_data: Dictionary containing win information

    Returns:
        UnionWinDB instance
    """
    return UnionWinDB(
        title=win_data['title'],
        union_name=win_data.get('union_name'),
        emoji=win_data.get('emoji', '✊'),
        date=win_data['date'],
        url=win_data['url'],
        summary=win_data['summary']
    )


def save_wins_to_db(db: Session, wins_data: list[dict]) -> int:
    """
    Save extracted wins to the database, avoiding duplicates.

    Args:
        db: Database session
        wins_data: List of win dictionaries

    Returns:
        Number of new wins added
    """
    new_wins_count = 0

    for win_data in wins_data:
        if not validate_win_data(win_data):
            continue

        if check_duplicate_win(db, win_data['url']):
            print(f"⏭️  Skipped duplicate: {win_data['title']}")
            continue

        new_win = create_win_from_data(win_data)
        db.add(new_win)

        # Commit each win individually to prevent one duplicate from blocking all wins
        try:
            db.commit()
            new_wins_count += 1
            print(
                f"➕ Added: {win_data.get('emoji', '✊')} {win_data['title']} "
                f"({win_data.get('union_name', 'N/A')})"
            )
        except IntegrityError as e:
            # Rollback the session if a duplicate is encountered
            db.rollback()
            print(
                f"⏭️  Skipped duplicate (database constraint): {win_data['title']}")
            print(f"   Error: {str(e)}")

    return new_wins_count


def process_research_results(db: Session, output_text: str) -> int:
    """
    Process research results and save to database.

    Args:
        db: Database session
        output_text: Raw output from OpenAI research

    Returns:
        Number of new wins found

    Raises:
        Exception: If processing fails
    """
    wins_data = extract_json_from_response(output_text)
    print(f"📊 Parsing {len(wins_data)} wins")
    return save_wins_to_db(db, wins_data)


def update_request_status(
    db: Session,
    request: SearchRequestDB,
    status: str,
    new_wins_found: int = 0,
    error_message: str | None = None
) -> None:
    """
    Update the status of a search request.

    Args:
        db: Database session
        request: SearchRequestDB instance to update
        status: New status value
        new_wins_found: Number of new wins found
        error_message: Optional error message
    """
    request.status = status
    request.new_wins_found = new_wins_found
    if error_message:
        request.error_message = error_message
    db.commit()
