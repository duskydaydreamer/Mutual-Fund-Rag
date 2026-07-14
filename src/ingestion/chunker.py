"""
Semantic section-based chunker for Groww mutual fund pages.

Instead of naive character splitting, this module:
1. Strips header/navigation noise and footer/SEO noise
2. Splits the remaining text into semantic sections using keyword anchors
3. Attaches enriched metadata (including chunk_type) to each chunk
4. Falls back to RecursiveCharacterTextSplitter for oversized sections
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Maximum chunk size before we apply the fallback splitter
MAX_CHUNK_CHARS = 1500

# Fallback splitter for oversized sections
FALLBACK_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=75,
    separators=["\n\n", "\n", ". ", " "],
    length_function=len,
)

# Ordered list of (section_name, start_anchor_regex, end_anchor_regex)
# Each section spans from its start anchor to the next section's start anchor.
SECTION_ANCHORS = [
    ("overview",          r"(?:Equity|Hybrid|Debt|Commodity)\s+(?:Mid Cap|Small Cap|Large Cap|Flexi Cap|ELSS|Multi Asset|Index|ETF|Liquid|Conservative Hybrid|Large & Mid Cap|Focused|Multicap|Defence|Nifty 50|Silver|Gold)",  None),
    ("returns",           r"Return calculator",         None),
    ("holdings",          r"Holdings\s*\(",              None),
    ("investments",       r"Minimum investments",        None),
    ("returns_rankings",  r"Returns and rankings",       None),
    ("exit_load_tax",     r"Exit Load|Exit load",        None),
    ("comparison",        r"Compare similar funds",      None),
    ("fund_manager",      r"Fund management",            None),
    ("about",             r"About\s+\w+",                None),  # "About HDFC Mid Cap..." etc.
    ("scheme_info",       r"Fund house\s+\w+",           None),
]

# Footer anchors — everything after this is noise
FOOTER_ANCHORS = [
    "Contact Us Download the App",
    "GROWW About Us Pricing",
    "Contact Us",
]

# Nav anchors — common header/nav text that precedes the real content
NAV_END_ANCHOR = "Brokerage and charges on Groww Blog"


def _find_position(text: str, pattern: str) -> int:
    """Find position of a regex pattern in text. Returns -1 if not found."""
    match = re.search(pattern, text)
    return match.start() if match else -1


def strip_noise(text: str, scheme_name: str) -> str:
    """Remove header navigation and footer SEO blocks."""
    # --- Strip header/nav ---
    # Try to find the end of the navigation block
    nav_end = text.find(NAV_END_ANCHOR)
    if nav_end >= 0:
        # Move past the anchor itself
        text = text[nav_end + len(NAV_END_ANCHOR):]
    else:
        # Fallback: find second occurrence of scheme name (first is in page title within nav)
        first = text.find(scheme_name)
        if first >= 0:
            second = text.find(scheme_name, first + len(scheme_name))
            if second >= 0:
                text = text[second:]
            else:
                text = text[first:]

    # --- Strip footer ---
    for anchor in FOOTER_ANCHORS:
        pos = text.find(anchor)
        if pos >= 0:
            text = text[:pos]
            break

    return text.strip()


def extract_section(text: str, start_pattern: str, end_pattern: Optional[str]) -> tuple:
    """
    Extract a section of text between start_pattern and end_pattern.
    Returns (section_text, start_pos, end_pos).
    If not found, returns ("", -1, -1).
    """
    start_match = re.search(start_pattern, text)
    if not start_match:
        return ("", -1, -1)

    start_pos = start_match.start()

    if end_pattern:
        end_match = re.search(end_pattern, text[start_pos + 1:])
        if end_match:
            end_pos = start_pos + 1 + end_match.start()
        else:
            end_pos = len(text)
    else:
        end_pos = len(text)

    return (text[start_pos:end_pos], start_pos, end_pos)


def truncate_holdings(holdings_text: str, max_holdings: int = 15) -> str:
    """
    Truncate the holdings section to keep only the top N holdings.
    Preserves the header and adds a note about truncation.
    """
    # Try to find the holdings count, e.g., "Holdings ( 78 )"
    count_match = re.search(r'Holdings\s*\(\s*(\d+)\s*\)', holdings_text)
    total_count = int(count_match.group(1)) if count_match else None

    # Holdings are listed as: "Name Sector Instruments Assets <pct>%"
    # Split by percentage pattern to count entries
    entries = re.split(r'(\d+\.\d+%)', holdings_text)

    if len(entries) > max_holdings * 2:
        # Keep header + first max_holdings entries (each entry is text + percentage)
        truncated = ''.join(entries[:max_holdings * 2 + 1])
        note = f" [Showing top {max_holdings} of {total_count or 'many'} holdings]"
        return truncated.strip() + note

    return holdings_text


def split_into_semantic_sections(text: str, scheme_name: str) -> list[tuple[str, str]]:
    """
    Split text into semantic sections using ordered keyword anchors.
    Returns a list of (chunk_type, section_text) tuples.
    """
    sections = []

    # Find positions of all section anchors
    anchor_positions = []
    for section_name, start_pattern, _ in SECTION_ANCHORS:
        pos = _find_position(text, start_pattern)
        if pos >= 0:
            anchor_positions.append((pos, section_name, start_pattern))

    # Sort by position
    anchor_positions.sort(key=lambda x: x[0])

    # Extract text between consecutive anchors
    for i, (pos, section_name, _) in enumerate(anchor_positions):
        if i + 1 < len(anchor_positions):
            end_pos = anchor_positions[i + 1][0]
        else:
            end_pos = len(text)

        section_text = text[pos:end_pos].strip()

        if not section_text:
            continue

        # Special handling: truncate holdings
        if section_name == "holdings":
            section_text = truncate_holdings(section_text)

        sections.append((section_name, section_text))

    # If no sections were found, treat entire text as general
    if not sections and text.strip():
        sections.append(("general", text.strip()))

    return sections


def chunk_document(cleaned_doc: dict) -> list[Document]:
    """
    Chunks a cleaned document into LangChain Document objects using
    semantic section splitting.
    """
    scheme_name = cleaned_doc.get("scheme_name", "Unknown")
    slug = scheme_name.lower().replace(" ", "-").replace("'", "")

    # Base metadata for all chunks
    base_metadata = {
        "source_url": cleaned_doc.get("source_url", ""),
        "scheme_name": scheme_name,
        "amc": cleaned_doc.get("amc", ""),
        "category": cleaned_doc.get("category", ""),
        "scrape_date": cleaned_doc.get("scrape_date", ""),
    }

    chunks = []
    full_text = cleaned_doc.get("full_page_text", "")

    if not full_text:
        logger.warning(f"No full_page_text for {scheme_name}, skipping.")
        return chunks

    # Step 1: Strip noise
    clean_text = strip_noise(full_text, scheme_name)
    logger.info(f"{scheme_name}: stripped noise — {len(full_text)} -> {len(clean_text)} chars ({100 - len(clean_text)*100//len(full_text)}% removed)")

    # Step 2: Split into semantic sections
    sections = split_into_semantic_sections(clean_text, scheme_name)

    for section_name, section_text in sections:
        if len(section_text) < 20:
            continue  # Skip trivially small sections

        meta = base_metadata.copy()
        meta["chunk_type"] = section_name
        meta["chunk_id"] = f"{slug}_{section_name}"

        # Step 3: If section is too large, use fallback splitter
        if len(section_text) > MAX_CHUNK_CHARS:
            sub_chunks = FALLBACK_SPLITTER.split_text(section_text)
            for j, sub_text in enumerate(sub_chunks):
                sub_meta = meta.copy()
                sub_meta["chunk_id"] = f"{slug}_{section_name}_{j}"
                chunks.append(Document(page_content=sub_text, metadata=sub_meta))
        else:
            chunks.append(Document(page_content=section_text, metadata=meta))

    logger.info(f"{scheme_name}: generated {len(chunks)} chunks")
    return chunks


def chunk_all_documents() -> list[Document]:
    """Reads all processed JSON files and generates chunks."""
    processed_dir = Path("data/processed")
    all_chunks = []

    logger.info("Starting semantic document chunking (Phase 3.2)...")

    processed_files = list(processed_dir.glob("*.json"))
    if not processed_files:
        logger.warning(f"No JSON files found in {processed_dir}. Run cleaner first.")
        return all_chunks

    for processed_file in sorted(processed_files):
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                doc = json.load(f)

            chunks = chunk_document(doc)
            all_chunks.extend(chunks)

        except Exception as e:
            logger.error(f"Failed to chunk {processed_file.name}: {e}")

    logger.info(f"✅ Chunking complete. Total chunks: {len(all_chunks)}")

    # Print chunk type distribution
    type_counts = {}
    for c in all_chunks:
        ct = c.metadata.get("chunk_type", "unknown")
        type_counts[ct] = type_counts.get(ct, 0) + 1
    logger.info(f"Chunk type distribution: {type_counts}")

    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_documents()
    print(f"\nTotal chunks: {len(chunks)}")
    print("\nSample chunks:")
    for c in chunks[:3]:
        print(f"\n--- [{c.metadata['chunk_type']}] {c.metadata['scheme_name']} ---")
        print(c.page_content[:200] + "...")
